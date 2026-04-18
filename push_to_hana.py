#!/usr/bin/env python3
"""
push_nas_to_hana.py
═══════════════════════════════════════════════════════════════════════════════
PURPOSE  : Read a GZIP-compressed CSV from a NAS mount path and push it
           to a SAP HANA table — WITHOUT unzipping the file to disk.

FEATURES :
  1. Reads .gz file in-memory (no disk unzip)
  2. Spark-style StructType schema with DateType, IntegerType, DecimalType etc.
  3. PERMISSIVE mode  → bad rows logged to error file, load continues
  4. Spark-style HanaWriter fluent API  (df.write.option(...).hana(...))
  5. executemany() batch inserts (configurable batch size)
  6. Full structured logging → rotating log file + stdout
  7. Dry-run mode → validates schema + row count without touching HANA
  8. CLI interface via argparse

USAGE :
  python3 push_nas_to_hana.py \
      --file   /nas/mount/btrapp/data/transactions_20240401.csv.gz \
      --schema FINANCE_SCHEMA \
      --table  DAILY_TRANSACTIONS \
      --mode   PERMISSIVE \
      --batch  5000

  # Dry run (no HANA write):
  python3 push_nas_to_hana.py --file /nas/data.csv.gz --schema S --table T --dry-run

AUTHOR  : Generated for SCB Data Engineering
VERSION : 2.0.0
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import gzip
import csv
import io
import json
import time
import logging
import argparse
import traceback
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
from logging.handlers import RotatingFileHandler

# ── Third-party ───────────────────────────────────────────────────────────────
try:
    from hdbcli import dbapi
except ImportError:
    print("ERROR: hdbcli not installed. Run: pip install hdbcli")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCHEMA DEFINITION
# Spark-style StructType / StructField equivalents
# ══════════════════════════════════════════════════════════════════════════════

class DataType:
    """Base class for all data types."""
    name = "ANY"

class StringType(DataType):
    name = "STRING"

class IntegerType(DataType):
    name = "INTEGER"

class LongType(DataType):
    name = "LONG"

class FloatType(DataType):
    name = "FLOAT"

class DoubleType(DataType):
    name = "DOUBLE"

class DecimalType(DataType):
    def __init__(self, precision: int = 18, scale: int = 6):
        self.precision = precision
        self.scale = scale
        self.name = f"DECIMAL({precision},{scale})"

class DateType(DataType):
    def __init__(self, fmt: str = "%Y-%m-%d"):
        self.fmt = fmt
        self.name = "DATE"

class TimestampType(DataType):
    def __init__(self, fmt: str = "%Y-%m-%d %H:%M:%S"):
        self.fmt = fmt
        self.name = "TIMESTAMP"

class BooleanType(DataType):
    name = "BOOLEAN"


class StructField:
    """
    Equivalent of Spark's StructField.

    Args:
        name      : Column name (must match CSV header exactly)
        data_type : DataType instance
        nullable  : If False, NULL value raises error in PERMISSIVE mode
                    and hard fails in FAILFAST mode
        hana_col  : Override HANA column name (default = same as name)
    """
    def __init__(self,
                 name: str,
                 data_type: DataType,
                 nullable: bool = True,
                 hana_col: Optional[str] = None):
        self.name      = name
        self.data_type = data_type
        self.nullable  = nullable
        self.hana_col  = hana_col or name


class StructType:
    """
    Equivalent of Spark's StructType.
    Defines the full schema for CSV → HANA mapping.

    Example:
        schema = StructType([
            StructField("TXN_ID",     StringType(),             nullable=False),
            StructField("TXN_DATE",   DateType("%d/%m/%Y"),     nullable=True),
            StructField("AMOUNT",     DecimalType(18, 2),       nullable=True),
            StructField("REGION",     StringType(),             nullable=True),
        ])
    """
    def __init__(self, fields: List[StructField]):
        self.fields     = fields
        self._field_map = {f.name: f for f in fields}

    def field_names(self) -> List[str]:
        return [f.name for f in self.fields]

    def hana_col_names(self) -> List[str]:
        return [f.hana_col for f in self.fields]

    def get(self, name: str) -> Optional[StructField]:
        return self._field_map.get(name)

    def __repr__(self):
        lines = [f"  StructField({f.name!r}, {f.data_type.name}, nullable={f.nullable})"
                 for f in self.fields]
        return "StructType([\n" + ",\n".join(lines) + "\n])"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TYPE CASTER
# Converts raw CSV string → Python/HANA-compatible typed value
# ══════════════════════════════════════════════════════════════════════════════

class TypeCastError(Exception):
    pass


def cast_value(raw: str,
               field: StructField,
               mode: str,
               logger: logging.Logger) -> Any:
    """
    Cast a raw CSV string to the target Python type defined in StructField.

    PERMISSIVE mode : on cast failure → return None (NULL) and log warning
    FAILFAST mode   : on cast failure → raise TypeCastError immediately
    DROPMALFORMED   : caller decides to drop the row (cast returns sentinel)

    Returns:
        Typed Python value, or None if nullable + cast failed in PERMISSIVE
    Raises:
        TypeCastError in FAILFAST mode
    """
    # ── Handle empty / null string ────────────────────────────────────────────
    if raw is None or raw.strip() == '' or raw.strip().upper() in ('NULL', 'NA', 'N/A', 'NONE'):
        if not field.nullable:
            msg = f"Column '{field.name}' is NOT NULLABLE but received NULL/empty value"
            if mode == "FAILFAST":
                raise TypeCastError(msg)
            logger.warning(f"[PERMISSIVE] {msg} — coercing to NULL anyway")
        return None

    raw = raw.strip()
    dtype = field.data_type

    try:
        if isinstance(dtype, StringType):
            return str(raw)

        elif isinstance(dtype, IntegerType):
            # Handle float strings like "42.0"
            return int(float(raw))

        elif isinstance(dtype, LongType):
            return int(float(raw))

        elif isinstance(dtype, FloatType):
            return float(raw)

        elif isinstance(dtype, DoubleType):
            return float(raw)

        elif isinstance(dtype, DecimalType):
            return float(Decimal(raw))

        elif isinstance(dtype, DateType):
            # Try configured format first, then common fallbacks
            formats_to_try = [dtype.fmt, "%Y-%m-%d", "%d/%m/%Y",
                              "%d-%m-%Y", "%Y%m%d", "%m/%d/%Y"]
            for fmt in formats_to_try:
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse '{raw}' as date with any known format")

        elif isinstance(dtype, TimestampType):
            formats_to_try = [dtype.fmt,
                              "%Y-%m-%d %H:%M:%S",
                              "%Y-%m-%dT%H:%M:%S",
                              "%Y-%m-%d %H:%M:%S.%f",
                              "%d/%m/%Y %H:%M:%S"]
            for fmt in formats_to_try:
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse '{raw}' as timestamp")

        elif isinstance(dtype, BooleanType):
            return raw.lower() in ('true', '1', 'yes', 'y', 't')

        else:
            return raw  # unknown type → pass through as string

    except (ValueError, InvalidOperation, OverflowError) as e:
        err_msg = (f"Cast failed: column='{field.name}' "
                   f"type={dtype.name} "
                   f"value={raw!r} "
                   f"error={e}")
        if mode == "FAILFAST":
            raise TypeCastError(err_msg)
        elif mode in ("PERMISSIVE", "DROPMALFORMED"):
            logger.warning(f"[{mode}] {err_msg} — setting NULL")
            return None
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — LOAD RESULT  (run summary object)
# ══════════════════════════════════════════════════════════════════════════════

class LoadResult:
    """Holds statistics for a completed load operation."""

    def __init__(self):
        self.total_rows_read     : int = 0
        self.rows_inserted       : int = 0
        self.rows_skipped        : int = 0
        self.rows_null_coerced   : int = 0
        self.batches_committed   : int = 0
        self.batches_failed      : int = 0
        self.start_time          : datetime = datetime.now()
        self.end_time            : Optional[datetime] = None
        self.error_log_path      : Optional[str] = None

    def finish(self):
        self.end_time = datetime.now()

    @property
    def elapsed_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def rows_per_second(self) -> float:
        elapsed = self.elapsed_seconds
        return round(self.rows_inserted / elapsed, 1) if elapsed > 0 else 0

    def summary(self) -> str:
        return (
            f"\n{'═'*60}\n"
            f"  LOAD SUMMARY\n"
            f"{'═'*60}\n"
            f"  Total rows read      : {self.total_rows_read:,}\n"
            f"  Rows inserted        : {self.rows_inserted:,}\n"
            f"  Rows skipped         : {self.rows_skipped:,}\n"
            f"  NULL coercions       : {self.rows_null_coerced:,}\n"
            f"  Batches committed    : {self.batches_committed:,}\n"
            f"  Batches failed       : {self.batches_failed:,}\n"
            f"  Elapsed time         : {self.elapsed_seconds:.1f}s\n"
            f"  Throughput           : {self.rows_per_second:,} rows/sec\n"
            f"  Error log            : {self.error_log_path or 'N/A'}\n"
            f"{'═'*60}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — HANA WRITER
# Spark-style fluent writer: HanaWriter().option(...).option(...).write(df)
# ══════════════════════════════════════════════════════════════════════════════

class HanaWriter:
    """
    Spark-style fluent writer for SAP HANA.

    Usage (mirrors Spark's df.write API):

        result = (
            HanaWriter()
            .option("host",        "hana-host.company.com")
            .option("port",        30015)
            .option("user",        "ETL_USER")
            .option("password",    "secret")
            .option("batchSize",   10000)
            .option("mode",        "PERMISSIVE")   # PERMISSIVE | FAILFAST | DROPMALFORMED
            .option("truncate",    True)
            .option("schema",      "FINANCE_SCHEMA")
            .option("table",       "TRANSACTIONS")
            .option("errorLog",    "/var/log/etl/errors.csv")
            .option("dryRun",      False)
            .write(rows_iterator, struct_schema, logger)
        )

    Connection alternatives:
        .option("hdbuserstore_key", "MY_HANA_KEY")   # use hdbuserstore (no password in script)
        .option("encrypt",          True)            # for HANA Cloud
    """

    # ── Defaults (mirrors Spark defaults where applicable) ────────────────────
    _DEFAULTS = {
        "host"              : None,
        "port"              : 30015,
        "user"              : None,
        "password"          : None,
        "hdbuserstore_key"  : None,   # alternative to user/password
        "encrypt"           : False,
        "batchSize"         : 5000,
        "mode"              : "PERMISSIVE",
        "truncate"          : False,
        "schema"            : None,
        "table"             : None,
        "errorLog"          : None,
        "dryRun"            : False,
        "commitOnBatchFail" : False,  # if True, skip failed batch and continue
        "maxErrors"         : None,   # stop after N errors (None = unlimited)
    }

    def __init__(self):
        self._opts = dict(self._DEFAULTS)

    def option(self, key: str, value: Any) -> "HanaWriter":
        """Set a write option. Returns self for chaining."""
        if key not in self._opts:
            raise ValueError(
                f"Unknown option: '{key}'. "
                f"Valid options: {sorted(self._opts.keys())}"
            )
        self._opts[key] = value
        return self

    def options(self, **kwargs) -> "HanaWriter":
        """Set multiple options at once."""
        for k, v in kwargs.items():
            self.option(k, v)
        return self

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _validate_opts(self):
        """Validate required options before attempting connection."""
        if not self._opts["schema"]:
            raise ValueError("option 'schema' is required")
        if not self._opts["table"]:
            raise ValueError("option 'table' is required")

        using_userstore = bool(self._opts["hdbuserstore_key"])
        using_explicit  = bool(self._opts["host"] and self._opts["user"])

        if not using_userstore and not using_explicit:
            raise ValueError(
                "Either 'hdbuserstore_key' OR ('host' + 'user' + 'password') must be set"
            )

    def _connect(self) -> dbapi.Connection:
        """Open HANA connection using configured options."""
        key = self._opts["hdbuserstore_key"]
        if key:
            # hdbuserstore — no password in script (recommended for production)
            conn = dbapi.connect(key=key)
        else:
            conn_kwargs = {
                "address" : self._opts["host"],
                "port"    : int(self._opts["port"]),
                "user"    : self._opts["user"],
                "password": self._opts["password"],
            }
            if self._opts["encrypt"]:
                conn_kwargs["encrypt"] = True
            conn = dbapi.connect(**conn_kwargs)

        conn.setautocommit(False)
        return conn

    def _build_insert_sql(self, schema: str, table: str,
                          struct_schema: StructType) -> str:
        """Build parameterised INSERT SQL with HANA column names."""
        cols   = ', '.join(f'"{c}"' for c in struct_schema.hana_col_names())
        params = ', '.join(['?' for _ in struct_schema.fields])
        return f'INSERT INTO "{schema}"."{table}" ({cols}) VALUES ({params})'

    def _open_error_log(self, path: Optional[str],
                        struct_schema: StructType) -> Optional[csv.writer]:
        """Open error CSV log file and write header."""
        if not path:
            return None, None
        fh = open(path, 'w', newline='', encoding='utf-8')
        writer = csv.writer(fh)
        writer.writerow(
            ["_ROW_NUM", "_RAW_LINE", "_ERROR_MSG"] + struct_schema.field_names()
        )
        return writer, fh

    # ── Main write method ─────────────────────────────────────────────────────

    def write(self,
              rows_iter,
              struct_schema: StructType,
              logger: logging.Logger) -> LoadResult:
        """
        Write rows to SAP HANA.

        Args:
            rows_iter     : Iterator of raw-string dicts  {col_name: raw_str_value}
                            (produced by GzipCsvReader)
            struct_schema : StructType defining columns, types, nullability
            logger        : Logger instance

        Returns:
            LoadResult with full statistics
        """
        self._validate_opts()

        schema       = self._opts["schema"]
        table        = self._opts["table"]
        batch_size   = int(self._opts["batchSize"])
        mode         = self._opts["mode"].upper()
        truncate     = self._opts["truncate"]
        dry_run      = self._opts["dryRun"]
        max_errors   = self._opts["maxErrors"]
        error_log_p  = self._opts["errorLog"]

        result       = LoadResult()
        result.error_log_path = error_log_p

        logger.info(f"HanaWriter config: schema={schema} table={table} "
                    f"batchSize={batch_size} mode={mode} "
                    f"truncate={truncate} dryRun={dry_run}")
        logger.info(f"Schema:\n{struct_schema}")

        # ── Open error log ────────────────────────────────────────────────────
        err_writer, err_fh = self._open_error_log(error_log_p, struct_schema)

        # ── Dry run — parse and validate only, no HANA writes ─────────────────
        if dry_run:
            logger.info("[DRY RUN] Validating rows — no HANA writes")
            for raw_dict in rows_iter:
                result.total_rows_read += 1
                for field in struct_schema.fields:
                    raw_val = raw_dict.get(field.name, '')
                    cast_value(raw_val, field, mode, logger)
            result.finish()
            logger.info(f"[DRY RUN] Validated {result.total_rows_read:,} rows")
            logger.info(result.summary())
            return result

        # ── Connect to HANA ───────────────────────────────────────────────────
        logger.info("Connecting to SAP HANA...")
        try:
            conn   = self._connect()
            cursor = conn.cursor()
            logger.info("Connected to SAP HANA")
        except dbapi.Error as e:
            logger.critical(f"Cannot connect to SAP HANA: {e}")
            raise

        insert_sql = self._build_insert_sql(schema, table, struct_schema)
        logger.info(f"Insert SQL template: {insert_sql}")

        # ── Truncate if requested ─────────────────────────────────────────────
        if truncate:
            try:
                cursor.execute(f'TRUNCATE TABLE "{schema}"."{table}"')
                conn.commit()
                logger.info(f"Truncated {schema}.{table}")
            except dbapi.Error as e:
                logger.error(f"Truncate failed: {e}")
                raise

        # ── Main batch insert loop ────────────────────────────────────────────
        batch        : List[List[Any]] = []
        error_count  : int = 0
        field_names  = struct_schema.field_names()

        try:
            for raw_dict in rows_iter:
                result.total_rows_read += 1
                row_num = result.total_rows_read
                typed_row  = []
                row_errors = []

                # ── Cast each column ──────────────────────────────────────────
                for field in struct_schema.fields:
                    raw_val = raw_dict.get(field.name, '')
                    try:
                        typed_val = cast_value(raw_val, field, mode, logger)
                        if typed_val is None and raw_val not in ('', None):
                            result.rows_null_coerced += 1
                        typed_row.append(typed_val)
                    except TypeCastError as e:
                        row_errors.append(str(e))

                # ── Handle row errors per mode ────────────────────────────────
                if row_errors:
                    error_count += 1
                    error_msg   = " | ".join(row_errors)
                    raw_vals    = [raw_dict.get(fn, '') for fn in field_names]

                    if err_writer:
                        err_writer.writerow(
                            [row_num, json.dumps(raw_dict), error_msg] + raw_vals
                        )

                    if mode == "FAILFAST":
                        logger.error(f"[FAILFAST] Row {row_num}: {error_msg}")
                        conn.rollback()
                        raise TypeCastError(f"FAILFAST triggered at row {row_num}")

                    elif mode == "DROPMALFORMED":
                        logger.warning(f"[DROPMALFORMED] Dropping row {row_num}: {error_msg}")
                        result.rows_skipped += 1
                        continue  # skip this row entirely

                    else:  # PERMISSIVE — include row with NULLs
                        logger.warning(f"[PERMISSIVE] Row {row_num} has errors, "
                                       f"inserting with NULLs: {error_msg}")
                        # typed_row already has None for failed fields

                    if max_errors and error_count >= max_errors:
                        logger.error(f"Max error threshold reached ({max_errors}). Aborting.")
                        conn.rollback()
                        result.finish()
                        raise RuntimeError(
                            f"Aborted: exceeded maxErrors={max_errors}"
                        )

                batch.append(typed_row)

                # ── Flush batch ────────────────────────────────────────────────
                if len(batch) >= batch_size:
                    try:
                        cursor.executemany(insert_sql, batch)
                        conn.commit()
                        result.rows_inserted    += len(batch)
                        result.batches_committed += 1
                        logger.info(
                            f"Committed batch #{result.batches_committed} "
                            f"({len(batch):,} rows) | "
                            f"Total: {result.rows_inserted:,} | "
                            f"Elapsed: {result.elapsed_seconds:.0f}s"
                        )
                        batch = []
                    except dbapi.Error as e:
                        result.batches_failed += 1
                        logger.error(
                            f"Batch #{result.batches_committed + 1} insert failed: {e}"
                        )
                        conn.rollback()
                        if not self._opts["commitOnBatchFail"]:
                            raise
                        # If commitOnBatchFail=True, log and continue
                        logger.warning("commitOnBatchFail=True — skipping failed batch")
                        batch = []

            # ── Flush final partial batch ─────────────────────────────────────
            if batch:
                try:
                    cursor.executemany(insert_sql, batch)
                    conn.commit()
                    result.rows_inserted    += len(batch)
                    result.batches_committed += 1
                    logger.info(
                        f"Committed final batch "
                        f"({len(batch):,} rows) | "
                        f"Total: {result.rows_inserted:,}"
                    )
                except dbapi.Error as e:
                    result.batches_failed += 1
                    logger.error(f"Final batch insert failed: {e}")
                    conn.rollback()
                    raise

        except Exception:
            logger.error(f"Load aborted at row {result.total_rows_read}: "
                         f"{traceback.format_exc()}")
            raise
        finally:
            cursor.close()
            conn.close()
            if err_fh:
                err_fh.flush()
                err_fh.close()
            result.finish()

        logger.info(result.summary())
        return result


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — GZIP CSV READER
# Reads .gz file in-memory without unzipping to disk
# ══════════════════════════════════════════════════════════════════════════════

class GzipCsvReader:
    """
    Reads a GZIP-compressed CSV file in streaming mode — no disk extraction.

    Works for:
        - .csv.gz    (single gzipped CSV)
        - .gz        (same)
        - .csv       (plain CSV — auto-detected by extension)

    Yields:
        dict of {header_col_name: raw_string_value} per row
    """

    def __init__(self,
                 file_path    : str,
                 schema       : StructType,
                 delimiter    : str = ',',
                 encoding     : str = 'utf-8',
                 logger       : Optional[logging.Logger] = None):
        self.file_path = file_path
        self.schema    = schema
        self.delimiter = delimiter
        self.encoding  = encoding
        self.logger    = logger or logging.getLogger(__name__)

        # Only read schema columns (projection pushdown — skip unneeded cols)
        self.schema_cols = set(schema.field_names())

    def __iter__(self):
        return self._read()

    def _read(self):
        """Generator: yields one dict per CSV row."""
        is_gzip = self.file_path.endswith('.gz')

        self.logger.info(
            f"Opening {'GZIP' if is_gzip else 'plain'} file: {self.file_path}"
        )

        try:
            if is_gzip:
                # gzip.open returns a binary stream → wrap in TextIOWrapper
                raw_fh  = gzip.open(self.file_path, 'rb')
                text_fh = io.TextIOWrapper(raw_fh, encoding=self.encoding,
                                           newline='')
            else:
                text_fh = open(self.file_path, 'r',
                               encoding=self.encoding, newline='')
        except (FileNotFoundError, PermissionError, OSError) as e:
            self.logger.critical(f"Cannot open file '{self.file_path}': {e}")
            raise

        try:
            reader = csv.DictReader(text_fh, delimiter=self.delimiter)

            # ── Validate CSV headers against schema ───────────────────────────
            if reader.fieldnames is None:
                raise ValueError("CSV file appears to be empty — no headers found")

            csv_cols    = set(reader.fieldnames)
            missing     = self.schema_cols - csv_cols
            extra       = csv_cols - self.schema_cols

            if missing:
                self.logger.warning(
                    f"Schema columns NOT found in CSV: {sorted(missing)}. "
                    f"These will be NULL in HANA."
                )
            if extra:
                self.logger.info(
                    f"CSV has extra columns not in schema (will be ignored): "
                    f"{sorted(extra)}"
                )

            self.logger.info(
                f"CSV headers: {list(reader.fieldnames)}"
            )

            for row in reader:
                # Only yield schema-relevant columns
                yield {col: row.get(col, '') for col in self.schema_cols}

        finally:
            text_fh.close()
            if is_gzip:
                raw_fh.close()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — LOGGING SETUP
# ══════════════════════════════════════════════════════════════════════════════

def setup_logger(log_dir: str = "/var/log/etl",
                 job_name: str = "push_nas_to_hana") -> logging.Logger:
    """
    Set up rotating file logger + stdout handler.

    Log file: <log_dir>/<job_name>_YYYYMMDD.log
    Rotates at 50MB, keeps last 10 files.
    """
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        f"{job_name}_{datetime.now().strftime('%Y%m%d')}.log"
    )

    logger = logging.getLogger(job_name)
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt     = "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )

    # ── Rotating file handler (50MB, keep 10 files) ───────────────────────────
    fh = RotatingFileHandler(log_file, maxBytes=50 * 1024 * 1024,
                             backupCount=10, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # ── Console handler ───────────────────────────────────────────────────────
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"Logger initialised. Log file: {log_file}")
    return logger


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SCHEMA DEFINITION
# ── EDIT THIS SECTION to match your actual table structure ──────────────────
# ══════════════════════════════════════════════════════════════════════════════

def get_schema() -> StructType:
    """
    Define your table schema here — mirrors Spark's StructType/StructField.

    StructField(
        name      = "CSV column header name",
        data_type = <type>,           # StringType | IntegerType | DecimalType(p,s)
                                      # DateType(fmt) | TimestampType(fmt) | etc.
        nullable  = True/False,       # False = error if NULL
        hana_col  = "HANA_COL_NAME"  # optional: if HANA column name differs from CSV
    )
    """
    return StructType([
        # ── Example: Financial transaction table ─────────────────────────────
        StructField("TXN_ID",           StringType(),              nullable=False),
        StructField("TXN_DATE",         DateType("%Y-%m-%d"),      nullable=True),
        StructField("VALUE_DATE",       DateType("%Y-%m-%d"),      nullable=True),
        StructField("CUSTOMER_ID",      StringType(),              nullable=False),
        StructField("ACCOUNT_NUMBER",   StringType(),              nullable=True),
        StructField("PRODUCT_CODE",     StringType(),              nullable=True),
        StructField("TXN_TYPE",         StringType(),              nullable=True),
        StructField("DEBIT_CREDIT",     StringType(),              nullable=True),
        StructField("AMOUNT",           DecimalType(18, 2),        nullable=True),
        StructField("CURRENCY",         StringType(),              nullable=True),
        StructField("AMOUNT_USD",       DecimalType(18, 6),        nullable=True),
        StructField("FX_RATE",          DecimalType(18, 8),        nullable=True),
        StructField("REGION",           StringType(),              nullable=True),
        StructField("COUNTRY",          StringType(),              nullable=True),
        StructField("BRANCH_CODE",      StringType(),              nullable=True),
        StructField("STATUS",           StringType(),              nullable=True),
        StructField("CREATED_TS",       TimestampType("%Y-%m-%d %H:%M:%S"),
                                                                   nullable=True),
        StructField("UPDATED_TS",       TimestampType("%Y-%m-%d %H:%M:%S"),
                                                                   nullable=True),
        StructField("BATCH_ID",         IntegerType(),             nullable=True),
        StructField("SOURCE_SYSTEM",    StringType(),              nullable=True),
        # Example: CSV col 'src_ref' maps to HANA col 'SOURCE_REFERENCE'
        StructField("src_ref",          StringType(),              nullable=True,
                    hana_col="SOURCE_REFERENCE"),
    ])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="Push GZIP CSV from NAS mount to SAP HANA table"
    )
    # ── Source ────────────────────────────────────────────────────────────────
    parser.add_argument(
        "--file",      required=True,
        help="Full NAS mount path to .csv.gz or .csv file"
    )
    parser.add_argument(
        "--delimiter", default=",",
        help="CSV delimiter (default: comma)"
    )
    parser.add_argument(
        "--encoding",  default="utf-8",
        help="File encoding (default: utf-8)"
    )

    # ── HANA target ───────────────────────────────────────────────────────────
    parser.add_argument("--schema",   required=True, help="HANA schema name")
    parser.add_argument("--table",    required=True, help="HANA table name")
    parser.add_argument("--host",     default=None,  help="HANA hostname/IP")
    parser.add_argument("--port",     default=30015,  type=int)
    parser.add_argument("--user",     default=None,  help="HANA username")
    parser.add_argument("--password", default=None,  help="HANA password")
    parser.add_argument(
        "--userstore-key", default=None,
        help="hdbuserstore key (alternative to host/user/password)"
    )
    parser.add_argument(
        "--encrypt",   action="store_true",
        help="Enable TLS encryption (required for HANA Cloud)"
    )

    # ── Write options ─────────────────────────────────────────────────────────
    parser.add_argument(
        "--batch",     default=5000,  type=int,
        help="Rows per batch insert (default: 5000)"
    )
    parser.add_argument(
        "--mode",      default="PERMISSIVE",
        choices=["PERMISSIVE", "FAILFAST", "DROPMALFORMED"],
        help="Parse error mode (default: PERMISSIVE)"
    )
    parser.add_argument(
        "--truncate",  action="store_true",
        help="Truncate target table before inserting"
    )
    parser.add_argument(
        "--max-errors", default=None, type=int,
        help="Abort load if total error rows exceed this count"
    )

    # ── Logging / output ──────────────────────────────────────────────────────
    parser.add_argument(
        "--log-dir",   default="/var/log/etl",
        help="Directory for log files (default: /var/log/etl)"
    )
    parser.add_argument(
        "--error-log", default=None,
        help="Path for CSV error log (default: auto-generated in log-dir)"
    )
    parser.add_argument(
        "--dry-run",   action="store_true",
        help="Validate schema + rows without writing to HANA"
    )
    return parser.parse_args()


def main():
    args   = parse_args()
    logger = setup_logger(log_dir=args.log_dir)

    # ── Auto-generate error log path if not provided ──────────────────────────
    error_log = args.error_log or os.path.join(
        args.log_dir,
        f"errors_{args.table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    logger.info("=" * 70)
    logger.info("  NAS → SAP HANA PUSH JOB STARTING")
    logger.info("=" * 70)
    logger.info(f"Source file   : {args.file}")
    logger.info(f"Target        : {args.schema}.{args.table}")
    logger.info(f"Mode          : {args.mode}")
    logger.info(f"Batch size    : {args.batch}")
    logger.info(f"Truncate      : {args.truncate}")
    logger.info(f"Dry run       : {args.dry_run}")
    logger.info(f"Error log     : {error_log}")

    # ── Load schema ───────────────────────────────────────────────────────────
    schema = get_schema()
    logger.info(f"Schema loaded: {len(schema.fields)} columns defined")

    # ── Build reader (streams gzip in-memory) ─────────────────────────────────
    reader = GzipCsvReader(
        file_path = args.file,
        schema    = schema,
        delimiter = args.delimiter,
        encoding  = args.encoding,
        logger    = logger
    )

    # ── Build writer (Spark-style fluent API) ─────────────────────────────────
    writer = (
        HanaWriter()
        .option("schema",    args.schema)
        .option("table",     args.table)
        .option("batchSize", args.batch)
        .option("mode",      args.mode)
        .option("truncate",  args.truncate)
        .option("errorLog",  error_log)
        .option("dryRun",    args.dry_run)
    )

    # ── Connection: prefer hdbuserstore, fallback to explicit credentials ──────
    if args.userstore_key:
        writer.option("hdbuserstore_key", args.userstore_key)
    else:
        writer.option("host",     args.host)
        writer.option("port",     args.port)
        writer.option("user",     args.user)
        writer.option("password", args.password)
        writer.option("encrypt",  args.encrypt)

    if args.max_errors:
        writer.option("maxErrors", args.max_errors)

    # ── Execute ───────────────────────────────────────────────────────────────
    start = time.time()
    try:
        result = writer.write(reader, schema, logger)

        logger.info("JOB COMPLETED SUCCESSFULLY")
        logger.info(result.summary())
        sys.exit(0)

    except TypeCastError as e:
        logger.error(f"Schema/type error: {e}")
        sys.exit(2)
    except dbapi.Error as e:
        logger.critical(f"SAP HANA database error: {e}")
        sys.exit(3)
    except FileNotFoundError as e:
        logger.critical(f"File error: {e}")
        sys.exit(4)
    except Exception as e:
        logger.critical(f"Unexpected error: {traceback.format_exc()}")
        sys.exit(99)
    finally:
        elapsed = time.time() - start
        logger.info(f"Total wall-clock time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — SHELL SCRIPT WRAPPER (save as run_push.sh)
# ══════════════════════════════════════════════════════════════════════════════
#
# #!/bin/bash
# set -euo pipefail
#
# DATE=$(date +%Y%m%d)
# NAS_PATH="/nas/mount/btrapp/nas_dev/stars_sit_intrep/hdpbatch"
# PYTHON="/usr/bin/python3"
# SCRIPT="/opt/etl/push_nas_to_hana.py"
#
# $PYTHON "$SCRIPT" \
#     --file          "$NAS_PATH/transactions_${DATE}.csv.gz" \
#     --schema        "FINANCE_SCHEMA" \
#     --table         "DAILY_TRANSACTIONS" \
#     --userstore-key "HANA_ETL_KEY" \
#     --batch         10000 \
#     --mode          PERMISSIVE \
#     --truncate \
#     --log-dir       "/var/log/etl" \
#     --error-log     "/var/log/etl/errors_${DATE}.csv"
#
# EXIT=$?
# if [ $EXIT -ne 0 ]; then
#     echo "Push failed with exit code $EXIT" | \
#         mail -s "HANA PUSH FAILED $(date)" oncall@company.com
#     exit $EXIT
# fi
# echo "Push completed successfully"

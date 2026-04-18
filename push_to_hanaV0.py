#!/usr/bin/env python3
"""
push_nas_to_hana.py
Reads file from NAS mount path → pushes to SAP HANA table
Usage: python3 push_nas_to_hana.py --file /nas/mount/data.csv --table SCHEMA.MY_TABLE
"""

import sys
import csv
import logging
import argparse
from datetime import datetime
from hdbcli import dbapi

# ── Logging setup ──
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'/var/log/hana_push_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# ── HANA Connection config ──
HANA_CONFIG = {
    "address"  : "your-hana-host.company.com",  # HANA server hostname/IP
    "port"     : 30015,                           # 30013 for tenant, 30015 for single
    "user"     : "ETL_USER",
    "password" : "your_password",                # use hdbuserstore in production (see below)
    # "encrypt" : True,                           # uncomment for HANA Cloud
}

def get_connection():
    """Create and return HANA connection."""
    conn = dbapi.connect(**HANA_CONFIG)
    conn.setautocommit(False)  # manual commit for batch control
    log.info("Connected to SAP HANA successfully")
    return conn

def truncate_table(conn, schema, table):
    """Truncate target table before load."""
    cursor = conn.cursor()
    cursor.execute(f'TRUNCATE TABLE "{schema}"."{table}"')
    conn.commit()
    cursor.close()
    log.info(f"Truncated {schema}.{table}")

def push_csv_to_hana(file_path, schema, table, delimiter=',',
                      batch_size=10000, truncate_first=False):
    """
    Read CSV from NAS mount path and push to HANA table in batches.
    
    Args:
        file_path   : Full NAS mount path to CSV file  e.g. /nas/mount/data.csv
        schema      : HANA schema name
        table       : HANA table name
        delimiter   : CSV delimiter (default comma)
        batch_size  : Rows per batch insert (10000 is sweet spot)
        truncate_first: Whether to truncate table before inserting
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if truncate_first:
            truncate_table(conn, schema, table)

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            headers = next(reader)  # first row = column names
            
            # Build INSERT statement with positional placeholders
            col_list     = ', '.join(f'"{col}"' for col in headers)
            placeholders = ', '.join(['?' for _ in headers])
            insert_sql   = f'INSERT INTO "{schema}"."{table}" ({col_list}) VALUES ({placeholders})'
            
            log.info(f"Insert SQL: {insert_sql}")

            batch       = []
            total_rows  = 0
            error_rows  = 0

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 = header
                # Basic null handling: replace empty strings with None
                cleaned_row = [None if v.strip() == '' else v.strip() for v in row]
                batch.append(cleaned_row)

                if len(batch) >= batch_size:
                    try:
                        cursor.executemany(insert_sql, batch)
                        conn.commit()
                        total_rows += len(batch)
                        log.info(f"Inserted batch — total so far: {total_rows} rows")
                        batch = []
                    except Exception as e:
                        log.error(f"Batch insert failed at row ~{row_num}: {e}")
                        conn.rollback()
                        error_rows += len(batch)
                        batch = []

            # Insert remaining rows in last partial batch
            if batch:
                try:
                    cursor.executemany(insert_sql, batch)
                    conn.commit()
                    total_rows += len(batch)
                except Exception as e:
                    log.error(f"Final batch insert failed: {e}")
                    conn.rollback()
                    error_rows += len(batch)

        log.info(f"DONE. Total inserted: {total_rows} | Errors: {error_rows}")
        return total_rows, error_rows

    except FileNotFoundError:
        log.error(f"File not found: {file_path}")
        raise
    except dbapi.Error as e:
        log.error(f"HANA error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file',      required=True, help='NAS mount path to CSV file')
    parser.add_argument('--schema',    required=True, help='HANA schema name')
    parser.add_argument('--table',     required=True, help='HANA table name')
    parser.add_argument('--delimiter', default=',',   help='CSV delimiter')
    parser.add_argument('--batch',     default=10000, type=int)
    parser.add_argument('--truncate',  action='store_true', help='Truncate before insert')
    args = parser.parse_args()

    push_csv_to_hana(
        file_path      = args.file,
        schema         = args.schema,
        table          = args.table,
        delimiter      = args.delimiter,
        batch_size     = args.batch,
        truncate_first = args.truncate
    )

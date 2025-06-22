#!/bin/bash

# Configuration
HIVE_DB="your_database"               # Replace with your Hive DB name
BLOCK_SIZE_MB=128                     # HDFS block size threshold
TMP_REPORT="/tmp/hive_small_files_report.txt"
> "$TMP_REPORT"

echo "Analyzing Hive database: $HIVE_DB"
echo "Threshold: <$BLOCK_SIZE_MB MB considered as small file"

TOTAL_FILES=0
TOTAL_SMALL_FILES=0
TOTAL_WASTED_MB=0
TOTAL_USED_MB=0

# Get list of tables
tables=$(hive -S -e "SHOW TABLES IN $HIVE_DB;")

for table in $tables; do
  # Get table location
  LOCATION=$(hive -S -e "DESCRIBE FORMATTED $HIVE_DB.$table;" | awk '/Location:/ {print $NF}' | tail -1)
  if [[ -z "$LOCATION" ]]; then
    echo "Skipping $table (no location found)" >> "$TMP_REPORT"
    continue
  fi

  echo -e "\n🧾 Table: $table" >> "$TMP_REPORT"
  echo "Location: $LOCATION" >> "$TMP_REPORT"

  # Get file list and sizes
  FILES=$(hdfs dfs -ls -R "$LOCATION" | grep -v '^d' | awk '{print $5, $8}')
  FILE_COUNT=0
  SMALL_FILE_COUNT=0
  SMALL_FILE_SIZE_MB=0
  USED_SIZE_MB=0

  while read -r SIZE PATH; do
    SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $SIZE/1024/1024}")
    USED_SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $USED_SIZE_MB+$SIZE_MB}")
    ((FILE_COUNT++))

    if (( $(echo "$SIZE_MB < $BLOCK_SIZE_MB" | bc -l) )); then
      ((SMALL_FILE_COUNT++))
      SMALL_FILE_SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $SMALL_FILE_SIZE_MB+$SIZE_MB}")
      echo "  ⚠ Small file: $PATH — ${SIZE_MB}MB" >> "$TMP_REPORT"
    fi
  done <<< "$FILES"

  WASTED_MB=$(awk "BEGIN {printf \"%.2f\", ($SMALL_FILE_COUNT * $BLOCK_SIZE_MB) - $SMALL_FILE_SIZE_MB}")
  echo "  📊 Total files         : $FILE_COUNT" >> "$TMP_REPORT"
  echo "  🧩 Small files (<$BLOCK_SIZE_MB MB): $SMALL_FILE_COUNT" >> "$TMP_REPORT"
  echo "  💾 Table size (MB)     : $USED_SIZE_MB" >> "$TMP_REPORT"
  echo "  🚫 Estimated space wasted (MB): $WASTED_MB" >> "$TMP_REPORT"

  # Update totals
  TOTAL_FILES=$((TOTAL_FILES + FILE_COUNT))
  TOTAL_SMALL_FILES=$((TOTAL_SMALL_FILES + SMALL_FILE_COUNT))
  TOTAL_USED_MB=$(awk "BEGIN {printf \"%.2f\", $TOTAL_USED_MB + $USED_SIZE_MB}")
  TOTAL_WASTED_MB=$(awk "BEGIN {printf \"%.2f\", $TOTAL_WASTED_MB + $WASTED_MB}")
done

# Summary
{
  echo -e "\n================== 📦 SCHEMA SUMMARY =================="
  echo "🔍 Database: $HIVE_DB"
  echo "📁 Total files: $TOTAL_FILES"
  echo "🧩 Total small files: $TOTAL_SMALL_FILES"
  echo "💾 Total data size (MB): $TOTAL_USED_MB"
  echo "🚫 Total space wasted (MB, approx): $TOTAL_WASTED_MB"
  echo "======================================================="
} >> "$TMP_REPORT"

cat "$TMP_REPORT"
echo -e "\n📄 Report saved at: $TMP_REPORT"

'''
project/

│
├── watcher/
│   ├── file_watcher.py
│   ├── route_resolver.py
│   ├── audit_logger.py
│   ├── file_utils.py
│
├── configs/
│   ├── routes.yaml
│   │
│   ├── dev/
│   │   ├── s4_tb.yaml
│   │   ├── s4_bs.yaml
│   │   ├── overlays.yaml
│   │   └── global_rates.yaml
│   │
│   ├── uat/
│   └── prod/
│
├── spark/
│   └── generic_loader.py
│
├── logs/
│
└── start_watcher.sh

routes.yaml

routes:

  S4_TX:
    pattern: ".*_S4_TX_.*\\.csv\\.gz"
    config_file: "s4_tb.yaml"

  S4_BX:
    pattern: ".*_S4_BX_.*\\.csv\\.gz"
    config_file: "s4_bs.yaml"

  OVERLAYS:
    pattern: "OXXXLAYS.*\\.csv\\.gz"
    config_file: "oxxxlays.yaml"

  GLOBAL_RATES:
    pattern: "Global_rates__.*\\.csv\\.gz"
    config_file: "global_rates.yaml"

configs/dev/s4_tx.yaml

hive_schema: xyz_dev
hive_table: pqr

hana_schema: sst_dev
hana_table: pqr_hana

spark:
  executor_memory: 4g
  executor_cores: 2
  num_executors: 4

retry_count: 3

route_resolver.py

import yaml
import re
import os


class RouteResolver:

    def __init__(self, route_file):
        with open(route_file, "r") as f:
            self.routes = yaml.safe_load(f)["routes"]

    def resolve(self, file_name):

        for route_name, route_details in self.routes.items():

            pattern = route_details["pattern"]

            if re.match(pattern, file_name):
                return {
                    "file_type": route_name,
                    "config_file": route_details["config_file"]
                }

        return None

file_utils.py
Handles:
stability checks
duplicate prevention

import os
import time


def wait_until_file_complete(file_path, wait_time=30):

    """
    NAS uploads may still be running.
    We verify file size remains unchanged.
    """

    size1 = os.path.getsize(file_path)

    time.sleep(wait_time)

    size2 = os.path.getsize(file_path)

    return size1 == size2

file_watcher.py

import argparse
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from route_resolver import RouteResolver
from file_utils import wait_until_file_complete
from audit_logger import AuditLogger


WATCH_PATH = "/mnt/nas_data/incoming"

MAX_PARALLEL_JOBS = 3


class NASHandler(FileSystemEventHandler):

    def __init__(self, env):

        self.env = env

        self.route_resolver = RouteResolver(
            "../configs/routes.yaml"
        )

        self.audit_logger = AuditLogger()

        self.executor = ThreadPoolExecutor(
            max_workers=MAX_PARALLEL_JOBS
        )

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = event.src_path

        file_name = os.path.basename(file_path)

        print(f"\nDetected file: {file_name}")

        # ----------------------------------------------------
        # STEP 1
        # Check if already processed successfully
        # ----------------------------------------------------

        if self.audit_logger.already_processed(file_name):

            print(f"{file_name} already processed")

            return

        # ----------------------------------------------------
        # STEP 2
        # Identify file type dynamically
        # ----------------------------------------------------

        route = self.route_resolver.resolve(file_name)

        if not route:

            print(f"No route found for {file_name}")

            return

        file_type = route["file_type"]

        config_file = route["config_file"]

        print(f"Resolved route: {file_type}")

        # ----------------------------------------------------
        # STEP 3
        # Ensure file upload completed
        # ----------------------------------------------------

        if not wait_until_file_complete(file_path):

            print(f"{file_name} still uploading")

            return

        # ----------------------------------------------------
        # STEP 4
        # Insert audit STARTED entry
        # ----------------------------------------------------

        self.audit_logger.insert_record(
            file_name,
            file_type
        )

        # ----------------------------------------------------
        # STEP 5
        # Submit asynchronously
        # Avoid blocking watchdog thread
        # ----------------------------------------------------

        self.executor.submit(
            self.trigger_spark_job,
            file_path,
            file_type,
            config_file
        )

    def trigger_spark_job(self,
                          file_path,
                          file_type,
                          config_file):

        try:

            config_path = f"../configs/{self.env}/{config_file}"

            spark_command = [
                "spark-submit",
                "--master", "yarn",
                "--deploy-mode", "cluster",

                "../spark/generic_loader.py",

                "--file-path", file_path,
                "--config-path", config_path,
                "--file-type", file_type,
                "--env", self.env
            ]

            print(f"Launching Spark Job: {file_type}")

            result = subprocess.run(
                spark_command,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                print(f"SUCCESS: {file_path}")

                self.audit_logger.update_status(
                    os.path.basename(file_path),
                    "SUCCESS"
                )

            else:

                print(result.stderr)

                self.audit_logger.update_status(
                    os.path.basename(file_path),
                    "FAILED",
                    result.stderr
                )

        except Exception as e:

            self.audit_logger.update_status(
                os.path.basename(file_path),
                "FAILED",
                str(e)
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--env", required=True)

    args = parser.parse_args()

    event_handler = NASHandler(args.env)

    observer = PollingObserver(timeout=10)

    observer.schedule(
        event_handler,
        WATCH_PATH,
        recursive=False
    )

    observer.start()

    print(f"Watching path: {WATCH_PATH}")

    observer.join()

 
python3 /project/watcher/file_watcher.py --env dev

Architecture
Watcher detects file
        ↓
Watcher submits spark-submit
        ↓
Scala Spark program starts
        ↓
Spark inserts STARTED into audit table
        ↓
Spark processes file
        ↓
Spark updates SUCCESS / FAILED
'''  


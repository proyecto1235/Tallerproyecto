#!/usr/bin/env python3
"""run_all.py — Orchestrate the full ML pipeline.

Executes stages 01-04 in order using subprocess.
Each stage runs as an independent Python process.

Usage:
    python run_all.py              # full pipeline
    python run_all.py --skip 03    # skip evaluation
    python run_all.py --only 02    # run only training
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SCRIPTS = [
    ("01_generate_dataset.py", "Generating synthetic dataset"),
    ("02_train_models.py", "Training supervised models"),
    ("03_evaluate_models.py", "Evaluating models"),
    ("04_train_unsupervised.py", "Training unsupervised models"),
]


def run_script(script_path: str, step_name: str) -> bool:
    logger.info(f"=== {step_name} ===")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False,
    )
    if result.returncode != 0:
        logger.error(f"Stage failed: {script_path} (exit code {result.returncode})")
        return False
    logger.info(f"Completed: {step_name}")
    return True


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    args = set(sys.argv[1:])

    skip_list: set = set()
    only_list: set = set()

    for arg in args:
        if arg.startswith("--skip="):
            skip_list.add(arg.split("=")[1])
        elif arg.startswith("--only="):
            only_list.add(arg.split("=")[1])

    for script_name, step_name in SCRIPTS:
        stage_id = script_name[:2]

        if skip_list and stage_id in skip_list:
            logger.info(f"Skipping stage {stage_id} ({step_name})")
            continue

        if only_list and stage_id not in only_list:
            continue

        script_path = os.path.join(base_dir, script_name)
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return 1

        success = run_script(script_path, step_name)
        if not success:
            logger.error("Pipeline aborted due to failure.")
            return 1

    logger.info("Pipeline complete. Models in models/, reports in reports/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

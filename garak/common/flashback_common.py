# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Common parameters and utilities for flashback probe and generator"""

import json
import logging
from pathlib import Path

from garak import _config


#logger = logging.getLogger(__name__)

def read_reports(report_prefix: str) -> list[dict]:
    """Read and parse report files based on prefix or default name"""
    reports = []
    
#    print(f"report_prefix: {report_prefix}")

    # Find all files matching the prefix pattern
    report_files = Path('.').glob(f"{report_prefix}*.report.jsonl")
    
    # Read and parse each report file
    for report_file in report_files:
        print(f"report_file: {report_file}")
        if not report_file.exists():
            continue
        with open(report_file, 'r') as f:
            for line in f:
                try:
                    report = json.loads(line.strip())
                    if report.get('entry_type') != 'attempt' or report.get('status') != 2:
                        continue
                    reports.append(report)
                except json.JSONDecodeError:
                    continue
        logging.debug("read_reports length: %s", len(reports))
    return reports

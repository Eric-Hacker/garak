# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Probe that reads previous report.jsonl files to create prompts based on past results"""

import json
from pathlib import Path
from typing import List

from garak import _config
from garak.probes import Probe
from garak.common.flashback_common import read_reports


DEFAULT_PARAMS = Probe.DEFAULT_PARAMS |  {
        "report_prefix": _config.reporting.report_dir + "/"
    }

class FlashbackBase(Probe):
    """Base class for Flashback probes that read report.jsonl files"""
    
    active = False

    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)
        self.prompts = []
        
    def _read_reports(self) -> List[dict]:
        """Read and parse report files based on prefix or default name"""
        return read_reports(self.report_prefix)

    def _filter_attempts(self, reports: List[dict], status: str) -> List[str]:
        """Filter attempt entries based on detector results"""
        filtered_prompts = []
        for report in reports:
            detector_results = report.get('detector_results', [])
            # Check if all detector results are zero
            all_zero = all(result[0] == 0 for result in detector_results.values())
            if all_zero and (status == 'pass'):
                filtered_prompts.append(report.get('prompt', ''))
            elif not all_zero and (status == 'fail'):
                filtered_prompts.append(report.get('prompt', ''))
            elif status == 'all':  
                filtered_prompts.append(report.get('prompt', ''))
                
        return filtered_prompts

class Pass(FlashbackBase):
    """Probe that uses prompts from previous passing attempts"""
    
    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)
        reports = self._read_reports()
        self.prompts = self._filter_attempts(reports, status='pass')

class Fail(FlashbackBase):
    """Probe that uses prompts from previous failed attempts"""
    
    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)
        reports = self._read_reports()
        self.prompts = self._filter_attempts(reports, status='fail')

class All(FlashbackBase):
    """Probe that uses prompts from previous runs"""
    
    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)
        reports = self._read_reports()
        self.prompts = self._filter_attempts(reports, status='all')

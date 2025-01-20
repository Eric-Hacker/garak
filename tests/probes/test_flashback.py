# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

import garak._config
from garak.probes.flashback import FlashbackBase, Pass, Fail, All

# Test data
MOCK_REPORTS = [
    # Passing attempt (all detector results are 0)
    {
        "entry_type": "attempt",
        "status": 2,
        "prompt": "passing prompt",
        "detector_results": {"detector1": 0, "detector2": 0}
    },
    # Failing attempt (some detector results are non-zero)
    {
        "entry_type": "attempt",
        "status": 2,
        "prompt": "failing prompt",
        "detector_results": {"detector1": 1, "detector2": 0}
    },
    # Non-attempt entry
    {
        "entry_type": "start_run",
        "status": 1,
        "prompt": "should be ignored"
    },
    # Wrong status
    {
        "entry_type": "attempt",
        "status": 1,
        "prompt": "wrong status"
    }
]

@pytest.fixture
def mock_report_file(tmp_path):
    """Create a mock report file with test data"""
    report_dir = tmp_path / "garak_runs"
    report_dir.mkdir()
    report_file = report_dir / "test.report.jsonl"
    
    with open(report_file, "w") as f:
        for report in MOCK_REPORTS:
            f.write(json.dumps(report) + "\n")
    
    return report_dir

@pytest.fixture
def config_with_report_dir(mock_report_file):
    """Create config with report directory set"""
    garak._config.load_base_config()
    config = garak._config
    config.reporting.report_dir = str(mock_report_file)
    return config

def test_flashback_base_read_reports(config_with_report_dir):
    """Test reading report files"""
    probe = FlashbackBase(config_root=config_with_report_dir)
    reports = probe._read_reports()
    
    # Should only include attempt entries with status 2
    assert len(reports) == 2
    assert all(r["entry_type"] == "attempt" and r["status"] == 2 for r in reports)

def test_flashback_base_filter_attempts_pass(config_with_report_dir):
    """Test filtering for passing attempts"""
    probe = FlashbackBase(config_root=config_with_report_dir)
    reports = MOCK_REPORTS
    filtered = probe._filter_attempts(reports, status="pass")
    
    assert len(filtered) == 1
    assert "passing prompt" in filtered

def test_flashback_base_filter_attempts_fail(config_with_report_dir):
    """Test filtering for failing attempts"""
    probe = FlashbackBase(config_root=config_with_report_dir)
    reports = MOCK_REPORTS
    filtered = probe._filter_attempts(reports, status="fail")
    
    assert len(filtered) == 1
    assert "failing prompt" in filtered

def test_flashback_base_filter_attempts_all(config_with_report_dir):
    """Test filtering for all attempts"""
    probe = FlashbackBase(config_root=config_with_report_dir)
    reports = MOCK_REPORTS
    filtered = probe._filter_attempts(reports, status="all")
    
    # Should include both passing and failing attempts
    assert len(filtered) == 2
    assert "passing prompt" in filtered
    assert "failing prompt" in filtered

def test_pass_probe_initialization(config_with_report_dir):
    """Test Pass probe initialization"""
    probe = Pass(config_root=config_with_report_dir)
    assert len(probe.prompts) == 1
    assert "passing prompt" in probe.prompts

def test_fail_probe_initialization(config_with_report_dir):
    """Test Fail probe initialization"""
    probe = Fail(config_root=config_with_report_dir)
    assert len(probe.prompts) == 1
    assert "failing prompt" in probe.prompts

def test_all_probe_initialization(config_with_report_dir):
    """Test All probe initialization"""
    probe = All(config_root=config_with_report_dir)
    assert len(probe.prompts) == 2
    assert "passing prompt" in probe.prompts
    assert "failing prompt" in probe.prompts

def test_invalid_json_handling(tmp_path):
    """Test handling of invalid JSON in report files"""
    report_dir = tmp_path / "garak_runs"
    report_dir.mkdir()
    report_file = report_dir / "invalid.report.jsonl"
    
    # Write some invalid JSON
    with open(report_file, "w") as f:
        f.write("this is not json\n")
        f.write(json.dumps(MOCK_REPORTS[0]) + "\n")
    
    config = _config
    config.reporting.report_dir = str(report_dir)
    
    probe = FlashbackBase(config_root=config)
    reports = probe._read_reports()
    
    # Should skip invalid JSON and include valid entries
    assert len(reports) == 1

def test_missing_report_file(tmp_path):
    """Test behavior when report file is missing"""
    report_dir = tmp_path / "garak_runs"
    report_dir.mkdir()
    
    config = _config
    config.reporting.report_dir = str(report_dir)
    
    probe = FlashbackBase(config_root=config)
    reports = probe._read_reports()
    
    assert len(reports) == 0

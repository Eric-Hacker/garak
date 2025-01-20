# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator that uses responses from previous report files"""

from typing import List, Optional

from garak import _config
from garak.generators import Generator
from garak.common.flashback_common import read_reports
from garak.probes.flashback import DEFAULT_PARAMS

class FlashbackGenerator(Generator):
    """Generator that uses responses from previous report files"""
    
    DEFAULT_PARAMS = Generator.DEFAULT_PARAMS | DEFAULT_PARAMS

    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)
        self.responses = self._load_responses()
        
    def _load_responses(self) -> List[str]:
        """Load responses from previous report files"""
        reports = read_reports(self.report_prefix)
        return [report.get('outputs', [''])[0] for report in reports if report.get('outputs')]
        
    def generate(self, prompt: str) -> Optional[str]:
        """Return a response from previous reports if available"""
        if not self.responses:
            return None
        # Needs work. THis doesn't seem like it would work right if there are multiple prompts that were the same, but how to track that?
        # Perhaps track the use of each prompt?
        # Not sure why this code would work in any case seems hallucinated.
        return self.responses[hash(prompt) % len(self.responses)]
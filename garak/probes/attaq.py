import pandas as pd

from garak import _config
from garak.probes import Probe

class Attaq100(Probe):
    recommended_detector = [
        "shields.Up",
    ]

    def __init__(self, config_root=_config):
        super().__init__(config_root=config_root)

        attaq_file = (_config.transient.package_dir / "resources" / "attaq" / "attaq_dataset.csv")
        self.prompts = list(pd.read_csv(attaq_file, usecols=['input'], nrows=100)['input'].values)

class Attaq(Probe):
    recommended_detector = [
        "shields.Up",
    ]

    def __init__(self, config_root=_config):
        super().__init__(config_root)

        attaq_file = (_config.transient.package_dir / "resources" / "attaq" / "attaq_dataset.csv")
        self.prompts = list(pd.read_csv(attaq_file, usecols=['input'])['input'].values)

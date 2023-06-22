"""Abacura configuration module"""

from pathlib import Path
from typing import Any

from tomlkit import parse

DEFAULT_GLOBAL_CONFIG = {
    "module_paths": [],
    "css_path": "css/abacura.css",
}


class Config:
    """Base configuration class"""
    _config = None
    _config_file: str
    name = "config"
       
    def __init__(self, **kwargs):
        super().__init__()
        if "config" not in kwargs or kwargs["config"] is None:
            kwargs["config"] = "~/.abacura"
            p = Path(kwargs["config"]).expanduser()
            if not p.is_file():
                with open(p, "w", encoding="UTF-8"):
                    pass
        self._config_file = kwargs["config"]
        self.reload()

    def reload(self) -> None:
        """Reload configuration file from disk"""
        cfile = Path(self._config_file).expanduser()
        try:
            self._config = parse(open(cfile, "r", encoding="UTF-8").read())

        except Exception as config_exception:
            raise (config_exception)

    def get_specific_option(self, section: str, key: str, default=None) -> Any:
        """Get configuration value for section, global, or default"""

        if section in self.config and key in self.config[section]:
            return self.config[section][key]

        if "global" in self.config and key in self.config["global"]:
            return self.config["global"][key]

        if key in DEFAULT_GLOBAL_CONFIG:
            return DEFAULT_GLOBAL_CONFIG[key]

        return default

    @property
    def config(self):
        return self._config

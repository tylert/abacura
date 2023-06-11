"""Abacura configuration module"""

from pathlib import Path
from typing import Any, Optional

from rich.markup import escape
from rich.panel import Panel
from textual import log
from tomlkit import parse

from abacura.plugins import command, Plugin

DEFAULT_GLOBAL_CONFIG = {
    "module_paths": [],
    "css_path": "abacura.css",
}

class Config(Plugin):
    """Base configuration class"""
    _config = None
    _config_file: str
    name = "config"
       
    def __init__(self, **kwargs):
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
            self._config = parse(open(cfile,"r", encoding="UTF-8").read())

        except Exception as config_exception:
            print(f"{cfile}: {repr(config_exception)}")

    def get_specific_option(self, section: str, key: str) -> Any:
        """Get configuration value for section, global, or default"""

        if section in self.config and key in self.config[section]:
            return self.config[section][key]

        if "global" in self.config and key in self.config["global"]:
            return self.config["global"][key]

        if key in DEFAULT_GLOBAL_CONFIG:
            return DEFAULT_GLOBAL_CONFIG[key]

        return None

    @property
    def config(self):
        return self._config

    @command(name="conf")
    def configcommand(self, context, reload: bool = False, full: bool = False) -> None:
        """@conf command"""

        log(f"@conf called with full '{full}' and reload '{reload}'")
        if full or context["app"].session =="null":
            
                conf = escape(context["manager"].config.config.as_string())
        else:
                conf = escape(
                    context["manager"].config.config[context["app"].session].as_string())
        
        panel = Panel(conf, highlight=True)
        tl = context["manager"].tl
        tl.markup = True
        tl.write(panel)
        tl.markup = False
     
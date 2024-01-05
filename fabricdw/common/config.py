from __future__ import annotations

import json
from os.path import exists
from typing import Any

from colorama import Fore, Style

from fabricdw.common import absolute_path

CONFIG_FILE: str = absolute_path("~/.config/fabricdw.json")


def _default_get(source: dict, name: str, fallback: Any) -> Any:
	return source[name] if name in source else fallback


class DictSerialization:
	def to_dict(self) -> dict:
		pass
	
	@classmethod
	def from_dict(cls, data: dict):
		pass


class Installation(DictSerialization):
	def __init__(self, data: dict):
		self.name = data["name"]
		self.root = data["root"]
	
	def __eq__(self, other):
		if isinstance(other, Installation):
			return other.name == self.name
		return False
	
	@classmethod
	def from_dict(cls, data: dict) -> Installation:
		return cls(data)
	
	def to_dict(self) -> dict:
		return {
			'root': self.root,
			'name': self.name
		}
	
	def pretty_name(self, after: Fore = None) -> str:
		return Installation.pretty_name_str(self.name, after)
	
	@staticmethod
	def pretty_name_str(name: str, after: Fore = None) -> str:
		return f"{Fore.CYAN}{name}{Style.RESET_ALL}{after if after else ''}"


class Defaults(DictSerialization):
	def __init__(self, data: dict):
		self.min_ram = _default_get(data, "min-ram", 0.5)
		self.max_ram = _default_get(data, "max-ram", 6)
		self.idle_time = _default_get(data, "idle_time", 0)
		self.backups = _default_get(data, "backups", 5)
	
	@classmethod
	def from_dict(cls, data: dict) -> Defaults:
		return cls(data)
	
	def to_dict(self) -> dict:
		return {
			"min-ram": self.min_ram,
			"max-ram": self.max_ram,
			"idle_time": self.idle_time,
			"backups": self.backups
		}


class Config(DictSerialization):
	def __init__(self, default: Defaults, installations: list[Installation]):
		self.defaults: Defaults = default
		self.installations: list[Installation] = installations
	
	@classmethod
	def from_dict(cls, data: dict) -> Config:
		defaults = Defaults.from_dict(data['defaults'])
		installations = [Installation.from_dict(installation) for installation in data['installations']]
		
		return cls(defaults, installations)
	
	def to_dict(self) -> dict:
		return {
			'defaults': self.defaults.to_dict(),
			'installations': [installation.to_dict() for installation in self.installations]
		}
	
	def add_installation(self, name: str, root: str) -> None:
		self.installations.append(Installation({
			"name": name,
			"root": root
		}))
	
	def remove_installation(self, installation: Installation) -> None:
		self.installations.remove(installation)
	
	def get_installation(self, name: str) -> Installation | None:
		for installation in self.installations:
			if installation.name == name:
				return installation
		
		return None


def _load_config() -> Config:
	raw: dict = {}
	if exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'r') as cfg:
			raw = json.load(cfg)
	else:
		print("config file missing, creating new")
		raw = {
			"defaults": {
				"min_ram": 0.5,
				"max_ram": 6,
				"idle_time": 0,
				"backups": 5,
			},
			'installations': []
		}
	
	return Config.from_dict(raw)


CONFIG: Config = _load_config()


def write_config() -> None:
	with open(CONFIG_FILE, "w") as config:
		json.dump(CONFIG.to_dict(), config, indent=4)

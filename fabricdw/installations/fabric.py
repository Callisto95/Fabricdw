from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

import requests
from pick import pick
from requests import Response

from fabricdw.args import args
from fabricdw.common import InvalidCombinationException, SERVER_JAR_FILE, VersionChoice

API_URL: str = "https://meta.fabricmc.net/v2"
BASE_URL: str = f"{API_URL}/versions"


class StableVersionDict:
	def __init__(self, data: dict[str, Any]):
		self.version: str = data["version"]
		self.stability: bool = data["stable"]
		self.data: dict[str, Any] = data
	
	def __str__(self) -> str:
		return f"{self.version} {self.stability} :: {self.data}"
	
	@classmethod
	def simple(cls, version: str = None, stability: bool = None) -> StableVersionDict:
		if version is None and stability is None:
			raise ValueError("version and stabiliy cannot be None")
		
		return StableVersionDict({ "version": version, "stable": stability })


class ApiUrls(StrEnum):
	GAME: str = f"{BASE_URL}/game"
	LOADER: str = f"{BASE_URL}/loader"
	INSTALLER: str = f"{BASE_URL}/installer"


def find_version(versions: list[StableVersionDict], version: str, stable: bool) -> StableVersionDict | None:
	for v in versions:
		if v.version == version and v.stability == stable:
			return v
	
	return None


def filter_versions(versions: list[StableVersionDict], stable: bool) -> list[StableVersionDict]:
	filtered_versions = [version for version in versions if version.stability is stable]
	
	return filtered_versions


def get_versions(url: ApiUrls) -> list[StableVersionDict]:
	versions = json.loads(requests.get(url).text)
	
	return [StableVersionDict(version) for version in versions]


def build_server_jar_url(game: StableVersionDict, loader: StableVersionDict, installer: StableVersionDict) -> str:
	return f"{BASE_URL}/loader/{game.version}/{loader.version}/{installer.version}/server/jar"


def evaluate_user_choice(version, versions: list[StableVersionDict], name: str) -> StableVersionDict:
	if version == VersionChoice.ASK or version is None:
		_, i = pick([v.version for v in versions], f"select {name} version", indicator=">")
		v = versions[i]
		print(f"Using {name} version {v.version}")
		return v
	elif version == VersionChoice.LATEST:
		print(f"Using latest {name} version ({versions[0].version})")
		return versions[0]
	else:
		print(f"Using given version for {name} ({version})")
		return StableVersionDict.simple(version=version)


def evaluate_versions() -> str:
	"""evaluate given versions, ask user if necessary"""
	print("Getting latest versions...")
	
	game_versions: list[StableVersionDict] = get_versions(ApiUrls.GAME)
	loader_versions: list[StableVersionDict] = get_versions(ApiUrls.LOADER)
	installer_versions: list[StableVersionDict] = get_versions(ApiUrls.INSTALLER)
	
	if not args().allow_snapshots:
		game_versions: list[StableVersionDict] = filter_versions(game_versions, True)
	
	if not args().allow_unstable:
		loader_versions: list[StableVersionDict] = filter_versions(loader_versions, True)
		installer_versions: list[StableVersionDict] = filter_versions(installer_versions, True)
	
	game_version = evaluate_user_choice(args().game_version, game_versions, "game")
	loader_version = evaluate_user_choice(args().loader_version, loader_versions, "loader")
	installer_version = evaluate_user_choice(args().installer_version, installer_versions, "installer")
	
	return build_server_jar_url(game_version, loader_version, installer_version)


def download_server_jar(directory: str, server_url: str) -> str:
	server_jar_response: Response = requests.get(server_url)
	
	if server_jar_response.status_code != 200:
		raise InvalidCombinationException()
	
	server_jar_file: str = f"{directory}/{SERVER_JAR_FILE}"
	
	with open(server_jar_file, "wb") as jar:
		jar.write(server_jar_response.content)
	
	return server_jar_file


def select_and_download_version(installation_directory: str = None) -> str:
	"""User selects version, download it

	:param installation_directory the directory, where the server jar is placed

	:returns: path of the downloaded jar file"""
	
	if not installation_directory:
		installation_directory = args().output_dir
	
	server_url: str = evaluate_versions()
	
	server_jar_file = download_server_jar(installation_directory, server_url)
	
	return server_jar_file

import json
from enum import StrEnum

import requests
from pick import pick

API_URL: str = "https://meta.fabricmc.net/v2"
BASE_URL: str = f"{API_URL}/versions"


# no enum for bool, class used instead
class VersionStability:
	STABLE: bool = True
	UNSTABLE: bool = False


class ApiUrls(StrEnum):
	GAME: str = f"{BASE_URL}/game"
	LOADER: str = f"{BASE_URL}/loader"
	INSTALLER: str = f"{BASE_URL}/installer"


def filter_versions(versions: list[dict], type: bool) -> list[dict]:
	filtered_versions = [version for version in versions if version['stable'] is type]
	
	return filtered_versions


def get_versions(type: ApiUrls) -> list[dict]:
	versions = json.loads(requests.get(type).text)
	
	return versions


def build_server_jar_url(game: dict[str, str], loader: dict[str, str], installer: dict[str, str]) -> str:
	return f"{BASE_URL}/loader/{game['version']}/{loader['version']}/{installer['version']}/server/jar"


def selection_from_user(game_versions: list[dict], loader_versions: list[dict], installer_versions: list[dict]) -> \
	tuple[dict, dict, dict]:
	# option is quite different from what is needed
	_, game_index = pick([game['version'] for game in game_versions], "select game version", indicator=">")
	_, loader_index = pick([loader['version'] for loader in loader_versions], "select loader version", indicator=">")
	_, installer_index = pick(
		[installer['version'] for installer in installer_versions], "select installer version", indicator=">"
	)
	
	return game_versions[game_index], loader_versions[loader_index], installer_versions[installer_index]


def select_version() -> str:
	print("getting latest versions...")
	
	game_versions = get_versions(ApiUrls.GAME)
	loader_versions = get_versions(ApiUrls.LOADER)
	installer_versions = get_versions(ApiUrls.INSTALLER)
	
	stable_game_versions = filter_versions(game_versions, VersionStability.STABLE)
	stable_loader_versions = filter_versions(loader_versions, VersionStability.STABLE)
	stable_installer_versions = filter_versions(installer_versions, VersionStability.STABLE)
	
	unstable_game_versions = filter_versions(game_versions, VersionStability.UNSTABLE)
	
	# loader and installer are latest by default
	# any 'unstable' loader or installer are out of date
	latest_stable = stable_game_versions[0]['version']
	latest_unstable = unstable_game_versions[0]['version']
	
	_, index = pick(
		[f"latest ({latest_stable})", f"latest-unstable ({latest_unstable})", "custom"], "select version",
		indicator=">"
	)
	
	match index:
		case 2:
			game_version, loader_version, installer_version = selection_from_user(
				game_versions, loader_versions, installer_versions
			)
		case 1:
			game_version, loader_version, installer_version = unstable_game_versions[0], stable_loader_versions[0], \
				stable_installer_versions[0]
		case 0 | _:
			game_version, loader_version, installer_version = stable_game_versions[0], stable_loader_versions[0], \
				stable_installer_versions[0]
	
	return build_server_jar_url(game_version, loader_version, installer_version)

import os
from os.path import exists

from fabricdw.args import args
from fabricdw.common import (convert_bool_to_str, convert_str_to_bool, EULA_FILE, FABRICD_ENV_FILE, Installation,
	SERVER_JAR_FILE, SERVER_PROPERTIES_FILE)
from fabricdw.installations.create import initialize_server, create_fabricdw_script
from fabricdw.installations.fabric import select_and_download_version
from fabricdw.properties import modify_properties


def update_installation() -> None:
	installation: Installation = Installation.ensure_exists(args().name)
	args().output_dir = installation.root
	
	server_jar: str = f"{installation.root}/{SERVER_JAR_FILE}"
	server_properties: str = f"{installation.root}/{SERVER_PROPERTIES_FILE}"
	fabricdw: str = f"{installation.root}/{FABRICD_ENV_FILE}"
	eula: str = f"{installation.root}/{EULA_FILE}"
	
	server_jar_backup: str = f"{server_jar}-bak"
	server_properties_backup: str = f"{server_properties}-bak"
	fabricdw_backup: str = f"{fabricdw}-bak"
	eula_backup: str = f"{eula}-original"
	
	originals_and_backup: list[tuple[str, str]] = list(zip(
		[server_jar, server_properties, fabricdw, eula],
		[server_jar_backup, server_properties_backup, fabricdw_backup, eula_backup]
	))
	
	try:
		for original, backup in originals_and_backup:
			os.replace(original, backup)
		
		select_and_download_version()
		
		initialize_server()
		
		modify_properties()
		
		create_fabricdw_script()
		
		# eula may have been accepted before, keep the state
		os.replace(eula_backup, eula)
		
		print(f"Updated installation {installation}")
		
		if args().keep_backups:
			print("Keeping backup files")
		else:
			for file in [server_jar_backup, server_properties_backup, fabricdw_backup]:
				os.remove(file)
			print("Deleted backup files")
	except Exception as err:
		print(f"An error occurred ({err})! Undoing update...")
		
		for original, backup in originals_and_backup:
			if exists(backup):
				os.replace(backup, original)

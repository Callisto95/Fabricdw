import os

from fabricdw.args import args
from fabricdw.common import (Installation, SERVER_JAR_FILE)
from fabricdw.installations.fabric import select_and_download_version


def update_installation() -> None:
	installation: Installation = Installation.ensure_exists(args().name)
	args().output_dir = installation.root
	
	server_jar: str = f"{installation.root}/{SERVER_JAR_FILE}"
	
	server_jar_backup: str = f"{server_jar}-bak"
	
	try:
		os.replace(server_jar, server_jar_backup)
		
		select_and_download_version()
		
		print(f"Updated installation {installation}")
		
		if args().keep_backups:
			print("Keeping server backup")
		else:
			os.remove(server_jar_backup)
			print("Deleted server backup")
	except Exception as err:
		print(f"An error occurred ({err})! Undoing update...")
		os.replace(server_jar_backup, server_jar)

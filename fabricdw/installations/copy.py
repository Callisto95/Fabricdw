import os
import shutil

from colorama import Fore, Style

from fabricdw.args import args
from fabricdw.common import ask_okay_to_write_into, CONFIG, Installation, remove_dir


def copy_installation() -> None:
	source: Installation = Installation.ensure_exists(args().source)
	Installation.ensure_does_not_exist(args().target)
	
	target_directory: str = args().output_dir
	
	try:
		os.makedirs(target_directory, exist_ok=True)
		
		if not ask_okay_to_write_into(target_directory, message_if_cancelled="copy cancelled"):
			return
		
		shutil.copytree(source.root, target_directory, dirs_exist_ok=True)
		
		new_installation: Installation = CONFIG.create_new_installation(args().target, target_directory)
		
		print(
			f"Copied {source.pretty_name()} as {new_installation.pretty_name()} "
			f"('{source.root}' -> '{new_installation.root}')"
		)
		
		print(
			f"Remember to change ports and the world name in the 'server.properties' {Fore.YELLOW}AND{Style.RESET_ALL} "
			f"in the 'fabricdw' file!"
		)
	except KeyboardInterrupt:
		if remove_dir(target_directory):
			print("Interrupted! Cleaning up...")

import os
from argparse import Namespace

from colorama import Fore, Style

from fabricdw.common import CONFIG, Installation, remove_dir, yes_no_question


def remove_installation(args: Namespace) -> None:
	installation_name: str = args.name
	active_installation: Installation = CONFIG.get_installation(installation_name)
	
	if active_installation is None:
		print(f"{Fore.RED}Installation '{args.name}' does not exist!{Style.RESET_ALL}")
		return
	
	if _remove_installation(active_installation):
		CONFIG.remove_installation(active_installation)


def _remove_installation(active_installation: Installation) -> bool:
	if not os.path.exists(active_installation.root) or not os.path.isdir(active_installation.root):
		print(f"installation '{active_installation.pretty_name()}' does not exist anymore.")
		return True
	elif yes_no_question(
		f"Remove installation '{active_installation.name}' ({active_installation.root})?\nThis will delete all files!"
	):
		remove_dir(active_installation.root)
		print(f"installation '{active_installation.pretty_name()}' ({active_installation.root}) deleted!")
		return True
	
	print("nothing deleted")
	return False

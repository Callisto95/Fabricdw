import os

from colorama import Fore, Style

from fabricdw.common import yes_no_question, Installation, remove_dir


def remove_installation(active_installation: Installation | None, fallback_name: str) -> bool:
	if active_installation is None:
		print(f"{Fore.RED}installation '{Installation.pretty_name_str(fallback_name, after=Fore.RED)}' does not exist!{Style.RESET_ALL}")
		return False
	
	if not os.path.exists(active_installation.root) or not os.path.isdir(active_installation.root):
		print(f"installation '{active_installation.pretty_name()}' does not exist anymore.")
		return True
	elif yes_no_question(f"Remove installation '{active_installation.name}' ({active_installation.root})?\nThis will delete all files!"):
		remove_dir(active_installation.root)
		print(f"installation '{active_installation.pretty_name()}' ({active_installation.root}) deleted!")
		return True
	
	print("nothing deleted")
	return False

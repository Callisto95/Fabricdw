from os.path import exists, isdir

from fabricdw.args import args
from fabricdw.common import CONFIG, Installation, remove_dir, yes_no_question


def delete_installation() -> None:
	active_installation: Installation = Installation.ensure_exists(args().name)
	
	if args().skip_delete_question or yes_no_question(
		f"Remove installation '{active_installation.name}' ({active_installation.root})?\nThis will delete all files!"
	):
		remove_dir(active_installation.root)
		print(f"installation '{active_installation.pretty_name()}' ({active_installation.root}) deleted!")
		CONFIG.remove_installation(active_installation)
	else:
		print("nothing deleted")

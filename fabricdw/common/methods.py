import os.path
import shutil

from pick import pick


def yes_no_question(question: str, yes_first: bool = False) -> bool:
	options = ["No", "Yes"]
	
	if yes_first:
		options = options[::-1]
	
	_, index = pick(options, question, indicator=">")
	
	return index == 1


def remove_dir(directory: str) -> None:
	shutil.rmtree(directory)


def absolute_path(path: str) -> str:
	return os.path.abspath(os.path.expanduser(path))


def okay_to_write_into(_dir: str) -> bool:
	if len(os.listdir(_dir)) > 0 and not yes_no_question(f"The directory '{_dir}' is not empty. Proceed anyway?"):
		print("cancelling installation")
		return False
	return True

from argparse import Namespace
from colorama import Fore, Style


def create_replacements(args: Namespace) -> dict[str, str]:
	replacements: dict[str, str] = {}
	
	for property_ in args.properties:
		contents: list[str] = property_.split("=")
		
		if len(contents) != 2:
			print(f"{Fore.RED}invalid property argument: '{property_}'!{Style.RESET_ALL}")
			continue
		
		replacements[contents[0]] = contents[1]
	
	return replacements


def modify_properties(active_dir: str, replacements: dict[str, str]) -> None:
	print("modifying server.properties...")
	
	properties_file: str = f"{active_dir}/server.properties"
	lines: list[str] = []
	
	with open(properties_file, "r") as properties:
		lines = [line.strip() for line in properties.readlines()]
		
		for index, line in enumerate(lines):
			if "=" not in line or line.startswith("#"):
				continue
			
			key, _ = line.split("=")
			
			if key not in replacements:
				continue
			
			lines[index] = f"{key}={replacements.pop(key)}"
	
	if len(replacements) != 0:
		print(f"{Fore.YELLOW}some properties have not been used:{Style.RESET_ALL}")
		for key, value in replacements.items():
			print(f"\t{key} ({value})")
	
	with open(properties_file, "w") as properties:
		properties.writelines([f"{line}\n" for line in lines])

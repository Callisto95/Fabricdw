from argparse import Namespace

from colorama import Fore, Style


def create_replacements(args: Namespace) -> dict[str, str]:
	replacements: dict[str, str] = { }
	
	for property_ in args.properties:
		contents: list[str] = property_.split("=")
		
		if len(contents) != 2:
			print(f"{Fore.YELLOW}invalid property argument: '{property_}'!{Style.RESET_ALL}")
			continue
		
		if contents[0] in replacements:
			print(f"{Fore.YELLOW}Duplicate property: '{contents[0]}' (value: '{contents[1]}')!{Style.RESET_ALL}")
			continue
		
		replacements[contents[0]] = contents[1]
	
	return replacements


def read_file(file: str) -> list[str]:
	lines: list[str]
	
	with open(file, "r") as properties:
		lines = [line.strip() for line in properties.readlines()]
	
	return lines


def split_line(line: str) -> tuple[str, str] | tuple[None, None]:
	line: str = line.strip()
	
	if "=" not in line or line.startswith("#"):
		return None, None
	
	# repack list[str] to tuple[str, str]
	key, value = line.split("=", maxsplit=1)
	return key, value


def modify_properties(active_dir: str, replacements: dict[str, str]) -> None:
	print("modifying server.properties file...")
	
	properties_file: str = f"{active_dir}/server.properties"
	lines: list[str] = read_file(properties_file)
	
	for index, line in enumerate(lines):
		key, _ = split_line(line)
		
		if key is None or key not in replacements:
			continue
		
		lines[index] = f"{key}={replacements.pop(key)}"
	
	if len(replacements) != 0:
		print(f"{Fore.YELLOW}some properties have not been used:")
		for key, value in replacements.items():
			print(f"\t{key} ({value})")
		print(Style.RESET_ALL, end="")
	
	with open(properties_file, "w") as properties:
		properties.writelines([f"{line}\n" for line in lines])

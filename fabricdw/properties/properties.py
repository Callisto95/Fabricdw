def modify_properties(active_dir: str, args) -> None:
	replacements = {
		"server-port": args.port,
		"query.port": args.port,
		"level-name": args.world_name,
		"level-seed": args.seed,
		"difficulty": args.difficulty,
		"gamemode": args.game_mode,
	}
	
	print("modifying server.properties...")
	
	properties_file: str = f"{active_dir}/server.properties"
	lines: list[str] = []
	
	with open(properties_file, "r") as properties:
		lines = properties.readlines()
		
		for index, line in enumerate(lines):
			if "=" not in line or line.startswith("#"):
				continue
			
			_id, _ = line.split("=")
			
			if _id not in replacements:
				continue
			
			lines[index] = f"{_id}={replacements[_id]}\n"
		
	with open(properties_file, "w") as properties:
		properties.writelines(lines)

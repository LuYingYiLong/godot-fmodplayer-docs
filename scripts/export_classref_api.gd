extends SceneTree

func _initialize() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.is_empty():
		push_error("Expected an absolute output JSON path after --")
		quit(1)
		return
	var output: Dictionary = {}
	var source_script: Script = get_script() as Script
	var manifest_path: String = source_script.resource_path.get_base_dir().path_join("../classref/manifest.json")
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(manifest_path)) as Dictionary
	for native_class_value: String in manifest["classes"]:
		var native_class: StringName = StringName(native_class_value)
		if not ClassDB.class_exists(native_class):
			push_error("Extension class unavailable: %s" % native_class)
			quit(1)
			return
		var methods: Array[Dictionary] = ClassDB.class_get_method_list(native_class, true)
		for method: Dictionary in methods:
			var default_values: Array[String] = []
			for default_value: Variant in method["default_args"]:
				default_values.append(var_to_str(default_value))
			method["default_args_repr"] = default_values
			method["return"]["type_name"] = type_string(method["return"]["type"])
			for argument: Dictionary in method["args"]:
				argument["type_name"] = type_string(argument["type"])
		var properties: Array[Dictionary] = ClassDB.class_get_property_list(native_class, true)
		for property: Dictionary in properties:
			property["type_name"] = type_string(property["type"])
			property["default"] = ClassDB.class_get_property_default_value(native_class, property["name"])
			property["default_repr"] = var_to_str(property["default"])
		var dynamic_properties: Array[Dictionary] = []
		if native_class_value.begins_with("FmodAudioEffectEQ"):
			var effect: RefCounted = ClassDB.instantiate(native_class) as RefCounted
			for property: Dictionary in effect.get_property_list():
				if String(property["name"]).begins_with("band_"):
					property["type_name"] = type_string(property["type"])
					property["default_repr"] = var_to_str(effect.get(property["name"]))
					dynamic_properties.append(property)
		var constants: Array[Dictionary] = []
		for constant_name: String in ClassDB.class_get_integer_constant_list(native_class, true):
			constants.append({
				"name": constant_name,
				"value": ClassDB.class_get_integer_constant(native_class, constant_name),
				"enum": ClassDB.class_get_integer_constant_enum(native_class, constant_name),
			})
		output[native_class] = {
			"inherits": ClassDB.get_parent_class(native_class),
			"methods": methods,
			"properties": properties,
			"dynamic_properties": dynamic_properties,
			"signals": ClassDB.class_get_signal_list(native_class, true),
			"constants": constants,
		}
	var file: FileAccess = FileAccess.open(arguments[0], FileAccess.WRITE)
	if file == null:
		push_error("Cannot open output JSON: %s" % arguments[0])
		quit(1)
		return
	file.store_string(JSON.stringify(output, "\t"))
	file.close()
	quit()

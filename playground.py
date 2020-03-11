from displaymanagement.display_manager import DisplayManager
display = DisplayManager(":1")
info = display.get_info()
json_info = display.toJSON()
print(json_info)

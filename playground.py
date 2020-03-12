from displaymanagement.display import Display

display = Display(":1")
display.init_display()
display.load_screen()
display.load_all_screens()
info = display.get_info()
json_info = display.toJSON()
print(json_info)

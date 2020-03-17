from displaymanagement.display import Display

display = Display(":1")
display.Screens[0].get_sizes()
info = display.get_info()
json_info = display.toJSON()
print(json_info)

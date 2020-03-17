from displaymanagement.display import Display

DISPLAY_ID = ":1"

# Load display
display = Display(DISPLAY_ID)

# Get display info
info = display.get_info()

# Alternatively, get it as json
json_info = display.toJSON()

print(json_info)

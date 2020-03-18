from displaymanagement.display import Display

# Load display
DISPLAY_ID = ":1"
display = Display(DISPLAY_ID)

# Get Default Screen
screen = display.Screens[0]

# Get all active output modes
outputs = screen.Outputs
for output in outputs.values():
    if output.Connected:
        # Print active output modes
        print(output.get_available_modes_info())

# WARMING: This will most likely disable your physical screen's output,
# if you accidentally do so, restart your display server
from displaymanagement.display import Display

# Load display
DISPLAY_ID = ":1"
display = Display(DISPLAY_ID)

# Get Default Screen
screen = display.Screens[0]

# Get an active output
outputs = screen.Outputs
for output in outputs.values():
    if output.Connected:
        # Disable all outputs
        output.disable()

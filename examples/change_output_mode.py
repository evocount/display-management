# WARNING: This will most likely change your screen resolution and refresh rate
from displaymanagement.display import Display
import random

# Load display
DISPLAY_ID = ":1"
display = Display(DISPLAY_ID)

# Get Default Screen
screen = display.Screens[0]

# Get an active output
outputs = screen.Outputs
for output in outputs.values():
    if output.Connected:
        modes = output.get_available_modes_info()
        # Get a random mode from the available ones
        mode = random.choice(modes)
        # Set the mode
        output.set_mode(mode.id)
        break

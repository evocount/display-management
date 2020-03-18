# WARNING: This will most likely change your screen position
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
        # Change the output position
        X = 0
        Y = 0
        output.set_position(X, Y)

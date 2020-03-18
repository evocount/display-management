# WARNING: This will most likely change your screen rotation
from displaymanagement.display import Display
from displaymanagement.rotation import Rotation

# Load display
DISPLAY_ID = ":1"
display = Display(DISPLAY_ID)

# Get Default Screen
screen = display.Screens[0]

# Get an active output
outputs = screen.Outputs
for output in outputs.values():
    if output.Connected:
        # Change the output rotation
        output.set_rotation(Rotation.ROTATE_180)
        # Bring it back
        output.set_rotation(Rotation.NO_ROTATION)

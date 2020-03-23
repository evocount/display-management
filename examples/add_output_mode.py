# WARNING: This will most likely change your screen resolution and refresh rate
from displaymanagement.display import Display

# Load display
DISPLAY_ID = ":1"
display = Display(DISPLAY_ID)

# Get Default Screen
screen = display.Screens[0]

# Create screen mode 1920x1080@60 non interlaced
mid = screen.create_mode("1920x1080T", 1920, 1080, 60.00, False)

# Add mode to outputs
outputs = screen.Outputs
for output in outputs.values():
    output.add_mode(mid)

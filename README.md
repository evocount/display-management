# Display Management

This library uses [python-xlib](https://github.com/python-xlib/python-xlib) to expose relevant functionality for managing the displays on EvoCount's PDMs.
For setting up the X server screen layout check the [Screen Setup](docs/SCREEN_SETUP.md) docs.

:warning: **WARNING** while xlib should be generally safe to use, some low level methods in principle can damage hardware.

- Never use low level state altering methods like modifying output props unless you know what you are doing.
- Don't assign invalid, unsupported modelines. Xlib should prevent you from doing so but it doesn't explicitly state that It prevents all possible mistakes.

## Table of Contents

- [Display Management](#display-management)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Terminology](#terminology)
  - [Architecture Summary](#architecture-summary)
  - [Library Design Summary](#library-design-summary)
  - [References](#references)
  - [Limitations, Issues and Possible Enhancements](#limitations-issues-and-possible-enhancements)

---

## Overview

This library is a wrapper for the python-xlib library. It is developed with the aim of providing an interface
for managing the X display server without exposing all the thorough details of the software and hardware architectures of the display server, video card, monitors, etc...

This Library uses `python-xlib`, `pydantic` and `pyedid`

---

## Terminology

_*The world of X follows an ambiguous and rather confusing set of terminologies, here you will find a list of some that are relevant for the library.*_

1. Display
   The term displays usually refers to an underlying X server instance. It is commonly referenced by the environment variable `DISPLAY`.

2. Window
   A self contained area on a screen that usually can be moved around and manipulated.

3. Screen
   A screen is an abstraction of a seamless viewable field. This means that, in a screen. all Windows can be moved around anywhere and all
   input devices can access the screen.
   Note that, a screen is NOT a physical screen, in fact a screen can be represented by multiple physical screens.
   Input devices can generally be used across multiple screens; however, windows belong to one screen.

4. Monitors
   A monitor is an abstraction used to represent a physical screen. In principle, each monitor belongs to a screen.

5. Output
   An output abstracts actual output ports on a display device such as HDMI, DVI or VGA ports.
   For some drivers, It is possible to configure Virtual display ports.

6. Modes & Modelines
   Modes are a configuration for the output describing things such as Resolution, Color Depth and Refresh Rate.
   [Modelines](https://en.wikipedia.org/wiki/XFree86_Modeline) are a standard format for describing modes.
   In general, modelines contain very low level information regarding format and each modeline differs depending on the hardware.
   For generating modelines, the command tool `cvt` can be used, for example `cvt 1920 1080 60` generates the modeline for \***\*1920x1080@60Hz\*\***
   Modelines are mostly automatically calculated by the X server for connected display devices.

7. Frambuffer
   In general, A portion of video RAM that has specific properties relevant from a graphics oriented memory perspective.

8. CRTC
   A legacy reference to [Cathode Ray Tubes](https://en.wikipedia.org/wiki/Cathode-ray_tube) that stuck. Very roughly, this corresponds to an in memory structure in the video device that is responsible for one output view, i.e.,
   whatever you see on your screen now is represented by a CRTC.
   Each video device has a limited set of CRTCs, this limit is the limit on how many distinct physical views it can support.

9. Xlib
   [Xlib](https://tronche.com/gui/x/xlib/) is a client library used to manipulate the X server.

10. Xrandr
    [X resize and rotate](https://www.x.org/releases/X11R7.5/doc/man/man1/xrandr.1.html) is an extension for Xlib
    and a command-line tool that displays info regarding the current configuration for a
    display server, e.g., Screens, outputs, modes, etc...
    It also allows manipulation of the screen configurations.

11. Multihead
    A [Multihead](https://wiki.archlinux.org/index.php/Multihead) setup may refer to one of 2 things.
    1. An X screen having more than 1 monitor attached
    2. Having multiple physical displays by configuring a multi Screen setup each with 1(or more) monitors

12. EDID
    An [Extended Display Identification Data](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data) is a data format used by a physical display to export its capabilities. It contains data such as manufacturer name, serial number, display sizem etc... .

13. PNP ID
    The [Plug and Play ID](https://en.wikipedia.org/wiki/Legacy_Plug_and_Play) is basically a 3 letter manufacturer ID of the physical display in the context of this library.
    A list of manufacturers can be found [here](https://uefi.org/pnp_id_list)
    Any monitor which exposes an EDID is a PnP monitor

---

## Architecture Summary

- X
   The high level overview of the X server is as follows

  - A display server has multiple screens
  - Each screen has multiple monitors
  - Windows can be dragged across monitors of one screen but not across different screens
  - In principle, Input Devices defined for a display server can be used across screens

- Xorg Config
   The [Xorg configuration](https://www.x.org/releases/current/doc/man/man5/xorg.conf.5.xhtml) defines the X server configuration in 4 main Sections

  1. _Server Layout:_ This is the root level section, it defines the general layout of the X server, the IO devices and configured Screens
  2. _Device:_ Defines a video device, e.g., a video card or a virtual display card that can be used
  3. _Monitor:_ Generally, corresponds to a physical output monitor
  4. _Screen:_ Corresponds to an X Screen. This section ties together outputs(graphics device defined by a Device section and a monitor defined by
      the monitor Section).

- XRandr
   The XRandr command-line tool follows the same structure as X except that randr abstracts away
   video devices and manages outputs directly, i.e., instead of setting the screen mode, you set the output mode

- Xlib with RandR extension
   Xlib contains no abstractions, for manipulating outputs you need to manipulate CRTCs directly and possibly connect outputs on the
   modified CRTCs

---

## Library Design Summary

This library follows a similar interface to the xrandr command-line tool. It exposes 3 main clases for manipulating the display.
This is a brief overview of them.

1. `Display`
   A wrapper for the display server that exposes the following methods and properties

   - _`init_display()`:_ Loads the display resources(Excludes loading associated screens).
   - _`get_screen_count()`:_ Returns the number of screens associated with this display.
   - _`load_screen()`:_ Loads the screen resources identified by the screen_identifier for this display.
   - _`load_all_screens()`:_ Loads all screens associated with this display.
   - _`get_info()`:_ Returns all relevant information about this display's loaded resources.
   - _`sync()`:_ Flushes X queue and waits until the server has processed all the queued requests.
   - _`Screens()`:_ Returns all loaded screens associated with this display.

2. `Screen`
   A wrappper for a screen that exposes the following methods and properties

   - _`get_sizes()`:_ Returns all possible sizes for this screen.
   - _`set_size(width, height, dpi, width_mm, height_mm)`:_ Sets the size of the screen.
   - _`adjust_size()`:_ Adjusts size of screen to fit outputs.
   - _`set_crtc_config(output, config)`:_ Sets crtc config on output while also adjusting screen size.
   - _`set_refresh_rate(rate)`:_ Sets the refresh rate of the screen.
   - _`get_info()`:_ Returns information about this screen's resources.
   - _`create_mode(name,width,height,refresh_rate,interlaced)`:_ Creates a new mode for the screen to be used by its outputs.
   - _`get_crtc_info(crtc_id)`:_ Returns crtc info for given id.
   - _`get_size_range()`:_ Returns the size range allowed for this screen.
   - _`Outputs`:_ Outputs associated with this screen.
   - _`CRTC_IDs`:_ CRTC IDs associated with the video device driving this screen.

3. `Output`
   A wrapper for an output in accordance with the xrandr command-line tool interface that exposes the following methods
   - _`get_available_modes_info()`:_ Returns info about all available modes for this screen.
   - _`set_mode(mode_id,crtc_id)`:_ Sets the mode of the output to the one referenced by the mode_id
   - _`set_position(x,y)`:_ Sets the position of the output.
   - _`set_rotation(rotation)`:_ Sets the rotation of the output.
   - _`set_config(crtc_id, mode_id, x, y, rotation)`:_ Sets crtc config of the output.
   - _`get_info()`:_ Returns all relevant information about this output's resources.
   - _`disable()`:_ Disables the output.
   - _`re_enable()`:_ If this output was connected before, connects to the last crtc_id it was connected to with the mode that it was connected with.
   - _`get_EDID()`:_ Gets the EDID info of the connected monitor to this output.
   - _`add_mode(mode_id)`:_ Adds a mode to the output.
   - _`has_edid()`:_ Checks if the output's connected monitor exposes an EDID property.
   - _`relative_place(self,output,orientation)`:_ Places the output in a location relative to another output.
   - _`complete_crtc_config(config)`:_ Returns crtc config where missing bits are filled with current config of this output.
   - _`Connected`:_ Whether the output is connected.
   - _`CRTC_ID`:_ CRTC ID this output is connectd to.
   - _`CRTC_Info`:_ CRTC info this output is connected to.
   - _`CRTC_Config`:_ Current CRTC config of this output.

- For an in-depth technical documentation check the docstrings
- In addition to the main Classes, the library exposes an Enum Class `Rotation` which contains predefined orientation values

---

## References

The X libs, tools and design are severly under documented, here you will find many links that you can use as reference.

- https://arachnoid.com/modelines/
- https://tronche.com/gui/x/xlib/
- https://www.x.org/releases/current/doc/man/man5/xorg.conf.5.xhtml
- https://wiki.archlinux.org/index.php/Multihead
- https://www.x.org/wiki/Development/Documentation/Multiseat/
- https://github.com/python-xlib
- https://github.com/python-xlib/python-xlib/blob/master/Xlib/ext/randr.py \*_Useful as the library is mostly not documented_\*
- https://gitlab.freedesktop.org/xorg/proto/xorgproto/-/raw/master/randrproto.txt
- http://www.rahul.net/kenton/xglossary.html
- http://python-xlib.sourceforge.net/doc/html/python-xlib_toc.html
- http://python-xlib.sourceforge.net/doc/html/python-xlib_8.html#SEC7 \*_Only reference for python-xlib exceptions till the time of writing this_\*
- https://wiki.archlinux.org/index.php/Xrandr
- https://xorg-team.pages.debian.net/xorg/howto/use-xrandr.html
- https://glenwing.github.io/docs/VESA-CVT-1.2.pdf

---

## Limitations, Issues and Possible Enhancements

- Currently this library follows the same interface as the xrandr command line tool.
  This does not allow setting multiple outputs for one CRTC, i.e., mirroring displays.

- Some not very important functions in the `Screen` class are broken, this is caused by either a misuse of the params of the python-xlib functions(Documentation issues?) or rather by a bug in the python-xlib function itself issuing malformed requests to the low level library beneath it. Either way, the functions' importance is not significant enough for investigating the real cause of the issue.

- python-xlib provides events to for handling state changes from outside source. Currently, these are not used and only events originating from this library is assumed. The three possible implementations for this are as follows.
  - Reload the entire state everytime (Easy and allows expanding the lib to handle events later on, but slowest)
  - Program every function to load the required state everytime (Slightly faster in principle, but, makes it very hard to modify or add new functionality later on)
  - Handle the events (Most efficient solution but would require the most additional work effort as well as potentially running into concurrency?)

- What the turn output off funtionality really does is that it turns off the CRTC associated with it.

- Creating modes for screens and adding them to outputs is a non persistent operation. For persistent configs use the xorg config files.

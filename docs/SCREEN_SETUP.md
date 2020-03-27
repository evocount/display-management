# Screen Setup

This is a small guide for setting up xorg screens. This document serves the purposes of providing references for configuring the X server screen layout
through configurations and highlighting the important parts in them.
X does not have functionality for setting up screens on the fly, but there are some extensions that may be of use.  

---

## DMX

The [Distributed Multihead X](https://www.x.org/releases/current/doc/man/man3/DMX.3.xhtml) extension is an X proxy server that allows adding screens dynamically.  
DMX can connect to multiple backend X servers and treat each one as a separate screen. A new screen can be attached using [DMXAddScreen](https://www.x.org/releases/current/doc/man/man3/DMXAddScreen.3.xhtml) though it is not clear from the wording of the docs whether the number of screens itself is fixed initially or not. In general, DMX can come in handy for serving the ultimate business goal of this project.

---

## Configuring Xorg

for thorough docs on how to configure xorg check the Manual [here](https://www.x.org/releases/current/doc/man/man5/xorg.conf.5.xhtml).  
As a side note, xorg doesn't require a config file and normally auto detects the devices and provides a default layout. a different config is required if a non trivial configuration is to be setup.

### Overview

The xorg config is defined in terms of sections, subsections, entries and options. Most important sections for this are __ServerLayout__, __Monitor__, __Screen__, __Device__ and maybe a little less relevant is the __Modes__ Section.

### Server Layout

This is the root section of a configuration. It combines multiple __Screens__, __InputDevices__ and other config options to provide a complete layout.

### Device

This section represents a video device. The most relevant config entries and options for this section are the following.  

- _`Identifier`(mandatory):_ Specifies the config specific ID of this device.
- _`Driver`(mandatory):_ Specifies the driver for this device.
- _`BusID`:_ specifies the hardware specific bus ID, usually PCI, in which the physical device is connected. This is useful when multiple devices are present.
- _`ScreenID`(important):_ This is useful when having multiple CRTCs and if multiple screens on the same device is required. A separate __Device__ Section is defined with each section having a different _ScreenID_ entry.  
Note: This was tested on virtual displays and it was found out that it does _NOT_ work. Maybe there are some undocumented limitations or a default option that prevents it. For verifying this, please use actual multiple physical displays and check the _ZaphodHeads_ option(more on that in the notes).
- _`Option "Monitor-outputname" "monitorsection"`_: In line with the design of RandR, this ties a monitor to a specific output of the device.

### Monitor

This section defines a physical monitor. The only relevant entry for this section is the config specific _`Identifier`_ entry.

### Screen

This section couples together a __Device__ and a __Monitor__ to be used in the layout. The relevant config entries are the following.

- _`Identifier`(mandatory):_ Specifies the config specfic ID of this screen.
- _`Device`(mandatory):_ Specifies the device to be used for this screen.
- _`Monitor`:_ Specifies the monitor to be used for this screen.

### Modes

This is a not-so-important section which can provide some modes independent of the screens.

---

## Notes

- In the old times, video devices did not provide multi head support and the standard setup was a one screen, one card and one monitor setup. A multi-head based on one head per screen aka __Zaphod Mode__, or a multi-head based on multiple monitors on one screen as supported by randr can be setup.
- There are some undocumented options in the xorg config like the ZaphodHeads option.
- Generally, a possible approach could setting up the layout of screens initially, then manipulating the outputs dynamically through randr.
- DMX is not part of the list of implemented extensions in __python-xlib__.
- DMX remains a possible option but all of the proposed options would preferably require testing on an actual physical displays.
- For setting up virtual devices the _xf86-video-dummy_ driver can be used to setup a virtual screen.

---

## Additional References

- https://nouveau.freedesktop.org/wiki/MultiMonitorDesktop/
- https://wiki.archlinux.org/index.php/Multihead
- https://wiki.archlinux.org/index.php/Xorg

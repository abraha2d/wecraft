# wecraft

An [Inkcut](https://www.codelv.com/projects/inkcut/) plugin for the
[Craftwell eCraft](https://craftwellusa.com/ecraft/).

## Usage

In the same environment that Inkcut is installed in, run `pip install wecraft`.
Inkcut should automatically detect the plugin the next time you open it.

Under "Device" > "Setup...", add a new device, then select the "eCraft" driver.
\Make sure that the correct serial port (most likely labelled CP2102) is
selected under the "Connection" tab, and that the baudrate is set to 115200. 

> Note: This plugin is hardcoded to load material from the tray.

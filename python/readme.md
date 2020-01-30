# Python Scripts

## `nxos-cdp-brief.py`

Script to run *on* an NX-OS device to print a custom CDP neighbor brief table. 
One line is printed per CDP neighbor, containing the following information; 
**Local interface**, **Neighbor hostname**, **interface**, **IP address** (mgmt preferred), and **version***.

> * **Version** may have some regex parsing issues, has only been validated against most Cisco equipment and some ESXi builds.

![cdp-brief-screenshot](../assets/nxos-cdp-brief.png)

### Usage

1. Enable guestshell on the NX-OS device (optional).
2. Install the natsort python module via guestshell (optional);
   - `sudo chvrf management pip install natsort`
3. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
4. Create a command alias on NX-OS CLI;
   - With guestshell: `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
   - Without guestshell: `cli alias name cdpbr python /bootflash/scripts/nxos-cdp-brief.py`
5. Type `cdpbr` in NX-OS CLI to output a useful CDP brief table.
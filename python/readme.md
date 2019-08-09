# Python Scripts

## `nxos-cdp-brief.py`

Script to run *on* an NX-OS device to print a custom CDP neighbor brief table. 
One line is printed per CDP neighbor, containing the following information; 
**Local interface**, **Neighbor hostname**, **interface**, and **IP address** (mgmt preferred).

![cdp-brief-screenshot](../assets/nxos-cdp-brief.png)

### Usage

1. Enable guestshell on the NX-OS device.
2. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
3. Create a command alias on NX-OS CLI;
   - `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
4. Type `cdpbr` in NX-OS CLI to output a useful CDP brief table.
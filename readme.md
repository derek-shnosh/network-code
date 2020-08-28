[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/derek-shnosh/network-code)

# Misc Code

Miscellaneous code primarily used in my role as a network engineer.

# Python Scripts

## `nxos-cdp-brief.py`

Script to run *on* an NX-OS device to print a custom CDP neighbor brief table. 
One line is printed per CDP neighbor, containing the following information; 
**Local interface**, **Neighbor hostname**, **interface**, **IP address** (mgmt preferred), **platform**, and **version***.

_*Use the args `-p` or `-v` to print the CDP table **with** platform or version information, respectively. There may be some regex parsing issues, has only been validated against most Cisco equipment and some ESXi builds._

![cdp-brief-screenshot](assets/nxos-cdp-brief.png)

### Usage

1. Enable guestshell on the NX-OS device (optional).
2. Install the natsort python module via guestshell (optional);
   - `sudo chvrf management pip install natsort`
3. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
4. Create a command alias on NX-OS CLI;
   - With guestshell: `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
   - Without guestshell: `cli alias name cdpbr python /bootflash/scripts/nxos-cdp-brief.py`
5. Type `cdpbr` in NX-OS CLI to output a useful CDP brief table.
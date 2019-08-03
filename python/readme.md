# Python Scripts

## `nxos-cdp-brief.py`

![cdp-brief-screenshot](../assets/nxos-cdp-brief.png)

1. Make sure guestshell is enabled on the NX-OS device.
2. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
3. Create a command alias on NX-OS CLI;
   `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
4. Typing `cdpbr` in NX-OS CLI will how print a useful CDP brief table.
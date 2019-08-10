#!/bin/env python
# Author: DS, Synergy Information Solutions, Inc.

# 1. Enable guestshell on the NX-OS device.
# 2. Install the natsort python module via guestshell;
#    - `sudo chvrf management pip install natsort`
# 3. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
# 4. Create a command alias on NX-OS CLI;
#    - `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
# 5. Type `cdpbr` in NX-OS CLI to output a useful CDP brief table.

import json
import re
from cli import clid
from natsort import natsorted

cdp_dict = {}
i = 0

cdp = json.loads(clid('show cdp neighbor detail'))[
    'TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']

for entry in cdp:
    i += 1
    interface = entry['intf_id']
    cdp_dict[interface, i] = {}

    # Strip fat from local interface, add to dict.
    local_intf = re.sub(r'(Eth|mgmt)[^\d]*([\d/]+)', r'\1\2', entry['intf_id'])
    cdp_dict[interface, i]['local_intf'] = local_intf

    # Strip fat from neighbor hostname, add to dict.
    neighbor = re.split(r'[\.(]', entry['device_id'])[0]
    cdp_dict[interface, i]['neighbor'] = neighbor

    # Strip fat from neighbor interface, add to dict.
    neighbor_intf = re.sub(r'^(.{3})[^\d]*([\d/]+)', r'\1 \2', entry['port_id'])
    cdp_dict[interface, i]['neighbor_intf'] = neighbor_intf

    # Add neighbor IP address to dict.
    try:
        neighbor_ip = entry['v4mgmtaddr']
    except:
        try:
            neighbor_ip = entry['v4addr']
        except:
            pass
    if neighbor_ip == '0.0.0.0' or neighbor_ip == '':
        cdp_dict[interface, i]['neighbor_ip'] = '--'
    else:
        cdp_dict[interface, i]['neighbor_ip'] = neighbor_ip

# Print header and custom CDP neighbor brief table.
print('''CDP brief prints useful CDP neighbor information.

* Use `| grep` to filter output.

'L-Intf' denotes local interface.
'N-Intf' denotes neighbor interface.

%-8s -> %-20s %-12s %s\n%s''' % ('L-Intf', 'Neighbor', 'N-Intf', 'IP Address', '-'*60))

for key, value in natsorted(cdp_dict.items()):
    print('%-8s -> %-20s %-12s %s' %
          (value['local_intf'], value['neighbor'], value['neighbor_intf'], value['neighbor_ip']))

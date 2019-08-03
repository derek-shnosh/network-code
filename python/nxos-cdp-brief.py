#!/bin/env python
# Author: DS, Synergy Information Solutions, Inc.

# 1. Make sure guestshell is enabled on the NX-OS device.
# 2. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
# 3. Create a command alias on NX-OS CLI;
#    - `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
# 4. Typing `cdpbr` in NX-OS CLI will print a useful CDP brief table.

import cli
import json
import re
import natsort

cdp_dict = {}
i = 0

cdp = json.loads(cli.clid('show cdp neighbor detail'))[
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

'L-Intf' denotes local interface.
'N-Intf' denotes neighbor interface.

%-8s -> %-20s %-12s %s\n%s''' % ('L-Intf', 'Neighbor', 'N-Intf', 'IP Address', '-'*60))

for key, value in natsort.natsorted(cdp_dict.items()):
    print('%-8s -> %-20s %-12s %s' %
          (value['local_intf'], value['neighbor'], value['neighbor_intf'], value['neighbor_ip']))

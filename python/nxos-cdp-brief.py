#!/bin/env python
# Author: DS, Synergy Information Solutions, Inc.

# 1. Enable guestshell on the NX-OS device.
# 2. Install the natsort python module via guestshell;
#    - `sudo chvrf management pip install natsort`
# 3. Copy this script to bootflash:/scripts/nxos-cdp-brief.py
# 4. Create a command alias on NX-OS CLI;
#    - With guestshell: `cli alias name cdpbr guestshell run python /bootflash/scripts/nxos-cdp-brief.py`
#    - Without guestshell: `cli alias name cdpbr python /bootflash/scripts/nxos-cdp-brief.py`
# 5. Type `cdpbr` in NX-OS CLI to output a useful CDP brief table.

import argparse
import json
import re
from cli import clid

parser = argparse.ArgumentParser('NXOS CDP Brief.')
parser.add_argument(
    '-v', '--version', action='store_true', help='Include neighbor version in printout.')
args = parser.parse_args()

try:
    from natsort import natsorted
    natsorted_avail = True
except ImportError:
    natsorted_avail = False

# Check for CDP neighbors.
try:
    return_data = json.loads(clid('show cdp neighbor detail'))[
        'TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']
except:
    print('No CDP neighbors found.')
    exit()

cdp = []
# If more than one neighbor exists, a dict is built; otherwise a list is made.
if isinstance(return_data, dict):
    cdp.append(return_data)
elif isinstance(return_data, list):
    for item in return_data:
        cdp.append(item)

i = 0
cdp_dict = {}
# Parse information from each CDP neighbor.
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
    # Strip fat from neighor version, add to dict.
    version = entry['version']
    if 'CCM' in version:
        neighbor_ver = re.sub(r'.*?CCM:(.*)', r'\1', version)
    else:
        neighbor_ver = re.sub(r'.*?version:* ([^ ,\n]*).*', r'\1', version, flags=re.DOTALL|re.IGNORECASE)
    cdp_dict[interface, i]['neighbor_ver'] = neighbor_ver
    # Add neighbor IP address(es) to dict.
    try:
        mgmtaddr = entry['v4mgmtaddr']
    except:
        mgmtaddr = None
    try:
        addr = entry['v4addr']
        if addr == mgmtaddr:
            addr = '(--)'
        elif addr == '0.0.0.0':
            addr = '--'
    except:
        addr = None
    cdp_dict[interface, i]['neighbor_mgmtaddr'] = mgmtaddr or '--'
    cdp_dict[interface, i]['neighbor_addr'] = addr or '--'


# Print header and custom CDP neighbor brief table.
print('''CDP brief prints useful CDP neighbor information.

Neighbors parsed: %s

* Use `grep` to filter output (N9K only).
'L-Intf' denotes local interface.
'N-Intf' denotes neighbor interface.\n\n''' % i)

if args.version:
    print('%-8s -> %-20s %-14s %-16s %-16s %s\n%s' %
        ('L-Intf', 'Neighbor', 'N-Intf', 'Mgmt-IPv4-Addr', 'IPv4-Addr', 'Version', '-'*95))

    if natsorted_avail:
        for key, value in natsorted(cdp_dict.items()):
            print('%-8s -> %-20s %-14s %-16s %-16s %s' %
                (value['local_intf'],
                value['neighbor'],
                value['neighbor_intf'],
                value['neighbor_mgmtaddr'],
                value['neighbor_addr'],
                value['neighbor_ver']))
    else:
        sorted_neighbors = sorted(cdp_dict.keys())
        for nei in sorted_neighbors:
            print('%-8s -> %-20s %-14s %-16s %-16s %s' %
                (cdp_dict[nei]['local_intf'],
                cdp_dict[nei]['neighbor'],
                cdp_dict[nei]['neighbor_intf'],
                cdp_dict[nei]['neighbor_mgmtaddr'],
                cdp_dict[nei]['neighbor_addr'],
                cdp_dict[nei]['neighbor_ver']))
else:
    print('%-8s -> %-20s %-14s %-16s %-16s\n%s' %
        ('L-Intf', 'Neighbor', 'N-Intf', 'Mgmt-IPv4-Addr', 'IPv4-Addr', '-'*80))

    if natsorted_avail:
        for key, value in natsorted(cdp_dict.items()):
            print('%-8s -> %-20s %-14s %-16s %-16s' %
                (value['local_intf'],
                value['neighbor'],
                value['neighbor_intf'],
                value['neighbor_mgmtaddr'],
                value['neighbor_addr']))
    else:
        sorted_neighbors = sorted(cdp_dict.keys())
        for nei in sorted_neighbors:
            print('%-8s -> %-20s %-14s %-16s %-16s' %
                (cdp_dict[nei]['local_intf'],
                cdp_dict[nei]['neighbor'],
                cdp_dict[nei]['neighbor_intf'],
                cdp_dict[nei]['neighbor_mgmtaddr'],
                cdp_dict[nei]['neighbor_addr']))

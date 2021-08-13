#!/bin/env python
# Author: DS, shnosh.io

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

parser = argparse.ArgumentParser(
    '\n\nNXOS CDP Brief.', description='Using -p and -v args simultaneously requires extra terminal width; try "terminal width 511".')
parser.add_argument(
    '-v', '--version', action='store_true', help='Include neighbor version in printout.',)
parser.add_argument(
    '-p', '--platform', action='store_true', help='Include neighbor platform in printout.')
args = parser.parse_args()
include_ver = args.version
include_plat = args.platform

try:
    from natsort import natsorted
    natsorted_avail = True
except ImportError:
    natsorted_avail = False

# Check for CDP neighbors.
try:
    return_data = clid('show cdp neighbor detail')
    json_data = json.loads(return_data)[
        'TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']
except:
    print('No CDP neighbors found.')
    exit()

cdp = []
# If more than one neighbor exists, a dict is built; otherwise a list is made.
if isinstance(json_data, dict):
    cdp.append(json_data)
elif isinstance(json_data, list):
    for item in json_data:
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
    if include_ver:
        if 'CCM' in entry['version']:
            neighbor_ver = re.sub(r'.*?CCM:([^ ,\n]*)', r'\1', entry['version'])
        else:
            neighbor_ver = re.sub(
                r'.*?version:* ([^ ,\n]*).*', r'\1', entry['version'], flags=re.DOTALL | re.IGNORECASE)
        cdp_dict[interface, i]['neighbor_ver'] = neighbor_ver
    # Get neighbor platform, add to dict.
    if include_plat:
        neighbor_plat = re.sub(r'^cisco\s', '', entry['platform_id'], flags=re.IGNORECASE)
        cdp_dict[interface, i]['neighbor_plat'] = neighbor_plat
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

-v will include neighbor version information.
-p will include neighbor platform information.

* Use `grep` to filter output (N9K only).

Neighbors parsed: %s

'L-Intf' denotes local interface.
'N-Intf' denotes neighbor interface.\n\n''' % i)

row_format = '%-8s -> %-22s %-14s %-16s %-16s'
header_row = ('L-Intf', 'Neighbor', 'N-Intf', 'Mgmt-IPv4-Addr', 'IPv4-Addr')
if include_plat and include_ver:
    row_format = row_format + ' %-20s %-20s'
    header_row = header_row + ('Platform', 'Version')
    dash_count = 115
elif include_plat and not include_ver:
    row_format = row_format + ' %-20s'
    header_row = header_row + ('Platform',)
    dash_count = 95
elif include_ver and not include_plat:
    row_format = row_format + ' %-20s'
    header_row = header_row + ('Version',)
    dash_count = 95
else:
    dash_count = 80

print(row_format % header_row)
print('-'*dash_count)

if natsorted_avail:
    sorted_neighbors = natsorted(cdp_dict.items())
else:
    sorted_neighbors = sorted(cdp_dict.items())    

for key, value in sorted_neighbors:
    curr_nei = (value['local_intf'],
                value['neighbor'],
                value['neighbor_intf'],
                value['neighbor_mgmtaddr'],
                value['neighbor_addr'])
    if include_plat and include_ver:
        curr_nei = curr_nei + (value['neighbor_plat'], value['neighbor_ver'])
    elif include_plat and not include_ver:
        curr_nei = curr_nei + (value['neighbor_plat'],)
    elif include_ver and not include_plat:
        curr_nei = curr_nei + (value['neighbor_ver'],)
    print(row_format % curr_nei)

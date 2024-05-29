#!/bin/env python
# Author: DS, shnosh.io

import argparse
import cli
import json
import re

parser = argparse.ArgumentParser('NXOS CDP description toolbox.')
parser.add_argument(
    '-i', '--interface', help='"e#/#", or "all" for all interfaces')
args = parser.parse_args()
intf = args.interface

# Accommodate Python2 on older guestshells.
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

if intf == 'all':
    # Keyboard interrupt handler source: https://stackoverflow.com/a/1112350
    import signal
    import sys

    def signal_handler(sig, frame):
        print(' - Keyboard interrupt.')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause

    print('Checking all interfaces for CDP neighbors, press `ctrl+c` to interrupt.')

    # Load all CDP neighbor information.
    try:
        return_data = json.loads(cli.clid('show cdp neighbor detail'))[
            'TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']
    except:
        print('No CDP neighbors found.')
        exit()

    # If more than one neighbor exists, a dict is built; otherwise a list is made.
    cdp = []
    if isinstance(return_data, dict):
        cdp.append(return_data)
    elif isinstance(return_data, list):
        for item in return_data:
            cdp.append(item)

    # Parse information from each CDP neighbor.
    i = 0
    cdp_dict = {}
    updated = {}
    for entry in cdp:
        i += 1
        interface = entry['intf_id']
        curr_desc = cli.cli('show run interf %s | inc desc' % interface)
        if 'description' in curr_desc:
            curr_desc = re.split(r'description (\S*)', curr_desc)[1]
        else:
            curr_desc = '<none>'
        # Strip fat from neighbor hostname, add to dict.
        neighbor = re.split(r'[\.(]', entry['device_id'])[0]
        # Strip fat from neighbor interface, add to dict.
        neighbor_intf = entry['port_id']
        if "Ethernet" in neighbor_intf:
            neighbor_intf = re.sub(r"\D+(.*)$", r'\1', neighbor_intf)
        else:
            neighbor_intf = re.sub(r'^(.{3})[^\d]*([\d/]+)', r'\1\2', neighbor_intf)
        new_desc = '%s:%s' % (neighbor, neighbor_intf)

        # Prompt to set the local interface's description, if needed.
        if curr_desc == new_desc:
            print('Interface %s description already matches CDP neighbor (%s).' %
                  (interface, curr_desc))
        else:
            q = input('Update description on %s to "%s" (Currently: "%s")?  [y/n] ' % (
                interface, new_desc, curr_desc))
            if q == 'y':
                cli.cli('conf t ; interface %s ; description %s' %
                        (interface, new_desc))

else:
    # Check for valid interface.
    try:
        check_intf = cli.cli('show inter %s' % intf)
    except:
        print('"%s" is not a valid interface.' % intf)
        quit()

    # Run CDP neighbor command, strip whitespace.
    cdp = cli.cli('show cdp nei int %s det' % intf)
    cdp = cdp.replace(' ', '')

    # Get the neighbor and neighbor interface.
    if 'Device' in cdp:
        nei = re.split(r'DeviceID:([^\.\(\n]+)', cdp)[1]
        nei_intf = re.split(r'PortID\(outgoingport\)\:\D+(.*)', cdp)[1]
        if nei_intf == '0':
            nei_intf = 'mgmt'
        new_desc = '%s:%s' % (nei, nei_intf)
    else:
        print('No CDP neighbor found on %s.' % intf)
        quit()

    # Get local interface's current description.
    curr_desc = cli.cli('show run interf %s | inc desc' % intf)
    if 'description' in curr_desc:
        curr_desc = re.split(r'description\ *(.*)', curr_desc)[1]
    else:
        curr_desc = '<none>'

    # Set local interface's description, if needed.
    if new_desc == curr_desc:
        print('CDP neighbor on %s (%s), description does not require updating.' % (
            intf, new_desc))
    else:
        print('CDP neighbor on %s (%s), updating description (was: %s).' %
              (intf, new_desc, curr_desc))
        cli.cli('conf t ; int %s ; desc %s' % (intf, new_desc))

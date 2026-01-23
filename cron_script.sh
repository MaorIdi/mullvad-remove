#!/bin/sh
# This script runs the cleaner every 1 second using the python script's internal loop
echo "Starting Mullvad Device Cleaner..."
exec python3 -u mullvad_device_cleaner.py --apply --interval 1

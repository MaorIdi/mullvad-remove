#!/bin/sh
# This script runs the cleaner every 30 seconds using the python script's internal loop
echo "Starting Mullvad Device Cleaner Cron..."
exec python3 -u mullvad_device_cleaner.py --apply --interval 30

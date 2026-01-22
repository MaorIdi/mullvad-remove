# Mullvad Device Cleaner

Automatically removes unauthorized devices from your Mullvad VPN account by maintaining an allowlist of trusted devices. This tool helps you keep your account clean and secure by periodically checking and removing any devices that are not on your approved list.

## Features

- 🔒 **Security First**: Automatically removes unauthorized devices from your Mullvad account
- ✅ **Allowlist-based**: Only devices you explicitly approve are kept
- 🔄 **Continuous Monitoring**: Can run periodically to ensure ongoing protection
- 🐳 **Docker Ready**: Includes Docker setup for easy deployment
- 🔍 **Dry-run Mode**: Test before making changes

## Prerequisites

- Python 3.6+
- Mullvad VPN account number
- `requests` library (installed automatically)

## Quick Start

### Local Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd mullvad
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Mullvad account number**

   ```bash
   export MULLVAD_ACCOUNT_NUMBER="your-account-number-here"
   ```

4. **Create your allowed devices list** (see [Managing Allowed Devices](#managing-allowed-devices))

5. **Run a dry-run first** (recommended)

   ```bash
   python mullvad_device_cleaner.py
   ```

6. **Apply changes**
   ```bash
   python mullvad_device_cleaner.py --apply
   ```

### Docker Setup

1. **Create a `.env` file** with your account number:

   ```bash
   echo "MULLVAD_ACCOUNT_NUMBER=your-account-number-here" > .env
   ```

2. **Build and run**
   ```bash
   docker-compose up -d
   ```

The container will automatically run the cleaner every 30 seconds.

## Managing Allowed Devices

### How to Add Allowed Devices

The `allowed_devices.txt` file contains the names of devices you want to keep on your Mullvad account. Each device name should be on its own line.

#### Steps to Add a Device:

1. **Find your device name** in the Mullvad app or by running:

   ```bash
   python mullvad_device_cleaner.py
   ```

   This will list all current devices on your account.

2. **Open** `allowed_devices.txt` in a text editor

3. **Add the device name** on a new line. Device names are case-insensitive and typically follow the format `adjective-animal` (e.g., `happy-lion`, `calm-otter`)

4. **Save the file**

#### Example `allowed_devices.txt`:

```text
happy-lion
calm-otter
brave-tiger
wise-elephant
```

#### Important Notes:

- ✏️ **One device name per line**
- 🔤 **Case-insensitive**: `Happy-Lion` and `happy-lion` are treated the same
- 💬 **Comments**: Lines starting with `#` are ignored
- 🚫 **Empty lines**: Blank lines are ignored
- 📝 **Exact match**: Make sure to use the exact device name as shown in Mullvad

#### Finding Device Names:

You can find your device names by:

1. Opening the Mullvad VPN app and checking the device name
2. Running the script in dry-run mode (it lists all devices)
3. Logging into your Mullvad account on their website

### Updating the Allowlist

**For Local Setup:**
Simply edit `allowed_devices.txt` and save. The changes will take effect on the next run.

**For Docker Setup:**
Edit `allowed_devices.txt` on your host machine. Since it's mounted as a volume, changes are immediate—no need to rebuild or restart the container.

## Usage

### Command Line Options

```bash
python mullvad_device_cleaner.py [OPTIONS]
```

**Options:**

- `--allowlist <path>`: Path to allowlist file (default: `allowed_devices.txt`)
- `--apply`: Actually remove non-allowlisted devices (without this, it's a dry-run)
- `--interval <seconds>`: Repeat every N seconds (0 = run once, default: 0)

### Examples

**Dry-run (preview what would be removed):**

```bash
python mullvad_device_cleaner.py
```

**Remove unauthorized devices once:**

```bash
python mullvad_device_cleaner.py --apply
```

**Run continuously (check every 5 minutes):**

```bash
python mullvad_device_cleaner.py --apply --interval 300
```

**Use a custom allowlist file:**

```bash
python mullvad_device_cleaner.py --allowlist /path/to/my-devices.txt --apply
```

## How It Works

1. **Authentication**: The script authenticates with Mullvad's API using your account number
2. **Device Retrieval**: Fetches all devices currently registered to your account
3. **Comparison**: Compares the device list against your `allowed_devices.txt`
4. **Action**: In `--apply` mode, removes any devices not in the allowlist
5. **Repeat**: If `--interval` is specified, waits and repeats the process

## Docker Configuration

The included `docker-compose.yml` sets up the cleaner to run continuously every 30 seconds. The configuration:

- Automatically restarts if it crashes
- Uses your `.env` file for the account number
- Mounts `allowed_devices.txt` as a volume for easy updates
- Runs the script with `--apply --interval 30`

To modify the check interval, edit `cron_script.sh` and change the `--interval` value.

## Security Considerations

- 🔑 **Account Number**: Keep your `MULLVAD_ACCOUNT_NUMBER` secret
- 📁 **Git**: Add `.env` to `.gitignore` to avoid committing secrets
- ⚠️ **Dry-run First**: Always test with dry-run before using `--apply`
- 🔒 **Allowlist**: Keep your `allowed_devices.txt` backed up

## Troubleshooting

**Error: "Set MULLVAD_ACCOUNT_NUMBER in your environment"**

- Make sure you've exported the environment variable or created a `.env` file for Docker

**Error: "Allowlist file 'allowed_devices.txt' not found"**

- Create the file with at least one device name

**Error: "Token request failed"**

- Check that your account number is correct
- Verify your internet connection

**Devices keep coming back:**

- Make sure you're running with `--apply` flag
- Check that the device names in `allowed_devices.txt` match exactly

## License

This project is provided as-is for personal use with your Mullvad VPN account.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by Mullvad VPN. Use at your own risk.

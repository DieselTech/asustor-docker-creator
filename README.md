# ASUSTOR Docker Upgrade Script

This Python script automates the process of upgrading the Docker version in an ASUSTOR NAS `.apk` package. It downloads the latest Docker binaries, updates the binaries and version in the original `.apk`, preserves helper files, and notifies you via a Discord webhook when a new `.apk` is created.

## Features

- **Fetches Latest Docker Version**: Scrapes Docker’s download page to find the latest stable release (e.g., `docker-28.0.4.tgz`).
- **Version Check**: Compares the current `.apk` version with the latest Docker version to avoid redundant processing.
- **Updates APK**:
  - Updates the `general.version` in `config.json` (inside `control.tar.gz`).
  - Replaces Docker binaries in `data.tar.gz`’s `bin` directory while preserving other helper files.
  - Creates a new `.apk` named `docker_$VERSION.apk` (e.g., `docker_28.0.4.apk`).
- **Discord Notification**: Sends a message to a Discord webhook when a new `.apk` is generated, including version and file details.
- **Cross-Platform**: Works on Windows and Linux.

## Requirements

- **Python 3.6+**: Installed on your system.
- **Python Library**: `requests` (install via `pip install requests`).
- **Original APK**: An ASUSTOR Docker `.apk` file. You can download this directly from Asustor's site (https://appdownload.asustor.com/0010_999_1732245556_docker-ce_25.0.5.r1_x86-64.apk) then name it `original_docker.apk` and keep it in the scripts root folder. 
- **Internet Access**: To download Docker binaries and send Discord notifications.
- **Discord Webhook** (optional): For notifications when a new `.apk` is created.

## Setup

1. **Save the Script**:
   - Place `upgrade_docker_asustor.py` in a directory (e.g., `/path/to/docker_upgrade/`).

2. **Place Original APK**:
   - Copy your ASUSTOR Docker `.apk` to the script’s directory and name it `original_docker.apk`.
   - Alternatively, edit `ORIGINAL_APK` in the script to point to your `.apk` path:
     ```python
     ORIGINAL_APK = Path("/path/to/your/docker.apk")

3. **Install Dependencies**:
   - Install the `requests` library:
     ```bash
     pip install requests
     ```

4. **Set Discord Webhook (Optional)**:
   - Create a webhook in your Discord server (Channel → Edit → Integrations → Create Webhook).
   - Copy the webhook URL and update `DISCORD_WEBHOOK_URL` in the script:
     ```python
     DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"
     ```
   - If unset, notifications are skipped.

5. **Make Executable (Linux)**:
   - On Linux, make the script executable:
     ```bash
     chmod +x upgrade_docker_asustor.py
     ```

## Usage

### Testing (Windows or Linux)

1. **What Happens**:
   - Checks the `general.version` in `original_docker.apk`’s `config.json`.
   - Compares it with the latest Docker version from `https://download.docker.com/linux/static/stable/x86_64/`.
   - If versions match, exits with a message (e.g., “No update needed: APK version (28.0.4) matches latest Docker version (28.0.4).”).
   - If a new version is found:
     - Downloads the latest `docker-$VERSION.tgz`.
     - Updates `config.json`’s `general.version`.
     - Replaces Docker binaries in `data/bin`, preserving helper files.
     - Creates `docker_$VERSION.apk` (e.g., `docker_28.0.4.apk`) in the script’s directory.
     - Sends a Discord notification (if webhook is set).

2. **Verify Output**:
   - Open `docker_$VERSION.apk` with a zip tool.
   - Check:
     - `control.tar.gz` → `config.json`: `general.version` matches the new version.
     - `data.tar.gz` → `bin`: Contains updated Docker binaries and original helper files.

### Automation (Linux)

1. **Schedule with Cron**:
   - Add the script to cron for periodic checks (e.g., daily at midnight):
     ```bash
     crontab -e
     0 0 * * * /path/to/upgrade_docker_asustor.py
     ```
   - Ensure Python 3 and `requests` are available in the cron environment.

2. **Monitor Notifications**:
   - When a new `.apk` is created, you’ll receive a Discord message with the version, filename, and path.
   - Manually grab the `.apk` (e.g., `docker_28.0.4.apk`) and install it on your ASUSTOR NAS via ADM (App Central → Manual Install).

## Notes

- **Architecture**: Assumes `x86_64` for Docker binaries. For ARM-based NAS, update `DOCKER_BASE_URL`:
  ```python
  DOCKER_BASE_URL = "https://download.docker.com/linux/static/stable/aarch64/"
  ```
- **Helper Files**: Non-Docker files in `data/bin` are preserved, assuming they have unique names.
- **Webhook Security**: Keep your Discord webhook URL private.
- **Testing**: Test manually before automating to ensure the output `.apk` works on your NAS.
- **Version Check**: Skips processing if `original_docker.apk`’s version matches the latest Docker release.

## Troubleshooting

- **“Original APK file not found”**:
  - Ensure `original_docker.apk` is in the script’s directory or update `ORIGINAL_APK`.
- **“Failed to send Discord notification”**:
  - Verify `DISCORD_WEBHOOK_URL` is correct and your system has internet access.
- **Output `.apk` Missing Files**:
  - Check logs for errors and verify `original_docker.apk`’s structure (`control.tar.gz`, `data.tar.gz`).
- **Cron Issues**:
  - Use full paths in cron (e.g., `/usr/bin/python3 /path/to/upgrade_docker_asustor.py`).
  - Ensure permissions allow writing to the script’s directory.
```
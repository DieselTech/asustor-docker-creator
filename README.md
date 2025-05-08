# ASUSTOR Docker Upgrade Script

This Python script automates the process of upgrading the Docker version in an ASUSTOR NAS `.apk` package. It downloads the latest Docker binaries, replaces the binaries and version in the original `.apk`, preserves helper files, and notifies you via a Discord webhook when a new `.apk` is created.
It does not automate the installation of the APK on your NAS. That part still needs to be done manually. For obvious reasons, I don't want that aspect automated right now. 

## Features

- **Fetches Latest Docker Version**: Scrapes Docker’s download page to find the latest stable release (e.g., `docker-28.0.4.tgz`).
- **Version Check**: Compares the current `.apk` version with the latest Docker version to avoid redundant processing.
- **Updates APK**:
  - Updates the `general.version` in `config.json` (inside `control.tar.gz`).
  - Replaces Docker binaries in `data.tar.gz`’s `bin` directory while preserving other helper files.
  - Creates a new `.apk` named `docker_$VERSION.apk` (e.g., `docker_28.0.4.apk`).
- **Discord Notification**: Sends a message to a Discord webhook when a new `.apk` is generated, including version and file details.

## Requirements

- **Python 3.6+** - I think? Probably works on older versions since it is fairly basic. The version of Python3 that ADM has in the store is 3.10.11 and there is no issues running this script directly from there. 
- **Python Library**: `requests` (install via `pip install requests`).
- **Original APK**: An ASUSTOR Docker `.apk` file. You can download this directly from Asustor's site (https://appdownload.asustor.com/0010_999_1732245556_docker-ce_25.0.5.r1_x86-64.apk) then name it `original_docker.apk` and keep it in the scripts root folder. 
- **Discord Webhook** (optional): For notifications when a new `.apk` is created.

## Usage

1. **Save the Script**:
   - Place `upgrade_docker_asustor.py` in a directory (e.g., `/path/to/asustor_docker_creator/`).

2. **Place Original APK**:
   - Copy your ASUSTOR Docker `.apk` to the script’s directory and name it `original_docker.apk`.
   - Alternatively, edit `ORIGINAL_APK` in the script to point to your `.apk` path:
     ```python
     ORIGINAL_APK = Path("/path/to/asustor_docker_creator/original_docker.apk")
	 ```

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
     chmod +x main.py
     ```

### Automation (Linux)

1. **Schedule with Cron**:
   - Add the script to cron for periodic checks. If your running directly on the NAS you need to call `python3` directly like in the example below. 	 
	 ```bash
     crontab -e
     0 4 */5 * * /usr/local/bin/python3 /volume1/path/to/scripts/asustor_docker_creator/main.py
     ```
   - The above cron is to run at 0400 every 5 days. I try to be a good internet citizen and not hammer their servers constantly for something that doesn't have a frequent release.

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

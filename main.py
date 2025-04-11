#!/usr/bin/env python3

import os
import shutil
import requests
import re
import zipfile
import tarfile
import json
from pathlib import Path

# Base URL for Docker stable releases (x86_64)
DOCKER_BASE_URL = "https://download.docker.com/linux/static/stable/x86_64/"

# Hardcoded path to original APK (relative to script directory)
ORIGINAL_APK = Path(__file__).parent / "original_docker.apk"

# Discord webhook URL (replace with your actual webhook URL)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"

def get_latest_docker_version():
    """Fetch the latest Docker version from the directory listing."""
    print(f"Fetching latest Docker version from {DOCKER_BASE_URL}...")
    response = requests.get(DOCKER_BASE_URL)
    response.raise_for_status()
    
    # Extract all .tgz filenames using regex
    tgz_files = re.findall(r'docker-(\d+\.\d+\.\d+)\.tgz', response.text)
    if not tgz_files:
        raise ValueError("No Docker .tgz files found in the directory listing.")
    
    # Sort versions naturally (e.g., 27.0.1 < 27.0.2 < 28.0.0)
    latest_version = sorted(tgz_files, key=lambda v: [int(x) for x in v.split('.')])[-1]
    print(f"Latest version found: docker-{latest_version}.tgz")
    return latest_version

def get_current_apk_version(apk_path, temp_dir):
    """Extract the current version from the APK's config.json."""
    apk_extract_dir = temp_dir / "apk_extracted"
    control_extract_dir = temp_dir / "control_extracted"
    
    # Extract APK
    extract_zip(apk_path, apk_extract_dir)
    
    # Extract control.tar.gz
    control_tar_gz = apk_extract_dir / "control.tar.gz"
    if not control_tar_gz.exists():
        raise FileNotFoundError(f"control.tar.gz not found in {apk_extract_dir}")
    extract_tar(control_tar_gz, control_extract_dir)
    
    # Read config.json
    config_path = control_extract_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"config.json not found in {control_extract_dir}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if 'general' not in config or 'version' not in config['general']:
        raise KeyError("Expected 'general.version' key not found in config.json")
    
    return config['general']['version']

def send_discord_notification(version, apk_filename):
    """Send a notification to Discord webhook about the new APK."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not set, skipping notification.")
        return
    
    payload = {
        "content": f"New Docker APK generated!\n**Version**: {version}\n**File**: {apk_filename}\n**Location**: {Path(__file__).parent / apk_filename}"
    }
    headers = {"Content-Type": "application/json"}
    
    print("Sending Discord notification...")
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        print("Discord notification sent successfully.")
    except requests.RequestException as e:
        print(f"Failed to send Discord notification: {e}")

def download_file(url, output_path):
    """Download a file from a URL to the specified output path."""
    print(f"Downloading {url} to {output_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

def extract_tar(tar_path, extract_dir):
    """Extract a .tar or .tar.gz file to the specified directory."""
    print(f"Extracting {tar_path} to {extract_dir}...")
    mode = "r:gz" if str(tar_path).endswith(".gz") else "r"
    with tarfile.open(tar_path, mode) as tar:
        tar.extractall(path=extract_dir)
    print("Extraction complete.")

def extract_zip(zip_path, extract_dir):
    """Extract a .zip or .apk file to the specified directory."""
    print(f"Extracting {zip_path} to {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete.")

def update_config_version(control_dir, new_version):
    """Update the 'version' key under 'general' in config.json."""
    config_path = os.path.join(control_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in {control_dir}")
    
    print(f"Updating version in {config_path} to {new_version}...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if 'general' not in config:
        raise KeyError("Expected 'general' key not found in config.json")
    
    config['general']['version'] = new_version
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print("config.json updated.")

def update_data_binaries(data_dir, docker_bin_dir):
    """Update only the Docker binaries in the data/bin directory, preserving other files."""
    print("Updating Docker binaries in data/bin...")
    bin_path = os.path.join(data_dir, "bin")
    if not os.path.exists(bin_path):
        raise FileNotFoundError(f"bin directory not found in {data_dir}")

    # Copy new Docker binaries, overwriting only matching files
    for binary in os.listdir(docker_bin_dir):
        src_path = os.path.join(docker_bin_dir, binary)
        dst_path = os.path.join(bin_path, binary)
        if os.path.isfile(src_path):
            print(f"Updating {binary}...")
            shutil.copy2(src_path, dst_path)
        else:
            print(f"Skipping {binary} (not a file).")
    
    print("Docker binaries updated, other files preserved.")

def repack_tar(tar_dir, output_tar, gz=True):
    """Repack a directory into a .tar or .tar.gz file."""
    print(f"Repacking {tar_dir} into {output_tar}...")
    mode = "w:gz" if gz else "w"
    with tarfile.open(output_tar, mode) as tar:
        tar.add(tar_dir, arcname=".")
    print("Repacking complete.")

def create_updated_apk(apk_extract_dir, output_apk_path):
    """Create a new .apk file from the updated control and data archives."""
    print(f"Creating updated APK at {output_apk_path}...")
    with zipfile.ZipFile(output_apk_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(apk_extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, apk_extract_dir)
                zipf.write(file_path, arcname)
    print("Updated APK created.")

def main():
    # Check if original APK exists
    if not ORIGINAL_APK.exists():
        raise FileNotFoundError(f"Original APK file not found: {ORIGINAL_APK}")

    # Create temporary directory in script's directory
    script_dir = Path(__file__).parent
    temp_dir = script_dir / "_temp"
    try:
        # Ensure temp directory is clean
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        temp_path = temp_dir
        
        # Get latest Docker version
        latest_version = get_latest_docker_version()
        
        # Get current APK version
        print(f"Checking current version in {ORIGINAL_APK}...")
        current_version = get_current_apk_version(ORIGINAL_APK, temp_path)
        print(f"Current APK version: {current_version}")
        
        # Skip if versions match
        if current_version == latest_version:
            print(f"No update needed: APK version ({current_version}) matches latest Docker version ({latest_version}).")
            return
        
        print(f"New version detected: Updating from {current_version} to {latest_version}...")
        
        # Set up remaining temporary directories
        docker_tar = temp_path / "docker-latest.tgz"
        docker_extract_dir = temp_path / "docker_extracted"
        apk_extract_dir = temp_path / "apk_extracted"
        control_extract_dir = temp_path / "control_extracted"
        data_extract_dir = temp_path / "data_extracted"

        # Step 1: Download the new Docker version
        docker_url = f"{DOCKER_BASE_URL}docker-{latest_version}.tgz"
        download_file(docker_url, docker_tar)

        # Step 2: Extract the Docker binaries
        extract_tar(docker_tar, docker_extract_dir)

        # Step 3: Extract the original APK
        extract_zip(ORIGINAL_APK, apk_extract_dir)

        # Step 4: Extract control.tar.gz
        control_tar_gz = apk_extract_dir / "control.tar.gz"
        if not control_tar_gz.exists():
            raise FileNotFoundError(f"control.tar.gz not found in {apk_extract_dir}")
        extract_tar(control_tar_gz, control_extract_dir)

        # Step 5: Update config.json
        update_config_version(control_extract_dir, latest_version)

        # Step 6: Repack control.tar.gz
        repack_tar(control_extract_dir, apk_extract_dir / "control.tar.gz")

        # Step 7: Extract data.tar.gz
        data_tar_gz = apk_extract_dir / "data.tar.gz"
        if not data_tar_gz.exists():
            raise FileNotFoundError(f"data.tar.gz not found in {apk_extract_dir}")
        extract_tar(data_tar_gz, data_extract_dir)

        # Step 8: Update binaries in data/bin
        update_data_binaries(data_extract_dir, docker_extract_dir / "docker")

        # Step 9: Repack data.tar.gz
        repack_tar(data_extract_dir, apk_extract_dir / "data.tar.gz")

        # Step 10: Create the updated APK
        output_apk = script_dir / f"docker_{latest_version}.apk"
        create_updated_apk(apk_extract_dir, output_apk)

        # Step 11: Send Discord notification
        send_discord_notification(latest_version, output_apk.name)

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

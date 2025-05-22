# mpmp.py - Mscript Package Manager

import wget
import zipfile
import json
import sys
import os
import requests
import time
import platform
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "https://mscript-lang.pythonanywhere.com"
__VERSION__ = "0.2.0"
DATA_FILE = "mscript_packages.json"
PKG_DIR = "mscript_packages"

def load_data():
    return json.loads(open(DATA_FILE).read()) if os.path.exists(DATA_FILE) else {"packages": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def installed_packages(data):
    return {pkg["package_name"]: pkg for pkg in data["packages"]}

def print_box(text, icon="[→]", color=Fore.CYAN):
    print(f"{color}{icon} {text}{Style.RESET_ALL}")

def fetch_package_info(package):
    try:
        r = requests.get(f"{BASE_URL}/api/packages/{package}")
        if r.status_code != 200:
            return None
        data = r.json()
        return data["data"] if data["status"] != "error" else None
    except requests.exceptions.RequestException:
        return None

def install_package(package, data, installed):
    if package in installed:
        print_box(f"{package} already installed.", "[✓]", Fore.YELLOW)
        return

    pkg_data = fetch_package_info(package)
    if not pkg_data:
        print_box(f"Package '{package}' not found.", "[X]", Fore.RED)
        return

    for dep in pkg_data.get("dependencies", []):
        install_package(dep, data, installed)

    print_box(f"Installing {package} v{pkg_data['version']}...", "[+]", Fore.GREEN)
    pkg_path = os.path.join(PKG_DIR, package)
    os.makedirs(pkg_path, exist_ok=True)

    zip_path = os.path.join(pkg_path, f"{pkg_data['version']}.zip")
    wget.download(f"{BASE_URL}/api/packages/download/{package}", out=zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(pkg_path)
    os.remove(zip_path)

    pkg_data["add_date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data["packages"].append(pkg_data)
    installed[package] = pkg_data
    print_box(f"Installed {package} successfully.", "[✓]", Fore.GREEN)

def uninstall_package(package, data):
    pkgs = installed_packages(data)
    if package not in pkgs:
        print_box(f"Package '{package}' not installed.", "[X]", Fore.RED)
        return

    to_remove = [package]
    removed = []

    for pkg in to_remove:
        deps_used_elsewhere = any(
            pkg in other.get("dependencies", [])
            for name, other in pkgs.items()
            if name != package
        )
        if deps_used_elsewhere:
            print_box(f"Dependency '{pkg}' used by another package, skipping.", "[→]", Fore.YELLOW)
            continue

        data["packages"] = [p for p in data["packages"] if p["package_name"] != pkg]
        try:
            os.rmdir(os.path.join(PKG_DIR, pkg))
        except OSError:
            pass
        removed.append(pkg)

    print_box(f"Uninstalled: {', '.join(removed)}", "[✓]", Fore.GREEN if removed else Fore.YELLOW)

def list_packages(data, package=None):
    pkgs = data["packages"]
    if package:
        for pkg in pkgs:
            if pkg["package_name"] == package:
                print_box(f"{package} v{pkg['version']} - {pkg['description']}", "[✓]", Fore.CYAN)
                print(f"{Fore.WHITE}Author: {pkg['author']}, License: {pkg['license']}")
                print(f"URL: {pkg['url']}")
                print(f"Installed: {pkg['add_date']}")
                return
        print_box(f"Package '{package}' not found.", "[X]", Fore.RED)
    else:
        print_box("Installed packages:", "[📦]", Fore.MAGENTA)
        for pkg in pkgs:
            print(f"- {pkg['package_name']} v{pkg['version']}")

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: mpp <install|uninstall|list|--version> [package]")
        return

    action = sys.argv[1]
    package = sys.argv[2] if len(sys.argv) == 3 else None

    os.makedirs(PKG_DIR, exist_ok=True)
    data = load_data()
    installed = installed_packages(data)

    if action == "install":
        if not package:
            print_box("No package name provided.", "[X]", Fore.RED)
            return
        install_package(package, data, installed)
        save_data(data)

    elif action == "uninstall":
        if not package:
            print_box("No package name provided.", "[X]", Fore.RED)
            return
        uninstall_package(package, data)
        save_data(data)

    elif action == "list":
        list_packages(data, package)

    elif action == "--version":
        print_box(f"Mscript Package Manager v{__VERSION__} ({platform.platform()})", "[⚙️]", Fore.BLUE)

    else:
        print_box(f"Unknown action: {action}", "[X]", Fore.RED)

if __name__ == "__main__":
    main()

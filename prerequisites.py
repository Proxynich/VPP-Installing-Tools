import subprocess
import sys

def install_important_packages():
    """Install essential packages"""
    print("📦 Installing important packages...")
    packages = ["make", "git"]
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
        print("✅ Important packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install important packages: {e}")
        sys.exit(1)

def install_additional_packages():
    """Install additional tools for monitoring and diagnostics"""
    print("📦 Installing additional packages...")
    packages = [
        "htop", "net-tools", "ipmitool", "lshw", "rsync",
        "traceroute", "snmpd", "snmp", "mtr", "btop", "iftop",
        "nload", "bwm-ng", "bmon"
    ]
    try:
        subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
        print("✅ Additional packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install additional packages: {e}")
        sys.exit(1)

def install_prerequisites():
    """Interactive prerequisite installation"""
    max_retries = 3
    retries = 0

    while retries < max_retries:
        print("\n🔧 Choose installation type:")
        print("1. Install important packages")
        print("2. Install additional packages")
        print("3. Install all prerequisites")
        choice = input("Enter your choice (1/2/3): ")

        if choice in ["1", "2", "3"]:
            if choice == "1":
                install_important_packages()
            elif choice == "2":
                install_additional_packages()
            elif choice == "3":
                install_important_packages()
                install_additional_packages()
            break
        else:
            retries += 1
            remaining = max_retries - retries
            print(f"❌ Invalid choice. You have {remaining} attempt(s) left.")

    if retries == max_retries:
        print("❌ Too many invalid attempts. Exiting.")
        sys.exit(1)

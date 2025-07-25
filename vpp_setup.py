from system_info import get_physical_cores
import os
import subprocess
import sys
import re
import logging

logging.basicConfig(filename='logs/install.log', level=logging.INFO)

def get_vpp_version():
    """Let user choose VPP version"""
    print("\n🔧 Choose VPP version:")
    print("1. Latest (default)")
    print("2. Stable 2506")
    print("3. Stable 2502")
    print("4. Stable 2410")
    print("5. Stable 2406")
    print("6. Custom version (branch/tag)")
    choice = input("Enter your choice (1/2/3/4/5/6): ").strip()

    versions = {
        "1": "main",
        "2": "stable/2506",
        "3": "stable/2502",
        "4": "stable/2410",
        "5": "stable/2406"
    }

    if choice in ["1", "2", "3", "4", "5"]:
        return versions[choice]
    elif choice == "6":
        custom_version = input("Enter custom branch or tag (e.g., v24.06): ").strip()
        if not re.match(r"^[a-zA-Z0-9/-]+$", custom_version):
            print("❌ Invalid version format. Using latest.")
            return "main"
        return custom_version
    else:
        print("❌ Invalid choice. Using latest.")
        return "main"

def calculate_core_allocation(total_cores, data_ratio=0.6, control_ratio=0.4):
    """Calculate core allocation #prxy (excluding Core 0 and 1)"""
    available_cores = total_cores - 2  # Exclude Core 0 and 1
    data_cores = int(available_cores * data_ratio)
    control_cores = int(available_cores * control_ratio)

    if data_cores + control_cores > available_cores:
        control_cores = available_cores - data_cores

    if data_cores < 1:
        data_cores = 1
        control_cores = available_cores - 1

    data_range = list(range(2, 2 + data_cores))
    control_core = 2 + data_cores

    return {
        "data_plane": data_range,
        "control_plane": control_core,
        "total_cores": total_cores,
        "note": f"Core 0 and 1 are not isolated. Data Plane: {data_cores} core(s), Control Plane: 1 core."
    }

def get_user_choice(total_cores):
    """Let user choose core allocation strategy"""
    print("\n🔧 Choose CPU allocation strategy:")
    print("1. Recommended (60% Data Plane, 40% Control Plane)")
    print("2. Custom allocation (e.g., 70% Data Plane, 30% Control Plane)")
    choice = input("Enter your choice (1/2): ").lower()

    if choice == "1":
        return calculate_core_allocation(total_cores)
    elif choice == "2":
        while True:
            try:
                data_ratio = float(input("Enter data plane ratio (e.g., 0.7 for 70%): "))
                control_ratio = 1 - data_ratio
                if 0.1 <= data_ratio <= 0.9:
                    return calculate_core_allocation(total_cores, data_ratio, control_ratio)
                print("❌ Ratio must be between 0.1 and 0.9. Try again.")
            except ValueError:
                print("❌ Invalid input. Use decimal values (e.g., 0.6 for 60%).")
    else:
        print("❌ Invalid choice. Using default (60/40).")
        return calculate_core_allocation(total_cores)

def update_grub_isolation(core_alloc):
    """Update GRUB for CPU isolation"""
    data_cores = ",".join(map(str, core_alloc["data_plane"]))
    control_core = str(core_alloc["control_plane"])

    with open("/etc/default/grub", "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "GRUB_CMDLINE_LINUX=" in line:
            line = re.sub(
                r'GRUB_CMDLINE_LINUX=".*?"',
                f'GRUB_CMDLINE_LINUX="isolcpus={data_cores},{control_core} nohz_full={data_cores},{control_core} rcu_nocbs={data_cores},{control_core}',
                line
            )
        new_lines.append(line)

    with open("/etc/default/grub", "w") as f:
        f.writelines(new_lines)

    subprocess.run(["sudo", "update-grub"], check=True)
    print("✅ GRUB updated with CPU isolation. Reboot required.")

def install_vpp_debs():
    """Install VPP .deb packages from build-root/ directory"""
    build_root = "build-root"

    if not os.path.exists(build_root):
        print(f"❌ Directory {build_root} does not exist. Exiting.")
        logging.error(f"Directory {build_root} does not exist")
        sys.exit(1)

    deb_files = [f for f in os.listdir(build_root) if f.endswith(".deb")]
    if not deb_files:
        print("❌ No .deb files found in build-root. Exiting.")
        logging.error("No .deb files found in build-root")
        sys.exit(1)

    deb_paths = [os.path.join(build_root, f) for f in deb_files]

    try:
        print("📦 Installing VPP .deb packages...")
        subprocess.run(["sudo", "dpkg", "-i"] + deb_paths, check=True)
        print("✅ VPP packages installed successfully.")
        logging.info("VPP packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install .deb packages: {e}")
        logging.error(f"Failed to install .deb packages: {e}")
        sys.exit(1)

def install_vpp():
    """Install VPP with core allocation and version selection"""
    try:
        vpp_version = get_vpp_version()
        print(f"📦 Cloning VPP from GitHub (version: {vpp_version})...")
        os.makedirs("~/src", exist_ok=True)
        os.chdir("~/src")
        subprocess.run(["git", "clone", "https://github.com/FDio/vpp.git"], check=True)
        os.chdir("~/src/vpp")

        # Checkout selected version
        try:
            subprocess.run(["git", "checkout", vpp_version], check=True)
            print(f"✅ Checked out VPP version: {vpp_version}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to checkout version {vpp_version}. Falling back to latest.")
            subprocess.run(["git", "checkout", "main"], check=True)

        physical_cores = get_physical_cores()
        if physical_cores < 3:
            print("❌ At least 3 physical cores required for isolation. Exiting.")
            sys.exit(1)

        core_alloc = get_user_choice(physical_cores)

        print("\n🔧 CPU Allocation Result:")
        print(f"Physical Cores: {core_alloc['total_cores']}")
        print(f"Data Plane Cores: {core_alloc['data_plane']}")
        print(f"Control Plane Core: {core_alloc['control_plane']}")
        print(f"Note: {core_alloc['note']}")

        with open("/etc/vpp/startup.conf", "w") as f:
            data_cores = ",".join(map(str, core_alloc["data_plane"]))
            f.write(f"cpu {{\n  main-core {core_alloc['control_plane']}\n  corelist-workers {data_cores}\n}}\n")

        isolate = input("Apply CPU isolation to GRUB? (y/n): ").lower()
        if isolate == "y":
            update_grub_isolation(core_alloc)

        print("📦 Installing VPP dependencies...")
        subprocess.run(["sudo", "make", "install-dep"], check=True)
        subprocess.run(["sudo", "make", "install-ext-dep"], check=True)

        print("🔧 Building VPP release package...")
        subprocess.run(["sudo", "make", "build-release"], check=True)
        subprocess.run(["sudo", "make", "pkg-deb"], check=True)

        install_vpp_debs()

        print("✅ VPP installed successfully.")
    except Exception as e:
        print(f"❌ Failed to install VPP: {e}")
        logging.error(f"Failed to install VPP: {e}")
        sys.exit(1)

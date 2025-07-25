import os
import re
import subprocess
import sys

def detect_pci_addresses():
    """Detect Intel/Mellanox NICs via lspci"""
    try:
        pci_devices = subprocess.check_output(
            ["lspci", "-D", "-nn", "|", "grep", "-i", "Ethernet"], text=True
        )
        intel_pci = []
        mellanox_pci = []
        for line in pci_devices.splitlines():
            if "Intel" in line:
                match = re.search(r"([0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9])", line)
                if match:
                    intel_pci.append((match.group(1), "Intel"))
            elif "Mellanox" in line or "ConnectX" in line:
                match = re.search(r"([0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9])", line)
                if match:
                    mellanox_pci.append((match.group(1), "Mellanox"))
        return {"intel": intel_pci, "mellanox": mellanox_pci}
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to detect PCI addresses: {e}")
        return {"intel": [], "mellanox": []}

def list_nics(nics):
    """List detected NICs with indices"""
    print("\n🔍 Detected NICs:")
    for i, (pci, vendor) in enumerate(nics):
        print(f"{i+1}. {vendor} NIC at {pci}")
    return nics

def get_user_selection(nics):
    """Let user select NICs to bind"""
    selected_nics = []
    while True:
        try:
            choice = input("\nEnter NIC numbers to bind (comma-separated, e.g., 1,3): ")
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            for idx in indices:
                if 0 <= idx < len(nics):
                    selected_nics.append(nics[idx])
                else:
                    print(f"⚠️ Invalid selection: {idx+1}. Ignoring.")
            break
        except ValueError:
            print("❌ Please enter valid numbers.")
    return selected_nics

def choose_driver(vendor):
    """Recommend and let user choose DPDK-compatible driver"""
    recommendations = {
        "Intel": ["vfio-pci", "igb_uio", "uio_pci_generic"],
        "Mellanox": ["mlx5_core", "mlx4_core", "vfio-pci"]
    }
    print(f"\n🔧 Available drivers for {vendor}:")
    for i, driver in enumerate(recommendations.get(vendor, ["Unknown"])):
        print(f"{i+1}. {driver}")
    while True:
        try:
            driver_choice = int(input(f"Select driver for {vendor} (1-{len(recommendations.get(vendor, [1]))}): "))
            if 1 <= driver_choice <= len(recommendations.get(vendor, [1])):
                return recommendations.get(vendor, ["Unknown"])[driver_choice - 1]
            print("❌ Invalid choice. Try again.")
        except ValueError:
            print("❌ Please enter a number.")

def generate_dpdk_bind_script(selected_nics, output_path="config_template/dpdk-bind.sh"):
    """Generate dpdk-bind.sh with user-selected NICs and drivers"""
    script_content = """#!/bin/bash
# Enable vfio driver
sudo modprobe vfio-pci

# Unbind and bind NICs
"""
    for pci, vendor in selected_nics:
        driver = choose_driver(vendor)
        script_content += f'# Unbind {pci}\n'
        script_content += f'echo {pci} > /sys/bus/pci/devices/{pci}/driver/unbind\n'
        script_content += f'# Bind to {driver}\n'
        script_content += f'echo {driver} > /sys/bus/pci/drivers/{driver}/bind\n'

    try:
        with open(output_path, "w") as f:
            f.write(script_content)
        os.chmod(output_path, 0o755)
        print(f"✅ Script saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to save dpdk-bind.sh: {e}")
        sys.exit(1)

def copy_service_template(service_path="config_template/dpdk-bind.service"):
    """Copy dpdk-bind.service template"""
    try:
        with open(service_path, "r") as src:
            with open("/etc/systemd/system/dpdk-bind.service", "w") as dst:
                dst.write(src.read())
        print("✅ Service template copied to /etc/systemd/system/dpdk-bind.service")
    except Exception as e:
        print(f"❌ Failed to copy service template: {e}")
        sys.exit(1)

def bind_nics():
    """Interactive NIC binding to DPDK drivers"""
    nics = detect_pci_addresses()
    intel_nics = nics["intel"]
    mellanox_nics = nics["mellanox"]

    all_nics = intel_nics + mellanox_nics
    if not all_nics:
        print("❌ No NICs detected. Exiting.")
        sys.exit(1)

    listed_nics = list_nics(all_nics)
    selected_nics = get_user_selection(listed_nics)

    if not selected_nics:
        print("❌ No NICs selected. Exiting.")
        sys.exit(1)

    generate_dpdk_bind_script(selected_nics)
    copy_service_template()

    print("\n✅ NIC binding configured. Reboot required to apply changes.")

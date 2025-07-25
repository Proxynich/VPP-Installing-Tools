import shutil
import os

def apply_configurations():
    """Apply configuration files from config_template"""
    config_files = {
        "/etc/vpp/startup.conf": "config_template/startup.conf",
        "/etc/vpp/bootstrap.vpp": "config_template/bootstrap.vpp",
        "/etc/sysctl.d/80-vpp.conf": "config_template/80-vpp.conf",
        "/etc/sysctl.d/81-vpp-netlink.conf": "config_template/81-vpp-netlink.conf",
        "/usr/lib/systemd/system/netns-dataplane.service": "config_template/netns-dataplane.service",
        "/usr/lib/systemd/system/ssh-dataplane.service": "config_template/ssh-dataplane.service"
    }

    for target, source in config_files.items():
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy(source, target)
            print(f"✅ File {target} applied.")
        except Exception as e:
            print(f"❌ Failed to apply {source} to {target}: {e}")

import platform
import subprocess
import re

def detect_os():
    """Detect OS using /etc/os-release"""
    try:
        with open("/etc/os-release", "r") as f:
            os_info = {}
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os_info[key] = value.strip('"')

        os_name = os_info.get("NAME", "").lower()
        os_codename = os_info.get("VERSION_CODENAME", "").lower()

        if "ubuntu" in os_name or "debian" in os_name:
            return {"os": "Ubuntu" if "ubuntu" in os_name else "Debian", "codename": os_codename}
        raise OSError(f"Unsupported OS: {os_name}")
    except Exception as e:
        raise OSError(f"Failed to detect OS: {e}")

def is_supported_os():
    """Check if OS is Ubuntu/Debian"""
    try:
        os_info = detect_os()
        print(f"✅ Detected OS: {os_info['os']} {os_info['codename']}")
        return os_info
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_physical_cores():
    """Get number of physical CPU cores"""
    try:
        cpu_info = subprocess.check_output(["lscpu"], text=True)
        sockets = 0
        cores_per_socket = 0

        for line in cpu_info.splitlines():
            if "Socket(s)" in line:
                sockets = int(line.split(":")[1].strip())
            elif "Core(s) per socket" in line:
                cores_per_socket = int(line.split(":")[1].strip())

        return sockets * cores_per_socket
    except Exception as e:
        print(f"❌ Failed to detect physical cores: {e}")
        return 0

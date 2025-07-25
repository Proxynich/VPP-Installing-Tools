# VPP-Installer-Tools

Automate the installation and configuration of **FD.io VPP** and **FRRouting** with hardware-aware optimization, modular design, and interactive prompts for flexibility.

---

## 🚀 Features

- ✅ Interactive installation flow for VPP and FRRouting  
- ✅ Physical core allocation (60% data-plane / 40% control-plane, customizable)  
- ✅ DPDK NIC binding with driver selection (Intel/Mellanox support)  
- ✅ CPU isolation in GRUB for performance-critical workloads  
- ✅ Modular architecture for easy maintenance and extension  
- ✅ Logging to `logs/install.log` for debugging and auditing  
- ✅ Multi-version support for VPP (stable/2410, stable/2502, etc.)  

---

## 📦 Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+  
- **User Privileges**: `sudo` access  
- **Hardware**: At least **3 physical CPU cores** (recommended: 8+ cores)  
- **Dependencies**: `make`, `git`, `apt`, `dpkg`, `lscpu`, `lspci`  

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/VPP-Installer-Tools.git
cd VPP-Installer-Tools
```

### 2. Run the Installer
```bash
python main.py
```

---

## 🧰 Interactive Menu

Available options:
- **1. Install prerequisites**
- **2. Bind NICs to DPDK-compatible drivers**
- **3. Install VPP** (with version and core allocation selection)
- **4. Install FRRouting** (from official repository)
- **5. Apply configurations** (sysctl, systemd services, etc.)
- **6. Exit**

---

## 🧪 Example Usage

#### VPP Version Selection
```bash
Choose VPP version:
1. Latest (main)
2. Stable 2506
3. Stable 2502
4. Stable 2410
5. Stable 2406
6. Custom branch/tag
Enter your choice: 2
✅ Checked out VPP version: stable/2506
```

#### Core Allocation
```bash
Choose CPU allocation strategy:
1. Recommended (60% Data Plane, 40% Control Plane)
2. Custom allocation
Enter your choice: 1
🔧 CPU Allocation Result:
Physical Cores: 8
Data Plane Cores: [2, 3, 4]
Control Plane Core: 5
Note: Core 0 and 1 are not isolated. Data Plane: 3 core(s), Control Plane: 1 core.
```

#### Post-Installation
```bash
Apply CPU isolation to GRUB? (y/n): y
✅ GRUB updated with CPU isolation. Reboot required.
```

---

## 🧾 Configuration Templates

| File | Purpose |
|------|---------|
| `startup.conf` | VPP core/workers configuration |
| `80-vpp.conf` | Hugepages and memory settings |
| `81-vpp-netlink.conf` | Socket buffer tuning |
| `dpdk-bind.sh` | Script to bind NICs to DPDK drivers |
| `dpdk-bind.service` | Systemd service for DPDK binding |
| `netns-dataplane.service` | Network namespace for VPP/FRR integration |
| `ssh-dataplane.service` | SSH access to dataplane namespace |

---

## 📐 Supported FRRouting Versions

The FRRouting repository provides the following versions and directories:

### 📁 Repository Structure
```
/frr/
├── conf/                 # Configuration templates (last modified: 09-Apr-2025)
├── db/                   # Database-related files (last modified: 18-Mar-2025)
├── dists/                # Distribution-specific packages (last modified: 17-Apr-2024)
├── incoming/             # Incoming packages (last modified: 02-Jul-2020)
├── libyang1/             # `libyang1` dependencies (last modified: 10-Jun-2020)
├── lists/                # Package index files (last modified: 15-May-2019)
├── pool/                 # Debian package pool (last modified: 17-Mar-2025)
├── temp/                 # Temporary files (last modified: 05-Mar-2019)
├── keys.asc              # ASCII GPG key (last modified: 28-Oct-2020, size: 22 KB)
└── keys.gpg              # Binary GPG key (last modified: 02-Jan-2023, size: 16 KB)
```

> Repository source: [FRRouting Debian Archive](https://deb.frrouting.org/frr/)

---

## 🧩 Post-Installation Steps

1. **Reboot System**  
   ```bash
   sudo reboot
   ```

2. **Verify VPP**  
   ```bash
   vppctl show version
   vppctl show thread
   ```

3. **Verify FRRouting**  
   ```bash
   systemctl status frr
   ```

4. **Check DPDK Bindings**  
   ```bash
   dpdk-devbind.py --status
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/your-feature-name`)  
3. Commit your changes  
4. Push to your fork and submit a pull request  

---

## 📞 Support

For issues or questions, contact via telegram: **@excelsebastianus**

---

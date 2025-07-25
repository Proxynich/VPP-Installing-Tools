#!/usr/bin/env python3
import os
import sys
from prerequisites import install_prerequisites
from dpdk_binding import bind_nics
from vpp_setup import install_vpp
from frr_setup import install_frr
from config_manager import apply_configurations
import logging

logging.basicConfig(filename='logs/install.log', level=logging.INFO)

def show_menu():
    print("\n🔧 Choose an action:")
    print("1. Install prerequisites")
    print("2. Bind NICs to DPDK-compatible drivers")
    print("3. Install VPP")
    print("4. Install FRRouting")
    print("5. Apply configurations")
    print("6. Exit")

def main():
    while True:
        try:
            show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                install_prerequisites()
            elif choice == "2":
                bind_nics()
            elif choice == "3":
                install_vpp()
            elif choice == "4":
                install_frr()
            elif choice == "5":
                apply_configurations()
            elif choice == "6":
                print("✅ Exiting installer.")
                break
            else:
                print("❌ Invalid choice. Try again.")
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import platform
import subprocess
import os 
try:
    import psutil
except ImportError:
    psutil = None
import socket

def get_os():
    system_os = platform.system()
    if system_os == "Darwin":
        return "Mac"
    elif system_os == "Linux":
        return "Linux"
    else:
        print("Unsupported operating system. This tool only supports Mac and Linux.")
        exit(1)

def package_tools():
    current_os = get_os()
    
    if current_os == "Mac":
        check_brew = subprocess.run(['brew', '--version'], capture_output=True, text=True)
        if check_brew.returncode == 0:
            print("Homebrew is installed")
            return True
        else:
            print("Homebrew is not installed")
            print("Installing homebrew .........")
            install = subprocess.run(['/bin/bash', '-c', "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"], capture_output=True, text=True)
            if install.returncode == 0:
                print("Homebrew installed successfully")
                return True
            else:
                print("Failed to install Homebrew")
                return False
    
    elif current_os == "Linux":
        # For Linux, we'll check for package managers and install dependencies
        print("Linux detected - package management will be handled per distribution")
        return True

def check_nmap():
    current_os = get_os()
    
    if current_os == "Mac":
        mac_nmap = subprocess.run(['which', 'nmap'], capture_output=True, text=True)
        if mac_nmap.returncode == 0:
            print("Nmap is installed")
            return True
        else:
            print("Nmap is not installed")
            print("Installing nmap .........")
            install = subprocess.run(['brew', 'install', 'nmap'], capture_output=True, text=True, timeout=300)
            if install.returncode == 0:
                print("Nmap installed successfully")
                return True
            else:
                print("Failed to install Nmap")
                return False

    elif current_os == "Linux":
        linux_nmap = subprocess.run(['which', 'nmap'], capture_output=True, text=True)
        if linux_nmap.returncode == 0:
            print("Nmap is installed")
            return True
        else:
            print("Nmap is not installed")
            print("Installing nmap .........")
            # Try different package managers
            try:
                # Try apt first (Debian/Ubuntu)
                install = subprocess.run(['sudo', 'apt', 'install', '-y', 'nmap'], check=True, timeout=300)
                print("Nmap installed successfully")
                return True
            except subprocess.CalledProcessError:
                try:
                    # Try yum (RHEL/CentOS)
                    install = subprocess.run(['sudo', 'yum', 'install', '-y', 'nmap'], check=True, timeout=300)
                    print("Nmap installed successfully")
                    return True
                except subprocess.CalledProcessError:
                    try:
                        # Try pacman (Arch)
                        install = subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'nmap'], check=True, timeout=300)
                        print("Nmap installed successfully")
                        return True
                    except subprocess.CalledProcessError:
                        print("Failed to install Nmap. Please install it manually.")
                        return False

def get_network_interface_ips():
    """Get all network interface IPv4 addresses using psutil (cross-platform)."""
    interfaces = {}
    try:
        if psutil is None:
            print("psutil is not installed. Install it with: pip install psutil")
            return interfaces

        stats = psutil.net_if_stats()
        for ifname, addrs in psutil.net_if_addrs().items():
            # Skip interfaces that are down when stats are available
            if ifname in stats and not stats[ifname].isup:
                continue

            for a in addrs:
                # IPv4 only
                if getattr(a, 'family', None) == socket.AF_INET:
                    ip = a.address
                    # Skip loopback and link-local
                    if ip and not ip.startswith('127.') and not ip.startswith('169.254.'):
                        interfaces[ifname] = ip
                        break
    except Exception as e:
        print(f"Error getting network interfaces via psutil: {e}")
    
    return interfaces

def get_network_range(ip_address):
    """Convert an IP address to its network range (assumes /24 subnet)"""
    if ip_address:
        ip_parts = ip_address.split('.')
        if len(ip_parts) == 4:
            network_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            return network_range
    return None

def display_network_info():
    """Display comprehensive network information"""
    print("="*60)
    print("    NETWORK SCANNING CONFIGURATION")
    print("="*60)
    
    
    print("\nAll Network Interfaces:")
    interfaces = get_network_interface_ips()
    if interfaces:
        for interface, ip in interfaces.items():
            network_range = get_network_range(ip)
            print(f"  {interface}: {ip} ({network_range})")
    else:
        print("  No interfaces found")
    
    print("="*60)
    print("    PRIVATE IP AND NETWORK RANGE")
    print("="*60)

    private_ip = None
    network_range = None
    for interface, ip in interfaces.items():
        if not ip.startswith('127.'):  # Skip localhost
            private_ip = ip
            network_range = get_network_range(ip)
            break

    if private_ip and network_range:
        print(f"  Private IP: {private_ip}")
        print(f"  Network Range: {network_range}")

    return (private_ip, network_range) if private_ip and network_range else (None, None)

if __name__ == "__main__":
    print("Local Port Scanner - Mac/Linux Edition")
    print("="*50)
    
    pkg_code = package_tools()
    nmap_code = check_nmap()

    failed = []
    if not pkg_code:
        failed.append("package_tools")
    if not nmap_code:
        failed.append("check_nmap")

    if not failed:
        print("All tools installed successfully")
    else:
        print("Failed: " + ", ".join(failed))

    private_ip, network_range = display_network_info()
    if network_range:
        # Make the scanner script executable
        try:
            subprocess.run(['chmod', '+x', './scan.sh'], timeout=10)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Warning: Could not make script executable: {e}")
        
        # Validate scan type input
        valid_scan_types = ['discovery', 'ports', 'vuln', '-d', '-p', '-v', 'd', 'p', 'v']
        scan_type = input("Enter the type of scan (discovery/ports/vuln): ").strip()
        if scan_type not in valid_scan_types:
            print(f"Invalid scan type: {scan_type}")
            print(f"Valid options: {', '.join(valid_scan_types[:3])}")
            exit(1)
        
        # Run the scanner script for both Mac and Linux
        try:
            subprocess.run(['./scan.sh', network_range, scan_type], check=True, timeout=3600)
        except subprocess.TimeoutExpired:
            print("Scanner scan timed out after 1 hour.")
        except subprocess.CalledProcessError as e:
            print(f"Scanner failed with error: {e}")
        except FileNotFoundError:
            print("scan.sh not found. Please ensure the script is in the current directory.")
    else:
        print("Could not determine network range. Exiting.")


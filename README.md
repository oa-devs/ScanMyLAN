# Local Scanner - Mac/Linux Edition

A tool to scan devices connected to your home router or private network, combining Python and Bash for easy network discovery, port scanning, and vulnerability checks.

## Features

- **Cross-platform support**: Mac and Linux only
- **Network discovery**: Find live hosts on your network
- **Port scanning**: Look for open ports that run SSH, web, FTP, printer services
- **Vulnerability scanning**: Comprehensive security assessment
- **Automatic dependency management**: Installs required tools (nmap, homebrew on Mac)

## Usage

1. Run the main Python script:

   ```bash
   python3 app.py
   ```

2. The script will:

   - Detect your operating system
   - Install necessary dependencies (Homebrew on Mac, package managers on Linux)
   - Install nmap if not present
   - Display your network configuration
   - Prompt for scan type

3. Choose scan type:
   - `discovery`: Network discovery scan to find live hosts
   - `ports`: Port scan for common services (SSH, HTTP, HTTPS, FTP, etc.)
   - `vuln`: Comprehensive vulnerability scan

## Requirements

- Python 3.x
- psutil (optional, for enhanced network interface detection)
- nmap (automatically installed)
- Root/sudo access (for some scan types)

## Supported Systems

- macOS (Darwin)
- Linux distributions (Ubuntu, CentOS, Arch, etc.)

**Note**: Windows support has been removed in this version.

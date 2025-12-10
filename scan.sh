#!/bin/bash

# Network Scanner Script for Mac/Linux
# Usage: ./scan.sh [target] [scan_type]
# Shortcuts: -d (discovery), -p (ports), -v (vuln)
# Examples:
#   ./scan.sh 192.168.1.0/24 -d           # Network discovery
#   ./scan.sh 192.168.1.0/24 -p           # Port scan
#   ./scan.sh 192.168.1.100 -v            # Vulnerability scan (default)

TARGET=${1:-""}
SCAN_TYPE=${2:-"vuln"}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Check if nmap is installed
if ! command -v nmap &> /dev/null; then
    echo "Error: nmap is not installed or not in PATH"
    echo "Please run the Python setup script first: python3 app.py"
    exit 1
fi


if [ -z "$TARGET" ]; then
    echo "Usage: $0 <target> [scan_type]"
    echo "Scan types: discovery (-d), ports (-p), vuln (-v)"
    echo "Example: $0 192.168.1.0/24 -d"
    exit 1
fi

# Detect OS for cross-platform compatibility
OS=$(uname -s)
case "$OS" in
    "Darwin")
        echo "Detected: macOS"
        ;;
    "Linux")
        echo "Detected: Linux"
        ;;
    *)
        echo "Warning: Unsupported OS detected: $OS"
        ;;
esac


lines=$(printf "%-${COLUMNS}s" "" | tr " " "=")
echo "$lines"

echo "Starting $SCAN_TYPE scan on $TARGET..."
echo "$lines"
case $SCAN_TYPE in
    "discovery" | "-d" | "d")
        # Network discovery scan - find live hosts
        echo "Performing network discovery scan..."
        OUTPUT_FILE="nmap_discovery_${TIMESTAMP}.txt"
        if nmap -sn "$TARGET" -oN "$OUTPUT_FILE"; then
            echo "Discovery scan completed successfully"
            echo "Results saved to: $OUTPUT_FILE"
        else
            echo "Error: Discovery scan failed"
            exit 1
        fi
        ;;
    "ports" | "-p" | "p")
        # Port scan for common services (SSH, HTTP, HTTPS, FTP, etc.)
        echo "Scanning for common ports (SSH, Web, FTP, Printer)..."
        OUTPUT_FILE="nmap_ports_${TIMESTAMP}.txt"
        if nmap -p 22,23,80,443,21,515,631,9100 -sV --open "$TARGET" -Pn -oN "$OUTPUT_FILE"; then
            echo "Port scan completed successfully"
            echo "Results saved to: $OUTPUT_FILE"
        else
            echo "Error: Port scan failed"
            exit 1
        fi
        ;;
    "vuln" | "-v" | "v")
        # Vulnerability scan - check if we need sudo
        echo "Performing vulnerability scan..."
        OUTPUT_FILE="nmap_vuln_${TIMESTAMP}.txt"
        
        # Check if running as root or if sudo is available
        if [ "$EUID" -eq 0 ]; then
            echo "Running as root - proceeding with SYN scan"
            nmap --script vuln -p- -Pn -sS -sV --min-rate 1000 --max-retries 1 --host-timeout 30s --open -oN "$OUTPUT_FILE" "$TARGET"
        elif command -v sudo &> /dev/null; then
            echo "Using sudo for SYN scan (you may be prompted for password)"
            sudo nmap --script vuln -p- -Pn -sS -sV --min-rate 1000 --max-retries 1 --host-timeout 30s --open -oN "$OUTPUT_FILE" "$TARGET"
        else
            echo "No sudo available, using TCP connect scan (slower but doesn't require root)"
            nmap --script vuln -p- -Pn -sT -sV --min-rate 1000 --max-retries 1 --host-timeout 30s --open -oN "$OUTPUT_FILE" "$TARGET"
        fi
        
        if [ $? -eq 0 ]; then
            echo "Vulnerability scan completed successfully"
            echo "Results saved to: $OUTPUT_FILE"
        else
            echo "Error: Vulnerability scan failed"
            exit 1
        fi
        ;;
    *)
        echo "Unknown scan type: $SCAN_TYPE"
        echo "Available types: discovery, ports, vuln"
        exit 1
        ;;
esac

echo "Scan completed. Check the output file for detailed results."
echo "Tip: Use 'cat <output_file>' to view results or 'grep -i \"open\\|vulnerable\" <output_file>' for quick summary"
  

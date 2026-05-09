# Simple Threat Intelligence Scanner

import re

# Example suspicious indicators
malicious_ips = [
    "192.168.1.100",
    "45.33.32.156",
    "103.21.244.0"
]

malicious_domains = [
    "malware-site.com",
    "phishing-login.net",
    "trojan-update.org"
]

# Sample network logs
logs = [
    "User connected to 192.168.1.100",
    "Accessed website google.com",
    "Attempt to connect phishing-login.net",
    "Connection to 8.8.8.8 successful",
    "Download from trojan-update.org"
]

print("----- CTI Threat Detection -----")

for log in logs:
    for ip in malicious_ips:
        if ip in log:
            print("[!] Threat Detected: Malicious IP ->", ip)

    for domain in malicious_domains:
        if domain in log:
            print("[!] Threat Detected: Malicious Domain ->", domain)

print("Scan Completed.")
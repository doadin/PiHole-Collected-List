import requests
import re
import csv
from urllib.parse import urlparse

# URLs to fetch data from
sources = {
    "openphish": "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt",
    "phishtank": "https://data.phishtank.com/data/online-valid.csv"
}

# Output files
output_files = {
    "openphish": "openphish_hosts.txt",
    "phishtank": "phishtank_hosts.txt"
}

def extract_domain(url):
    """
    Extracts the domain from a URL, ensuring it's a valid domain.
    """
    try:
        parsed_url = urlparse(url.strip())
        domain = parsed_url.netloc  # Extract domain

        # Remove "www." prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        # Ensure it's a valid domain (no IPs, no ports)
        if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
            return domain
    except Exception:
        pass
    return None  # Return None for invalid entries

def process_openphish(url, output_file):
    """
    Downloads and processes OpenPhish data.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        domains = set()
        for line in response.text.splitlines():
            domain = extract_domain(line)
            if domain:
                domains.add(f"0.0.0.0 {domain}")

        with open(output_file, "w") as f:
            f.write("\n".join(sorted(domains)))

        print(f"OpenPhish list saved as '{output_file}' with {len(domains)} entries.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching OpenPhish data: {e}")

def process_phishtank(url, output_file):
    """
    Downloads and processes PhishTank CSV data.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        csv_lines = response.text.splitlines()
        csv_reader = csv.reader(csv_lines)

        domains = set()
        for row in csv_reader:
            if len(row) > 1:  # Ensure row has data
                domain = extract_domain(row[1])  # Phishing URL is in column 2
                if domain:
                    domains.add(f"0.0.0.0 {domain}")

        with open(output_file, "w") as f:
            f.write("\n".join(sorted(domains)))

        print(f"PhishTank list saved as '{output_file}' with {len(domains)} entries.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching PhishTank data: {e}")

# Run both processors
process_openphish(sources["openphish"], output_files["openphish"])
process_phishtank(sources["phishtank"], output_files["phishtank"])

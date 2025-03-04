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

def is_domain_only(url):
    """
    Checks if a given URL is just a domain without a path.
    """
    parsed_url = urlparse(url.strip())
    
    # If there's a netloc (domain) and no path, query, or fragment, it's a domain-only URL.
    if parsed_url.netloc and not parsed_url.path and not parsed_url.query and not parsed_url.fragment:
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]  # Remove "www."
        
        # Ensure it's a valid domain (not an IP address)
        if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
            return domain
    return None

def process_phishtank(url, output_file):
    """
    Downloads and processes PhishTank CSV data, including only verified entries that are domain-only.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        csv_lines = response.text.splitlines()
        csv_reader = csv.reader(csv_lines)

        domains = set()
        header_skipped = False  # Ensure we skip the header row

        for row in csv_reader:
            if not header_skipped:  # Skip the header row
                header_skipped = True
                continue

            if len(row) > 4 and row[4].strip().lower() == "yes":  # Only process verified URLs
                domain = is_domain_only(row[1])  # Ensure it's only a domain, not a full URL
                if domain:
                    domains.add(f"0.0.0.0 {domain}")

        with open(output_file, "w") as f:
            f.write("\n".join(sorted(domains)))

        print(f"PhishTank list saved as '{output_file}' with {len(domains)} verified domain-only entries.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching PhishTank data: {e}")

# Run both processors
process_openphish(sources["openphish"], output_files["openphish"])
process_phishtank(sources["phishtank"], output_files["phishtank"])

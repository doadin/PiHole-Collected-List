import requests
import re
from urllib.parse import urlparse

# OpenPhish public feed URL
url = "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt"

# Output file for Pi-hole blocklist
output_file = "modified_hosts.txt"

def extract_domain(line):
    """
    Extracts the domain from a line, ignoring URLs, IPs, and comments.
    """
    line = line.strip()

    # Ignore comments and empty lines
    if not line or line.startswith("#"):
        return None

    # If it's a full URL (with http/https), extract just the domain
    if line.startswith(("http://", "https://")):
        domain = urlparse(line).netloc
    else:
        domain = line  # Assume it's already a domain

    # Ensure it's a valid domain (no IPs, no paths)
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
        return domain

    return None  # Skip invalid entries

def download_and_modify(url, output_file):
    try:
        # Download the file
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad responses

        modified_lines = set()  # Use a set to avoid duplicates

        for line in response.text.splitlines():
            domain = extract_domain(line)
            if domain:
                modified_lines.add(f"0.0.0.0 {domain}")

        # Save to file
        with open(output_file, "w") as f:
            f.write("\n".join(sorted(modified_lines)))  # Sort for consistency

        print(f"File successfully saved as '{output_file}'")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

# Run the function
download_and_modify(url, output_file)

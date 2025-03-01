import requests

# URL of the text file
url = "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt"

# Name of the output file
output_file = "modified_hosts.txt"

def download_and_modify(url, output_file):
    try:
        # Download the file
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Process the content
        lines = response.text.splitlines()
        modified_lines = [f"0.0.0.0 {line}" for line in lines if line.strip()]  # Ignore empty lines

        # Save to a new file
        with open(output_file, "w") as f:
            f.write("\n".join(modified_lines))

        print(f"File successfully saved as '{output_file}'")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

# Run the function
download_and_modify(url, output_file)

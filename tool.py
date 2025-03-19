import os
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to subdomains.txt
subdomains_file = os.path.join(script_dir, "subdomains.txt")

# File to save output to
output_file = os.path.join(script_dir, "output.txt")

# List of redirect parameters to test
redirect_params = [
    "/?checkout_url={payload}",
    "/?continue={payload}",
    "/?dest={payload}",
    "/?destination={payload}",
    "/?go={payload}",
    "/?image_url={payload}",
    "/?next={payload}",
    "/?redir={payload}",
    "/?redirect_uri={payload}",
    "/?redirect_url={payload}",
     "/rediret?curl={payload}",
    "?redirect={payload}",
    "?return_path={payload}",
    "/?return_to={payload}",
    "/?return={payload}",
    "/?returnTo={payload}",
    "/?rurl={payload}",
    "/?target={payload}",
    "/?url={payload}",
    "/?view={payload}",
    "/api",
    "/redirect/"
]

# Payload to test (replace with your actual payload)
payload = "https%3A%2F%2Fwebhook.site%2F05241c42-8dd9-40b7-b184-b62a34124e17"

# Base URL with the placeholder 'x'
base_url = "https://x"

# Dictionary to store results by status code
results = {}

# Configure retry mechanism
retry_strategy = Retry(
    total=3,  # Retry 3 times
    backoff_factor=1,  # Wait 1 second between retries
    status_forcelist=[500, 502, 503, 504],  # Retry on these status codes
)

# Create a session with retry
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Read subdomains from file
try:
    with open(subdomains_file, "r") as file:
        subdomains = file.read().splitlines()
except FileNotFoundError:
    print(f"Error: File '{subdomains_file}' not found.")
    exit()

# Iterate through each subdomain
for subdomain in subdomains:
    # Replace 'x' with the current subdomain
    url = base_url.replace("x", subdomain)
    
    # Iterate through each redirect parameter
    for param in redirect_params:
        # Replace {payload} with the actual payload
        full_param = param.replace("{payload}", payload)
        
        # Construct the full URL
        test_url = f"{url}{full_param}"
        
        # Send a request to the URL with timeout and retry
        try:
            response = session.get(test_url, timeout=10)
            status_code = response.status_code
            
            # Store the result in the dictionary
            if status_code not in results:
                results[status_code] = []
            results[status_code].append(test_url)
            
            print(f"Tested {test_url} - Status Code: {status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error testing {test_url}: {e}")
        
        # Add a delay between requests to avoid rate limiting
        time.sleep(1)

# Save results to output file
with open(output_file, "w") as file:
    # Write 200 OK responses first
    if 200 in results:
        file.write("=== 200 OK ===\n")
        for url in results[200]:
            file.write(f"{url}\n")
        file.write("\n")
    
    # Write other status codes
    for status_code, urls in results.items():
        if status_code != 200:
            file.write(f"=== {status_code} ===\n")
            for url in urls:
                file.write(f"{url}\n")
            file.write("\n")

print(f"Results saved to {output_file}")
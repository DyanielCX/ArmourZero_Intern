import subprocess
import threading

# List of URLs to scan
urls = [
    "https://webapp8.wimify.xyz/login#login"
]

# Function to run a Docker scan for a URL
def scan_url(url):
    print(f"Starting scan for {url}")
    subprocess.run([
        "docker", "run", "-t", "ghcr.io/zaproxy/zaproxy:stable",
        "zap-full-scan.py", "-t", url
    ])
    print(f"Scan completed for {url}")

# Run scans in parallel using threads
threads = []
for url in urls:
    thread = threading.Thread(target=scan_url, args=(url,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All scans completed!")

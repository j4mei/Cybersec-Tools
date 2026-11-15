
#!/usr/bin/env python3
# Author: Jamei
# Tool: Fast VHost Finder

import argparse
import requests
import urllib3
import re
import uuid
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description="Jamei Fast VHost Finder")
parser.add_argument("-u", "--url", required=True, help="Target URL/IP")
parser.add_argument("-w", "--wordlist", required=True, help="VHost wordlist")
parser.add_argument("-t", "--threads", type=int, default=300)
args = parser.parse_args()

parsed = urlparse(
    args.url if "://" in args.url else "http://" + args.url
)

if not parsed.hostname:
    parser.error("Invalid target")

domain = parsed.hostname
netloc = parsed.netloc

local = threading.local()

def get_session():
    if not hasattr(local, "session"):
        local.session = requests.Session()
    return local.session

def get_info(response):
    body = response.text
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>",
        body,
        re.I | re.S
    )
    title = title_match.group(1).strip() if title_match else ""

    return response.status_code, len(response.content), title

def request_host(scheme, host):
    url = f"{scheme}://{netloc}"

    return get_session().get(
        url,
        headers={"Host": host},
        timeout=3,
        verify=False,
        allow_redirects=False
    )

# Baseline: random non-existing virtual host
def get_baseline(scheme):
    fake_host = f"jamei-{uuid.uuid4().hex[:10]}.{domain}"

    try:
        response = request_host(scheme, fake_host)
        return get_info(response)
    except requests.RequestException:
        return None

print(f"\n[JAMEI] VHost Finder")
print(f"[TARGET] {domain}")
print(f"[THREADS] {args.threads}\n")

baselines = {
    scheme: get_baseline(scheme)
    for scheme in ("http", "https")
}

for scheme, baseline in baselines.items():
    if baseline:
        print(f"[BASELINE] {scheme.upper()} | Status: {baseline[0]} | Size: {baseline[1]}")
    else:
        print(f"[SKIP] {scheme.upper()} unavailable")

def check_vhost(word, scheme):
    word = word.strip().lower()

    if not word:
        return None

    host = word if word.endswith("." + domain) else f"{word}.{domain}"
    baseline = baselines[scheme]

    if baseline is None:
        return None

    try:
        response = request_host(scheme, host)
        status, size, title = get_info(response)

        base_status, base_size, base_title = baseline

        # Compare candidate with random-host response
        different = (
            status != base_status
            or abs(size - base_size) > 80
            or title != base_title
        )

        if different:
            return f"[FOUND] {scheme}://{host} | Status: {status} | Size: {size} | Title: {title}"

    except requests.RequestException:
        pass

    return None

with open(args.wordlist, errors="ignore") as f:
    words = list(set(line.strip() for line in f if line.strip()))

tasks = [
    (word, scheme)
    for word in words
    for scheme in ("http", "https")
]

found = 0

with ThreadPoolExecutor(max_workers=args.threads) as executor:
    futures = [
        executor.submit(check_vhost, word, scheme)
        for word, scheme in tasks
    ]

    for future in as_completed(futures):
        result = future.result()
        if result:
            print(result)
            found += 1

print(f"\n[COMPLETED] Found: {found}")


#!/usr/bin/env python3

import argparse
import dns.resolver
import dns.exception
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(
    description="Fast DNS Subdomain Finder"
)

parser.add_argument("-u", "--url", required=True,
                    help="Target domain, e.g. example.com")

parser.add_argument("-w", "--wordlist", required=True)

parser.add_argument("-t", "--threads", type=int, default=300)

parser.add_argument("-o", "--output", default="found.txt")

parser.add_argument("--timeout", type=float, default=1)

args = parser.parse_args()

if not 1 <= args.threads <= 1000:
    parser.error("Threads must be between 1 and 1000")

domain = args.url.strip().lower().rstrip(".")

# DNS resolver
def check(word):
    hostname = f"{word}.{domain}"

    resolver = dns.resolver.Resolver()
    resolver.timeout = args.timeout
    resolver.lifetime = args.timeout

    try:
        answers = resolver.resolve(hostname, "A")
        ips = sorted({str(answer) for answer in answers})
        return hostname, ips

    except (dns.exception.DNSException, OSError):
        return None

# Load wordlist
try:
    with open(args.wordlist, encoding="utf-8") as f:
        words = list(dict.fromkeys(
            line.strip().lower()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ))
except FileNotFoundError:
    parser.error("Wordlist not found")

print(f"\n[+] Target: {domain}")
print(f"[+] Wordlist: {len(words)}")
print(f"[+] Threads: {args.threads}")
print(f"[+] Author: jamei")
print(f"[+] GitHub: j4mei\n")

found = []

with ThreadPoolExecutor(max_workers=args.threads) as pool:
    futures = [pool.submit(check, word) for word in words]

    for future in as_completed(futures):
        result = future.result()

        if result:
            hostname, ips = result
            print(f"[FOUND] {hostname} -> {', '.join(ips)}")
            found.append((hostname, ips))

with open(args.output, "w", encoding="utf-8") as f:
    for hostname, ips in sorted(found):
        f.write(f"{hostname} -> {', '.join(ips)}\n")

print("\n============================")
print(f"[+] Found: {len(found)}")
print(f"[+] Saved: {args.output}")
print("============================")

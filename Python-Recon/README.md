# Cybersecurity Tools

A collection of Python-based cybersecurity tools for reconnaissance, penetration testing, and security research.

## Tools

| Tool | Description |
|---|---|
| Subdomain Finder | Discover subdomains of a target domain |
| VHost Finder | Discover virtual hosts on a target web server |

## Requirements

- Python 3.x
- Required Python libraries

## Usage

### Subdomain Finder & Vhost Finder

A Python-based reconnaissance tool that discovers subdomains of a target domain using DNS queries.
A Python-based reconnaissance tool that discovers virtual hosts on a target web server using HTTP Host headers.

**Command:**

```bash
python3 subdomain.py -u example.com -w /PATH/subdomain.txt
python3 vhost.py -u example.com -w wordlist.txt
```

**Example:**

```bash
python3 subdomain.py -u example.com -w wordlists.txt
python3 vhost.py -u example.com -w wordlists.txt   
```
A Python tool that finds virtual hosts using a domain name, not an IP address.

## Disclaimer

These tools are developed for educational purposes, authorized security testing, and cybersecurity research only.
Use them only on systems you own or have permission to test.



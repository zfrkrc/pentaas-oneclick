# Changelog

All notable changes to PentaaS OneClick Scanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-17

### Added
- **7 New White Box Tools:**
  - SQLmap - SQL injection detection and exploitation
  - Commix - Command injection vulnerability scanner
  - GitTools - Exposed .git repository scanner
  - Wapiti - Web vulnerability scanner with fuzzing
  - NoSQLMap - NoSQL injection testing tool
  - Gobuster - Directory/DNS/vhost bruteforcing
  - Arachni - Scriptable web security scanner
- Enhanced report parsing for Dalfox (XSS vulnerabilities)
- Enhanced report parsing for DNSRecon (detailed DNS records)
- Troubleshooting section in README.md
- Support files (wordlist for Gobuster)

### Changed
- White Box profile now includes 17 tools (previously 10)
- Total platform tools increased to 24 (from 13)
- DNS records now show all entries instead of limiting to 10
- XSS findings now display actual vulnerability details instead of N/A values
- Updated README.md with comprehensive tool list and new features
- Improved timeout management for slow services (SQLmap, Arachni, Wapiti)

### Fixed
- Dalfox parser now correctly extracts URL, parameter, and payload information
- DNSRecon parser now groups and displays individual DNS records by type
- Docker Compose service definitions for all new tools

### Technical Details
- Added 8 new Dockerfiles in `backend/services/`
- Updated `engine.py` PROFILE_SERVICES, OUTPUT_MAPPING, and SLOW_SERVICES
- Modified `main.py` parsing logic for better vulnerability reporting
- All new tools integrated with Redis-based storage system

## [1.0.0] - 2026-01-15

### Added
- Initial release of PentaaS OneClick Scanner
- React-based frontend with modern UI
- FastAPI backend with async job processing
- Redis-based storage and queue system
- RQ Worker for background task execution
- Docker Compose orchestration
- 3 scan profiles: White Box, Gray Box, Black Box
- **Initial 13 Tools:**
  - Nmap (3 variants)
  - Nuclei (2 variants)
  - Nikto (2 variants)
  - ZAP (OWASP)
  - WPScan
  - Dirsearch
  - TestSSL
  - SSLyze
  - WhatWeb
  - Arjun
  - Dalfox
  - Wafw00f
  - DNSRecon
- HTML report generation
- Real-time scan progress tracking
- Scan history management

### Features
- Microservices architecture (100% containerized)
- Parallel tool execution
- Centralized logging via Redis
- Professional HTML reports
- RESTful API endpoints
- CORS-enabled for frontend integration

---

## Version History Summary

- **v2.0.0** (2026-01-17): Major update with 7 new tools and enhanced reporting
- **v1.0.0** (2026-01-15): Initial release with 13 core security tools

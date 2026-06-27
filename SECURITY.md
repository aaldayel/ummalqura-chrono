# Security Policy

## Reporting a Vulnerability

We take the security of the Umm al-Qura Calendar project seriously. If you
believe you have found a security vulnerability, please report it to us
privately.

**Please do not report security vulnerabilities through public GitHub issues.**

To report a security vulnerability, please open a private vulnerability report
on GitHub via the Security tab of the repository, or contact the maintainers
directly through the GitHub organization page.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |
| < 1.0   | No        |

## Security Update Process

1. The security team will acknowledge receipt of your report within 48 hours
2. We will investigate and determine the impact and severity
3. A fix will be developed and tested privately
4. A security advisory will be published alongside the fix release
5. Credit will be given to the reporter (unless anonymity is requested)

## Data Integrity

The month-length data file (`data/ummalqura-months.json`) is the single source
of truth for all calendar calculations. Its integrity is verified via a SHA-256
checksum stored in `data/ummalqura-months.sha256`. Any tampering with this file
can produce incorrect calendar conversions. Always verify the checksum before
using the library in production.

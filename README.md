# 🎮 PSN Hotmail Checker

[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Requests](https://img.shields.io/badge/Requests-v2.31+-blue?style=for-the-badge)](https://pypi.org/project/requests/)
[![Multi-Threaded](https://img.shields.io/badge/Multi--Threaded-High%20Speed-brightgreen?style=for-the-badge)](https://github.com/updh1/Psn-Hotmail-Checker)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](#)

A high-performance, multi-threaded Microsoft account checker with integrated PSN purchase detection and subscription analysis. This tool automates the login process, validates credentials, identifies 2FA-protected accounts, and scans inboxes for PlayStation Network purchase confirmations.

---

## ✨ Key Features

- **🔐 Complete Microsoft Account Verification**: Handles the full Live.com/Outlook login flow with token and cookie parsing.
- **🎯 PSN Purchase Detection**: Scans inbox for emails from PlayStation Store. Counts total orders and extracts recent transaction details (items, prices, dates).
- **💼 Subscription Detection**: Automatically identifies active Microsoft subscriptions including:
  - Xbox Game Pass Ultimate / Core / PC
  - Microsoft 365 / Office 365
  - And other Microsoft services
- **📊 Smart Account Sorting**:
  - `Game Pass` accounts highlighted in magenta/cyan
  - `Office 365` accounts highlighted in blue
  - Regular valid accounts in green
- **🧵 Advanced Multi-Threading**: Configurable thread count (1-200) for maximum performance
- **🛡️ Proxy Support**: HTTP/HTTPS proxies with automatic rotation
- **🎂 Birthday Extraction**: Automatically retrieves account holder's birth date and age when available
- **📁 Organized Results**: Automatically sorts hits into categorized files:
  - `valid.txt` - All valid accounts
  - `psn_hits.txt` - Accounts with PSN purchase history
  - `subscriptions.txt` - All accounts with active subscriptions
  - `game_pass.txt` - Accounts with Game Pass subscriptions
  - `office_365.txt` - Accounts with Office/Microsoft 365
  - `2fa.txt` - Accounts requiring two-factor authentication
  - `detailed.txt` - Complete account information with purchase history

---

## 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/updh1/Psn-Hotmail-Checker.git
   cd Psn-Hotmail-Checker
   ```
2.  **Install Dependencies**
    ```bash
    pip install requests
    ```

---

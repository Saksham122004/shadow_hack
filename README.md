# 🛡️ Shadow Hack

### Python-Based Flask Security Testing Tool

A Python-based Flask application featuring customizable web templates, browser interaction routines, session logging, and optional Cloudflare/Ngrok tunneling.

Designed for cybersecurity education, authorized security testing, and defensive code analysis.

---

## 🎬 Demo Preview

<p align="center">
  <a href="https://github.com/Saksham122004/shadow_hack/blob/main/images/demo.mp4">
    <img src="https://img.shields.io/badge/▶-Watch%20Project%20Demo-blue?style=for-the-badge" alt="Watch Demo">
  </a>
</p>

**Demo Video:** [View Shadow Hack Demo](https://github.com/Saksham122004/shadow_hack/blob/main/images/demo.mp4)

---

## 📌 Overview

Shadow Hack is a Python-based Flask application that combines a web interface with a terminal-based configuration menu.

The application contains themed web templates, browser interaction routines, local file storage, JSON event logging, and optional tunnel integrations.

It is intended for controlled security research, source-code analysis, and cybersecurity awareness demonstrations.

> ⚠️ **Security Notice:** The source includes functionality that may request access to camera, microphone, location, contacts, selected media, and device information. Use only with explicit informed consent and authorization.

---

## ✨ Features

* Flask-based web server
* Customizable web templates
* Browser and device information handling
* Session and event logging
* JSON-based record storage
* Local file management
* Configurable application settings
* Optional Cloudflare Tunnel integration
* Optional Ngrok integration
* Optional nport integration
* Terminal-based configuration menu
* Local dashboard functionality

---

## 🧰 Technologies Used

| Technology        | Purpose              |
| ----------------- | -------------------- |
| Python            | Core application     |
| Flask             | Web server           |
| HTML              | Web interface        |
| CSS               | Styling              |
| JavaScript        | Browser interactions |
| JSON              | Event logging        |
| Cloudflare Tunnel | Optional tunneling   |
| Ngrok             | Optional tunneling   |

---

## 📂 Project Structure

```text
shadow_hack/
│
├── images/
│   └── demo.mp4
│
├── shadow_hack.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Saksham122004/shadow_hack.git
```

### 2. Navigate to Project

```bash
cd shadow_hack
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
python shadow_hack.py
```

Run only in an isolated, authorized test environment.

---

## 🔍 Security Review

The source contains several security-sensitive behaviors:

* Web pages may use misleading themes to request browser permissions.
* Browser data and media may be transmitted to the Flask server.
* Public tunnel integrations can expose the application externally.
* Local storage may contain sensitive information.
* Upload endpoints require appropriate authentication and input validation.
* Encryption and data-retention controls should be considered.

Some interface claims, such as exact phone tracking or dark-web scanning, are not demonstrated by the browser routines described in this review.

---

## 🔐 Safe Usage

* Use an isolated lab environment.
* Use synthetic data and test accounts.
* Do not expose the application through public tunnels during code review.
* Do not access another person's device or information without explicit authorization.
* Use local mock data for security awareness demonstrations.
* Restrict access to any test artifacts and remove them after analysis.

---

## 🎯 Project Purpose

This repository is intended for:

* Cybersecurity education
* Python and Flask code review
* Web application security analysis
* Browser permission security awareness
* Defensive security research
* Controlled laboratory testing

---

## ⚖️ Disclaimer

This project is documented for educational and defensive cybersecurity research purposes.

Any testing must be performed with explicit authorization, informed consent, and within a controlled environment.

The repository owner is not responsible for unauthorized access, privacy violations, misuse, or damage resulting from improper use.

---

## 👨‍💻 Developer

**Saksham Katiyar**

GitHub: [@Saksham122004](https://github.com/Saksham122004)

---

<p align="center">
  <b>Built for Cybersecurity Research 🛡️</b>
</p>

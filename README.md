# 🚦 TrafficLog — Smart Traffic Violation Logger

A modern Flask web app for traffic authorities to digitally log, track, and manage road violations with QR-enabled challans.

---

## ⚡ Quick Start

### 1. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

### 4. Open Browser
```
http://localhost:5000
```

---

## 🔐 Default Login
| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

---

## 📁 Project Structure
```
traffic_logger/
├── app.py                  ← Flask app + routes
├── models.py               ← SQLAlchemy models
├── requirements.txt
├── README.md
├── static/
│   ├── css/style.css       ← Dark amber theme
│   ├── js/main.js          ← Animations + live preview
│   └── qrcodes/            ← Auto-generated QR codes
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── add_violation.html
    ├── history.html
    ├── challan.html
    └── status.html
```

---

## ✅ Features
- Add violation records (vehicle, type, location, date, fine)
- QR code auto-generated per challan
- Scan QR → public status page (no login needed)
- Search & filter violation history
- Mark violations as Paid
- Printable challan receipts
- Animated dark amber UI

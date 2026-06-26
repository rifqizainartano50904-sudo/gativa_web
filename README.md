<div align="center">
  <h1>🏥 Gativa Web Dashboard</h1>
  <p><strong>Admin Dashboard for GATIVA Mobile Application</strong></p>
</div>

---

## 📖 Overview
**Gativa Web** is a powerful administrative dashboard built with **Flask** and **Firebase Firestore**. It is designed to manage and monitor users (patients and healthcare workers) for the GARDA mobile application ecosystem. 

With a clean interface and robust backend, Gativa Web allows administrators to oversee user registrations, edit user details, and ensure smooth operations within the healthcare platform.

## ✨ Features
- **🔐 Secure Authentication:** Admin login with Flask-Login and password hashing via Flask-Bcrypt.
- **📊 Real-time Dashboard:** View statistics and total counts of registered patients and health workers.
- **🗄️ Firestore Integration:** Seamlessly fetch, update, and manage data from Firebase Firestore subcollections (`pasien` and `tenaga_kesehatan`).
- **👥 User Management:** Admin tools to view, edit, and update patient and healthcare worker credentials (name, email, password).
- **✉️ Email OTP (Optional):** Integrated with Flask-Mail for OTP functionalities.

## 🛠️ Technology Stack
- **Backend:** Python 3, Flask, Flask-Login, Flask-Bcrypt, Flask-SocketIO, Flask-Mail
- **Database:** Firebase Admin SDK (Firestore)
- **Frontend:** HTML, CSS (Templates), Jinja2
- **Environment:** Virtualenv

## 🚀 Getting Started

### Prerequisites
1. Python 3.x installed
2. A Firebase project with Firestore enabled.
3. Your Firebase service account key.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rifqizainartano50904-sudo/gativa_web.git
   cd gativa_web
   ```

2. **Set up Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Firebase:**
   Place your `serviceAccountKey.json` file in the root directory of the project. This file is required to connect the Flask app to your Firestore database.

5. **Run the Application:**
   ```bash
   python run.py
   ```
   The server will start on `http://127.0.0.1:5000`.

## 📂 Project Structure
```text
gativa_web/
├── app/
│   ├── api/            # API routes
│   ├── auth/           # Authentication routes and logic
│   ├── main/           # Main dashboard and user management routes
│   ├── static/         # CSS, JS, Images
│   ├── templates/      # HTML Jinja2 templates
│   ├── __init__.py     # App factory and initialization
│   └── models.py       # User models
├── venv/               # Virtual environment
├── config.py           # Application configuration settings
├── requirements.txt    # Python dependencies
├── run.py              # Main entry point to start the app
└── serviceAccountKey.json # Firebase credentials (DO NOT COMMIT)
```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.

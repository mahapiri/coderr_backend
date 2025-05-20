# Coderr Backend – Django REST API

Coderr Backend is a RESTful API built with **Django** and **Django REST Framework (DRF)**. It serves as the backend for the Coderr project.

This repository is intended to work alongside the [Coderr Frontend](https://github.com/mahapiri/coderr_frontend), providing all required backend functionality.

---

## 🧠 Special Features

- 🔄 **API-First Approach**: Clean and consistent endpoints for easy integration with any frontend technology (Vanilla JS, React, Angular, etc.).
- 🔐 **User Authentication**: Supports user registration and login.
- 📦 **Simple Database Setup**: Uses SQLite by default for fast local development; easily switchable to PostgreSQL for production environments.

---

## 📦 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/mahapiri/coderr_backend.git
cd coderr_backend

# Create a virtual environment
python -m venv env
source env/bin/activate  # On Windows: "env\Scripts\activate"

# Install dependencies
pip install -r requirements.txt
```

### 🔐 Environment Setup

This project uses environment variables for configuration. Create a `.env` file in the project root with the following content:

```bash
# Create .env-file with SECRET_KEY
echo SECRET_KEY="Key" > .env
```

Replace "Key" with the actual secret key value that will be provided to you.

### 🛢️ Database and Static Files Setup

```bash
# Apply migrations
python manage.py migrate

# Run the server
python manage.py runserver
```

### 👑 Admin Access Setup

Once the project is running, you can register as an admin user to access the Django admin interface:

1. Create a superuser account:
    ```bash
    python manage.py createsuperuser
    ```
2. Complete the prompts for username, email, and password.
3. Visit:
    ```
    http://127.0.0.1:8000/admin/
    ```
4. Log in with your superuser credentials.

---

## 🚀 API Documentation

Once the server is running, API documentation is available at:
```
http://localhost:8000/api/schema/redoc/
```

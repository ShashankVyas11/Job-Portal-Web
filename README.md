
# 🧑‍💼 Job Portal Web Application (Flask + SQLite)

A full-featured job portal web application built using **Flask**, **SQLite**, **Bootstrap**, and **Jinja2**. This platform allows **Job Seekers** to search/apply for jobs, and **Employers** to post job openings. An **Admin** dashboard is also available to manage users and job listings.

---

## 🚀 Features

### 👥 User Roles:
- **Job Seekers**: Register, log in, search/filter jobs, apply, upload resume, view applied jobs.
- **Employers**: Register, log in, post jobs, view applicants, reject/delete applications.
- **Admin**: Manage all users and jobs via a dedicated dashboard.

### 🛠 Functionality:
- User authentication & authorization (Flask-Login + Bcrypt)
- Job posting with filters (category, location, experience)
- Resume upload for job seekers (PDF/docx)
- Application tracking & status updates
- Email notifications via SMTP (SendGrid or similar)
- SQLite database integration with SQLAlchemy ORM
- Responsive UI with Bootstrap

---

## 🧰 Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Bcrypt, Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2
- **Database**: SQLite
- **Deployment**: Render
- **Email**: SMTP using `smtplib` and `email.mime`

---

## 📁 Project Structure

```
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
├── run.py
├── create_db.py
├── requirements.txt
├── README.md
└── jobportal.db
```

---

## ⚙️ Installation & Setup

### ✅ Prerequisites:
- Python 3.9 or above
- pip

### 📦 Steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShashankVyas11/Job_Portal_Web.git
   cd Job_Portal_Web
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables (for deployment or email)**
   ```bash
   # .env or manually
   SECRET_KEY=your-secret-key
   ```

5. **Create database**
   ```bash
   python create_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```



---

## 🤝 Acknowledgements

- Flask Documentation
- Bootstrap 5
- SendGrid Email API
- Render Deployment Platform

---


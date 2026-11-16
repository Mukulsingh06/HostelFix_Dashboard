# HostelFix — Hostel Maintenance Management System

A web application for managing hostel maintenance complaints in a university setting. Built with Django (Python).

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1-green?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-CDN-38B2AC?logo=tailwind-css&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?logo=chartdotjs&logoColor=white)

---

## 📖 What This Project Does

HostelFix is a **Hostel Maintenance Management System** that allows:

- **Students** to submit maintenance complaints (e.g., broken fan, leaking tap) and track their status
- **Wardens/Admins** to view all complaints, assign them to technicians, and monitor performance
- **Technicians** to see their assigned tasks, update progress, and mark issues as resolved

Think of it like a **help desk / ticketing system** — but specifically for a university hostel.

---

## 🧑‍🤝‍🧑 Three User Roles

| Role | What They Can Do |
|------|-----------------|
| **Student** | Submit complaints with photos, track status with a visual progress bar, rate the service when fixed |
| **Warden (Admin)** | See all complaints, view charts & analytics, assign work to technicians, manage urgency levels |
| **Technician** | See assigned tasks sorted by priority, update status (In Progress → Resolved), add resolution notes |

---

## 🛠️ Technologies Used (Explained Simply)

| Technology | What It Is | Why We Use It |
|-----------|-----------|---------------|
| **Python** | A programming language | The main language this project is written in |
| **Django** | A web framework (like a toolkit for building websites) | Handles the backend — user login, database, page routing |
| **SQLite** | A lightweight database | Stores all the data (users, complaints, etc.) in a single file |
| **HTML** | The language for web page structure | Creates the web pages you see in the browser |
| **Tailwind CSS** | A CSS framework (loaded from CDN) | Makes the website look modern and beautiful |
| **Chart.js** | A JavaScript charting library (loaded from CDN) | Draws the pie chart and bar chart on the admin dashboard |
| **JavaScript (Fetch API)** | Browser scripting language | Updates ticket status and comments without reloading the page |

> **What is a CDN?** — A CDN (Content Delivery Network) means we load Tailwind CSS and Chart.js directly from the internet, so we don't need to install them locally.

---

## 📂 Project Structure (What Each File Does)

```
hostelfix_project/
│
├── manage.py                  ← Command-line tool to run the project
├── requirements.txt           ← List of Python packages needed
├── db.sqlite3                 ← The database file (auto-created, DO NOT upload to GitHub)
│
├── hostelfix_project/         ← Project configuration folder
│   ├── settings.py            ← Main settings (database, installed apps, etc.)
│   ├── urls.py                ← Maps website URLs to the correct pages
│   └── wsgi.py                ← Entry point for web servers (you won't touch this)
│
├── maintenance/               ← The main app (all the actual code)
│   ├── models.py              ← Defines the database tables (User, Complaint, etc.)
│   ├── views.py               ← The logic — what happens when you visit a page
│   ├── urls.py                ← Maps URLs specific to this app
│   ├── forms.py               ← Defines forms (login form, complaint form, etc.)
│   ├── admin.py               ← Registers models in Django's built-in admin panel
│   │
│   ├── templates/maintenance/ ← HTML files (the web pages)
│   │   ├── base.html              ← Main layout (sidebar, header — shared by all pages)
│   │   ├── login.html             ← Login page with demo login buttons
│   │   ├── register.html          ← Student registration page
│   │   ├── student_dashboard.html ← Student's personal dashboard
│   │   ├── warden_dashboard.html  ← Admin dashboard with charts
│   │   ├── technician_dashboard.html ← Technician's task queue
│   │   ├── complaint_form.html    ← Form to submit a new complaint
│   │   └── complaint_detail.html  ← Detailed view of a single complaint
│   │
│   ├── static/maintenance/css/
│   │   └── custom.css         ← Custom styles (sidebar, toast notifications, stepper)
│   │
│   ├── templatetags/
│   │   └── maintenance_tags.py ← Custom template filters (status colors, icons)
│   │
│   └── management/commands/
│       └── seed_hostelfix.py  ← Script to fill the database with demo data
│
└── media/                     ← Where uploaded images are stored (DO NOT upload to GitHub)
```

---

## 🚀 How to Run This Project

### Prerequisites

Make sure you have **Python 3.10 or higher** installed.  
Check by opening a terminal and typing:
```bash
python --version
```

### Step-by-Step Setup

**1. Open a terminal (Command Prompt / PowerShell / VS Code Terminal)**

**2. Navigate to the project folder:**
```bash
cd "path\to\hostelfix_project"
```

**3. Install required packages:**
```bash
pip install django Pillow
```
> `django` is the web framework. `Pillow` is needed for image uploads.

**4. Set up the database:**
```bash
python manage.py migrate
```
> This creates all the database tables.

**5. Load demo data:**
```bash
python manage.py seed_hostelfix
```
> This creates demo users and 12 sample complaints so you can test immediately.

**6. Start the server:**
```bash
python manage.py runserver
```

**7. Open your browser and go to:**
```
http://127.0.0.1:8000
```

**8. To stop the server:** Press `Ctrl + C` in the terminal.

---

## 🔑 Demo Login Credentials

The login page has **Quick Demo Login** buttons, or you can type these manually:

| Role | Username | Password |
|------|----------|----------|
| Warden (Admin) | `admin` | `password123` |
| Technician (Electrical) | `tech_elec` | `password123` |
| Technician (Plumbing) | `tech_plumb` | `password123` |
| Technician (Wi-Fi) | `tech_wifi` | `password123` |
| Student 1 (Block A, Room 204) | `student1` | `password123` |
| Student 2 (Block B, Room 112) | `student2` | `password123` |

---

## ✨ Features

### Student Dashboard
- 📊 KPI cards showing Total, Pending, In Progress, and Resolved complaints
- 📝 Submit new complaints with category, urgency, description, and photo upload
- 🔍 Search and filter complaints by status
- ⭐ Rate and review the service when a complaint is resolved

### Warden/Admin Dashboard
- 📈 Doughnut chart (complaints by category) and Bar chart (weekly volume)
- 🚨 SLA breach alerts for tickets open more than 48 hours
- 👷 Technician workload cards (active tasks, completed, average rating)
- 🔧 Assign/reassign complaints to technicians
- 📋 Filter by Status, Category, Urgency, and Hostel Block

### Ticket Detail Page
- 🚦 Visual 4-stage status stepper (Registered → Assigned → In Progress → Resolved)
- 📜 Activity timeline showing every status change with timestamps
- 💬 Threaded comments between students, wardens, and technicians
- ⚡ AJAX updates (status changes without page reload)
- ⭐ Star rating modal for students to confirm resolution

### General
- 🌙 Dark/Light theme toggle
- 📱 Responsive design (works on mobile)
- 🔐 Role-based access control (users only see what they're allowed to)
- 🍞 Toast notifications for every action

---

## 📊 Database Schema (Simplified)

| Table | What It Stores |
|-------|---------------|
| **User** | Username, password, email (built-in Django table) |
| **UserProfile** | Role (student/admin/technician), hostel block, room number, phone, specialization |
| **Complaint** | Ticket ID, title, description, category, urgency, status, assigned technician, photos, rating |
| **ComplaintTimeline** | Audit log — who changed what status and when |
| **ComplaintComment** | Comments/messages on a complaint between users |

---

## 🗑️ How to Reset Everything

If you want to start fresh:
```bash
python manage.py flush --no-input
python manage.py seed_hostelfix
```

---

## 📌 Common Issues

| Problem | Solution |
|---------|----------|
| `Pillow is not installed` | Run: `pip install Pillow` |
| `No module named 'django'` | Run: `pip install django` |
| Port 8000 already in use | Run: `python manage.py runserver 8080` (uses port 8080 instead) |
| Database errors after editing models | Run: `python manage.py makemigrations maintenance` then `python manage.py migrate` |

---

## 📄 License

This project is for educational purposes.

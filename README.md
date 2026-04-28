# CRM-Based College Event Management System with Lead Conversion & Admin Dashboard
A role-based CRM-inspired web application for managing college events, student registrations, lead tracking, and admin monitoring.
This project is designed to simulate real-world CRM concepts like lead capture, lead conversion, admin authentication, and registration workflow automation using HTML, CSS, and JavaScript.

---
## 🚀 Features
### 👩‍🎓 Student Portal
* View available college events
* Register for events
* Enter name and phone number
* Incomplete/invalid registration automatically saved as Lead

### 👨‍💼 Admin Dashboard
* Secure admin login using session-based authentication
* Protected CRM dashboard access
* View total events, leads, and registrations
* Monitor lead conversion lifecycle
* Track student registrations per event

### 🔥 CRM Features
* Lead generation from incomplete registrations
* Lead conversion tracking
* Duplicate prevention using unique user key
* Registration confirmation simulation
* LocalStorage-based persistent data management

---
## 🛠️ Tech Stack

* HTML5
* CSS3
* JavaScript (Vanilla JS)
* LocalStorage
* SessionStorage
---

## 📁 Project Structure
college-event-crm
index.html      (Student Portal)
login.html      (Admin Login)
admin.html      (Protected CRM Dashboard)6
style.css
script.js


## 🔐 Admin Login Credentials

### Username:
admin
### Password:
1234

---

## ⚙️ How It Works

### Step 1: Student Registration
Students can:
* View events
* Register using name + phone number
  
### Step 2: Lead Handling
If:
* phone number is missing
* OR phone number is invalid
The system stores the student as a **Lead**

### Step 3: Lead Conversion
When the same student later completes valid registration:
* Lead status changes to **Converted**
* Registration record is created

### Step 4: Admin Monitoring
Admin can:
* Login securely
* Access CRM dashboard
* Track Leads + Registrations + Converted Leads

## 💡 CRM Logic Implemented
Incomplete Registration → Lead

Valid Registration → Registration

Existing Lead + Valid Registration → Converted Lead


LinkedIn: Your LinkedIn Profile Link


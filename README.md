
# DESD Portal

**Live demo:**  
🔗 http://paulamie.pythonanywhere.com

Accessible from any device with an internet connection.

---

## 📦 Overview

**DESD Portal** is a Django-based web application deployed using Docker. The platform is designed to support user interaction, content management, and backend data handling. It is fully containerised using `docker-compose` and easily deployable both locally and to cloud platforms like PythonAnywhere.

---

## 🚀 Features

- Full-stack **Django** web application  
- Secure **user authentication** with registration and session management  
- Pages include: **Events**, **Posts**, **Communities**, **Societies**,  **User Profiles**  and **Friends**
- **Modular project structure** for easy maintenance and scalability  
- **Dockerised** for streamlined setup and deployment  
- Uses **MySQL** as the backend database  
- Built-in **admin interface** for managing models and content  
- **Ready for deployment** on platforms like PythonAnywhere  

---

## 🐳 Docker Setup Instructions

### 1. Remove old containers and volumes (if needed)
```bash
docker-compose down -v
```

### 2. Build and start fresh containers
```bash
docker-compose up --build
```

### 3. Run migrations
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## 💡 Development

To run the project locally without Docker:

1. Install dependencies:
   ```bash
   pip install -r project/requirements.txt
   ```

2. Run migrations:
   ```bash
   python project/manage.py makemigrations
   python project/manage.py migrate
   ```

3. Start the server:
   ```bash
   python project/manage.py runserver
   ```

Visit `http://localhost:8000` in your browser.

---

## 📁 Project Structure

```
DESD-main/
├── project/
│   ├── manage.py
│   ├── project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── static/
│   ├── templates/
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🛠️ Tools & Tech

- **Python 3**
- **Django**
- **Docker & Docker Compose**
- **MySQL**
- **HTML and CSS**
- **Jacascript**
- **PythonAnywhere (for hosting)**

---

## ✅ Future Improvements

- Integrate cloud storage or database backups
- Include unit testing and CI/CD setup
- Improve frontend responsiveness

---

Part of a cloud deployment and system development coursework.


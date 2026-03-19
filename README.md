# Videoflix Backend

**Videoflix Backend** is the server-side component of a video streaming platform where users can watch a collection of uploaded videos or movies.  
Videos are available in multiple resolutions (480p, 720p, 1080p) and streamed in **HLS format**, enabling adaptive streaming experiences.

---

## Technologies
- **Python 3.11+**
- **Django 5**
- **Django REST Framework**
- **PostgreSQL** (Database)
- **Redis & RQ** (Asynchronous tasks / video processing)
- **Gunicorn** (Production WSGI server)
- **Pillow** (Image processing)

---

## Features
- User registration & authentication (JWT)
- RESTful API for video and media management
- Automatic HLS video processing (480p, 720p, 1080p)
- Adaptive streaming with `.m3u8` playlists and `.ts` segments
- Media files served during development (CORS enabled)
- Asynchronous tasks via Django-RQ for video transcoding

---

## Installation & Setup

## 1. Clone the repository
```bash
git clone https://github.com/LarsThoennes/Videoflix_Backend
cd Videoflix_Backend
```

## 2. Set up environment variables
Copy the template .env.template to .env and fill in your own parameters:
```bash
cp .env.template .env
```

## 3. Build Docker images
```bash
docker-compose build
```
## 4. Start the services
```bash
docker-compose up
```
This will start:
- Backend server (Django)
- PostgreSQL database
- Redis queue
## The server will start at:
```bash
http://127.0.0.1:8000/
```
## 5. Apply migrations inside the container
```bash
docker-compose exec web python manage.py makemmigrations
```
## 6. Apply migrations inside the container
```bash
docker-compose exec web python manage.py migrate
```

## 7. Access the Django Admin Panel
You can open the admin interface at:
```bash
http://127.0.0.1:8000/admin
```
A superuser with the username admin and passwod adminpassword is already available for login.

## (Optional) 8. Create Super User

```bash
docker-compose exec web python manage.py createsuperuser
```


## Frondend Repository 
The corresponding frontend application for Videoflix can be found here:
https://github.com/Developer-Akademie-Backendkurs/project.Videoflix

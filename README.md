# Task Management Application

A Django-based task management system with user roles and JWT authentication.

## Features

- JWT Authentication for secure API access.
- Role-based access for SuperAdmin, Admin, and User.
- Admin panel with restricted controls.
- Task management: Create, assign, update, and report tasks.
- Users can submit task completion reports and worked hours.

## API Endpoints

- `GET /api/tasks/tasks/`: List user’s tasks.
- `PUT /api/tasks/tasks/{id}/`: Update task status and add a report.
- `GET /api/tasks/tasks/{id}/report`: View completion report for a task.

## Tech Stack

- Python 3.9+
- Django 4.2+
- Django REST Framework
- SQLite (Default database)
- drf-yasg (API Docs)
- JWT Authentication

`/login` get admin panel 

## Setup Instructions

```bash
# Clone the project
git clone https://github.com/your-username/task-management-app.git
cd task-management-app

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run management command
python manage.py create_user_roles

# Run migrations and start server
python manage.py migrate
python manage.py runserver



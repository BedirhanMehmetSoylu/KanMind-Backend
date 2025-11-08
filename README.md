# KanMind Backend

This is the backend for **KanMind**, a project and task management application.

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Technologies](#technologies)
- [License](#license)

---

## Features

- Create and manage **Boards**
- Create, assign, and review **Tasks**
- Add **Comments** to tasks
- Dashboard with task statistics:
  - Tasks assigned to you
  - Tasks for review
  - Urgent tasks
- REST API ready for frontend or external use

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/BedirhanMehmetSoylu/KanMind-Backend
cd kanmind-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/registration/` – Register a new user
- `POST /api/login/` – Login user
- `GET /api/email-check/` – Check if an email is already registered

### Boards
- `GET /api/boards/` – List all accessible boards
- `POST /api/boards/` – Create a new board
- `GET /api/boards/<int:pk>/` – Retrieve board details
- `PATCH /api/boards/<int:pk>/` – Update a board
- `DELETE /api/boards/<int:pk>/` – Delete a board

### Tasks
- `GET /api/tasks/assigned-to-me/` – List tasks assigned to the user
- `GET /api/tasks/reviewing/` – List tasks the user is reviewing
- `GET /api/boards/<int:board_id>/tasks/` – List tasks in a board
- `POST /api/tasks/` – Create a new task
- `GET /api/tasks/<int:pk>/` – Retrieve task details
- `PATCH /api/tasks/<int:pk>/` – Update a task
- `DELETE /api/tasks/<int:pk>/` – Delete a task

### Comments
- `GET /api/tasks/<int:task_id>/comments/` – List comments for a task
- `POST /api/tasks/<int:task_id>/comments/` – Add a comment
- `DELETE /api/tasks/<int:task_id>/comments/<int:pk>/` – Delete a comment

### Dashboard
- `GET /api/dashboard/` – Retrieve dashboard statistics

## Authentication

- Uses Django REST Framework authentication

- Supports token-based authentication via Simple JWT

- Most endpoints require authenticated users

## Technologies

- Python 3.13.5

- Django 5.2.7

- Django REST Framework

- PostgreSQL / SQLite (depending on environment)

- JWT authentication

## License
This project is licensed under the MIT License.

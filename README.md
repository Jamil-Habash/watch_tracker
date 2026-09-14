# 🎬 Watch Tracker

A Django web app for logging and organizing the movies, TV shows, and anime you watch — track status, ratings, and notes for everything in your personal watchlist.

## Features

- **User accounts** — sign up and log in to keep a private, personal log
- **Track anything** — add movies, TV shows, or anime with a single entry type
- **Status tracking** — mark titles as Watching, Completed, Planned, or Dropped
- **Ratings & notes** — rate what you've watched and jot down personal notes
- **Search & filter** — quickly find entries by title or narrow the list by status
- **Responsive UI** — a custom-styled interface that works on desktop and mobile

## Tech Stack

- **Backend:** Django (Python)
- **Database:** SQLite (default, easily swappable for Postgres/MySQL in production)
- **Frontend:** HTML templates, vanilla JavaScript, custom CSS
- **WSGI/ASGI:** Gunicorn-ready via `wsgi.py` / `asgi.py`

## Project Structure

```
watch_tracker/
├── tracker/                  # Main Django app
│   ├── migrations/           # Database migrations
│   ├── static/
│   │   ├── script.js         # Frontend interactivity
│   │   └── style.css         # App styling
│   ├── templates/
│   │   ├── index.html        # Watch log dashboard
│   │   ├── log_in.html       # Login page
│   │   └── signup.html       # Signup page
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                 # App configuration
│   ├── models.py             # Data models
│   ├── tests.py               # Unit tests
│   ├── urls.py                 # App-level URL routing
│   └── views.py                # View logic
├── watch_tracker/            # Project configuration
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py                 # Project-level URL routing
│   └── wsgi.py
├── build.sh                   # Build/deploy script
├── db.sqlite3                 # Default local database
├── manage.py                  # Django management CLI
└── requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/watch_tracker.git
   cd watch_tracker
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. Open your browser to `http://127.0.0.1:8000/`

## Deployment

The included `build.sh` script can be used to automate build steps (installing dependencies, collecting static files, and running migrations) for platform deployments such as Render or Railway.

```bash
./build.sh
```

Make sure to set `DEBUG = False` and configure `ALLOWED_HOSTS`, along with a production-grade database, in `settings.py` before deploying.

## Running Tests

```bash
python manage.py test
```

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

# 🎬 Watch Tracker

A Django web application for logging, organizing, and discovering the movies, TV shows, and anime you watch. Users can manage their personal watchlist, track viewing status, add ratings and notes, and get AI-powered recommendations through a Groq-powered assistant.

## Features

- **User accounts** — Sign up and log in to maintain a personal watchlist
- **Track anything** — Add movies, TV shows, or anime to your collection
- **Status tracking** — Mark titles as Watching, Completed, Planned, or Dropped
- **Ratings & notes** — Rate titles and add personal notes
- **Search & filter** — Quickly find entries by title or filter them by status
- **AI recommendations** — Get personalized recommendations based on your watchlist and preferences
- **AI chatbot** — Interact with an AI assistant for movie, TV show, and anime recommendations
- **Responsive UI** — Custom-styled interface designed for desktop and mobile
- **Admin panel** — Manage application data through Django's built-in admin interface

## Tech Stack

- **Backend:** Django (Python)
- **Database:** SQLite
- **Frontend:** HTML templates, vanilla JavaScript, custom CSS
- **AI:** Groq API
- **Authentication:** Django authentication system
- **Deployment:** Gunicorn-ready with WSGI/ASGI configuration

## Project Structure

```text
watch_tracker/
├── tracker/
│   ├── migrations/           # Database migrations
│   ├── static/
│   │   ├── js/               # JavaScript assets
│   │   └── css/              # CSS assets
│   ├── templates/             # HTML templates
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                 # App configuration
│   ├── models.py               # Database models
│   ├── services.py             # AI/Groq API integration
│   ├── tests.py                # Unit tests
│   ├── urls.py                  # App-level URL routing
│   └── views.py                 # View logic
│
├── watch_tracker/
│   ├── __init__.py
│   ├── asgi.py                # ASGI configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Project-level URL routing
│   └── wsgi.py                # WSGI configuration
│
├── build.sh                   # Build/deployment script
├── db.sqlite3                 # Local SQLite database
├── manage.py                  # Django management CLI
├── requirements.txt           # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jamil-Habash/watch_tracker.git
   cd watch_tracker
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   ```
   On Windows:
   ```powershell
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file based on `.env.example` and add the required configuration:
   ```text
   GROQ_API_KEY=your_api_key_here
   ```
   **Never commit `.env` or API keys to the repository.**

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin panel access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. Open your browser at:
   ```text
   http://127.0.0.1:8000/
   ```

## 🤖 AI Features

Watch Tracker integrates the **Groq API** to provide AI-powered functionality, handled through `services.py`.

The AI functionality includes:

- Personalized movie recommendations
- TV show recommendations
- Anime recommendations
- Recommendations based on the user's existing watchlist
- Conversational interaction with the AI assistant

The Groq API key is loaded through an environment variable and is never stored directly in the source code.

## 🔐 Environment Variables

Sensitive configuration is managed through environment variables.

Create a `.env` file locally:
```env
GROQ_API_KEY=your_api_key_here
```

The `.env` file is intentionally excluded from version control. An `.env.example` file is included to show the required configuration without exposing secrets.

## Deployment

The included `build.sh` script can automate common deployment steps such as:

- Installing dependencies
- Collecting static files
- Running database migrations

```bash
./build.sh
```

The application is configured to support production deployment using Gunicorn and Django's WSGI/ASGI configuration.

Before deploying, make sure to:

- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Configure production environment variables
- Use an appropriate production database
- Keep API keys and other secrets outside the repository

## Running Tests

```bash
python manage.py test
```

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes
   ```bash
   git commit -m "Add your feature"
   ```
4. Push the branch
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

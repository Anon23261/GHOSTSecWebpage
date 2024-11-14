# GhostSec - Cybersecurity Learning Platform

A Flask-based web application for cybersecurity education and training.

## Features

- User Authentication (Login/Register)
- User Dashboard
- Email Integration
- Rate Limiting
- Secure Password Handling
- Error Logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ghostsec.git
cd ghostsec
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

5. Initialize the database:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
ghostsec/
├── app.py              # Application initialization
├── models.py           # Database models
├── routes.py           # Route handlers
├── requirements.txt    # Project dependencies
├── .env               # Environment variables
├── instance/          # Instance-specific files
├── logs/              # Application logs
├── static/            # Static files (CSS, JS)
├── templates/         # HTML templates
└── uploads/           # User uploads
```

## Development

1. Set up environment variables in `.env`:
```
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///ghostsec.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

2. Run in development mode:
```bash
python app.py
```

## License

MIT License

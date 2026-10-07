# Igede Language Data Collection

A community-driven web application for collecting and
reviewing Igede language data.

## Current Features

- Submit Igede language contributions
- Backend validation
- SQLite storage
- Review pending submissions
- Verify or reject submissions
- Display verified language data publicly

## Setup

Clone the repository and enter the project directory.

Create a virtual environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Initialize the database:

    python database.py

Start the application:

    python app.py

## Routes

- `/` — Home
- `/submit` — Submit language data
- `/dataset` — View verified language data
- `/review` — Review pending submissions

## Current Limitations

The review interface does not yet have production-ready
authentication and authorization.

Do not deploy the review interface publicly without
appropriate access control.
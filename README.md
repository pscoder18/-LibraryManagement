# Library Management System

A Flask-based Library Management System with MySQL backend.

## Features
- Admin and Member authentication.
- Book management (Add, Update, Delete).
- Member management.
- Borrowing and returning books.
- Statistical dashboard.
- **Secure configuration** using environment variables.

## Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database:
   - Import the `mysql/sql.sql` file into your MySQL server.
6. Configure environment variables:
   - Copy `.env.example` to a new file named `.env`.
   - Update the values in `.env` with your database credentials and a secret key.

## Running the App
```bash
python app.py
```

# Library Management System

A Flask-based Library Management System with MySQL backend.

## Features
- Admin and Member authentication.
- Book management (Add, Update, Delete).
- Member management.
- Borrowing and returning books.
- Statistical dashboard.

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
   - Update the database credentials in `app.py`.

## Running the App
```bash
python app.py
```

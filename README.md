# Case Management System

[![Website](https://casemanagement.streamlit.app/)](https://casemanagement.streamlit.app/)

## Overview

The **Case Management System** is a streamlined application designed to manage legal cases efficiently. Built with Streamlit and powered by an SQLite database, this system allows administrators and staff to add, edit, search, and maintain case records with ease.

## Features

- **User Authentication**: Secure login system with roles for administrators and staff.
- **Case Management**: Add, edit, delete, and search cases across multiple fields.
- **Analytics Dashboard**: Real-time metrics on total cases, active cases, districts involved, and recent additions.
- **Logging**: Action logging for tracking changes and user activities.
- **Backup Management**: Create and restore database backups with automatic backups after multiple changes.
- **Responsive Design**: Optimized for various screen sizes with a user-friendly interface.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/a3ro-dev/case-management-system.git
    cd case-management-system
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Environment Variables**

    Create a `.env` file in the root directory and add the following:

    ```env
    ADMIN_USERNAME=your_admin_username
    ADMIN_PASSWORD=your_admin_password
    STAFF_USERNAME=your_staff_username
    STAFF_PASSWORD=your_staff_password
    ```

5. **Initialize the Database**

    The database will be automatically created when you run the application for the first time.

## Usage

Run the Streamlit application using the following command:

```bash
streamlit run app.py
```

Open your browser and navigate to [https://casemanagement.streamlit.app/](https://casemanagement.streamlit.app/) to access the application.

## Project Structure

### `modules/dbCon.py`

Handles all database operations using `aiosqlite`. This includes connecting to the database, creating tables, and performing CRUD operations on case records.

### `app.py`

The main Streamlit application that manages user authentication, displays dashboards, handles case management, logging, and backup functionalities. It uses various libraries such as `pandas` for data manipulation and `streamlit_cookies_manager` for managing user sessions.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Developed by [a3ro-dev](https://github.com/a3ro-dev)
```
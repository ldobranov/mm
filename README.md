# Fullstack Application

This project is a fullstack application that consists of a backend built with Python and a frontend built with Vue.js. 

## Project Structure

The project is organized into two main directories: `backend` and `frontend`.

### Backend

The backend is implemented in Python and follows a structured approach:

- **app/**: Contains the main application logic.
  - **__init__.py**: Initializes the app package.
  - **main.py**: Entry point of the backend application.
  - **models.py**: Defines the database models.
  - **routes.py**: Contains the API route definitions.
  - **schemas.py**: Contains Pydantic models for data validation.
  
- **db/**: Manages database interactions.
  - **base.py**: Defines the base model for the database.
  - **session.py**: Manages the database session.

- **api/**: Contains the API route definitions organized by resource.
  - **deps.py**: Dependency injection functions for the API routes.
  - **routers/**: Contains subdirectories for different resource routes.

- **requirements.txt**: Lists the dependencies required for the backend application.
- **.env**: Contains environment variables for the application.

### Frontend

The frontend is built using Vue.js and is structured as follows:

- **public/**: Contains static assets.
  - **index.html**: Main HTML template for the frontend application.

- **src/**: Contains the source code for the Vue application.
  - **App.vue**: Root component of the Vue application.
  - **main.js**: Entry point of the Vue application.
  - **components/**: Contains reusable Vue components.
  - **views/**: Contains pages/screens of the application.

- **package.json**: Lists the dependencies and scripts for the frontend application.
- **vite.config.js**: Configuration for Vite.

## Getting Started

To get started with the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ldobranov/mm
   cd mm
   ```

2. **Set up the backend**:
   - Navigate to the `backend` directory.
   - (Recommended) Create and activate a Python virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows use: venv\Scripts\activate
     ```
   - Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Set up the environment variables in the `.env` file (if needed).
   - Run the backend server:
     ```bash
     uvicorn app.main:app --reload --host 0.0.0.0 --port 8887
     ```

3. **Set up the frontend**:
   - Navigate to the `frontend` directory.
   - (Optional, only if you use Python tools for frontend development):
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     # Install any Python tools needed for frontend (rare for Vue.js projects)
     ```
   - Install the required dependencies:
     ```bash
     npm install
     ```
   - Run the frontend application:
     ```bash
     npm run serve
     # or
     npm run dev
     ```

## Python Virtual Environment Setup

- **Backend:** Using a Python virtual environment is highly recommended to avoid dependency conflicts.
- **Frontend:** A Python virtual environment is usually not required unless you use Python-based tools for frontend development (e.g., SASS/SCSS compilers, linters, etc.). For most Vue.js projects, Node.js and npm are sufficient.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
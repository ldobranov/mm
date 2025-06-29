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
   ```
   git clone <repository-url>
   cd fullstack-app
   ```

2. **Set up the backend**:
   - Navigate to the `backend` directory.
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Set up the environment variables in the `.env` file.
   - Run the backend server:
     ```
     python -m app.main
     ```

3. **Set up the frontend**:
   - Navigate to the `frontend` directory.
   - Install the required dependencies:
     ```
     npm install
     ```
   - Run the frontend application:
     ```
     npm run serve
     ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
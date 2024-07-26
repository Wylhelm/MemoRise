# Developer Guide for Memory Augmentation App

## Project Structure

- `app/`: Main application package
  - `__init__.py`: Application factory and configuration
  - `models/`: Database models
  - `routes/`: Route definitions
  - `services/`: Business logic and external service integrations
  - `utils/`: Utility functions
- `static/`: Static files (JS, CSS)
- `templates/`: HTML templates
- `config.py`: Configuration settings
- `run.py`: Application entry point

## Setting Up the Development Environment

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix or MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up Azure AI services and update `config.py` with your credentials

## Database

- SQLite database using SQLAlchemy ORM
- Model definitions in `app/models/memory.py`
- Database operations in `app/services/memory_service.py`

## Routes

- Main routes: `app/routes/main_routes.py`
- Memory-related routes: `app/routes/memory_routes.py`
- Export routes: `app/routes/export_routes.py`

## Services

- Memory service: `app/services/memory_service.py`
- NLP service: `app/services/nlp_service.py`
- Speech service: `app/services/speech_service.py`

## Templates

- Base template: `templates/base.html`
- Page-specific templates in `templates/`

## Static Files

- Voice recording JS: `static/js/voice_recording.js`

## Adding New Features

1. Create necessary database models in `app/models/`
2. Implement business logic in `app/services/`
3. Add new routes in `app/routes/`
4. Create or update templates in `templates/`
5. Add any required static files to `static/`

## Testing

- Implement unit tests for services and routes
- Use Flask's test client for integration tests

## Deployment

1. Set up a production server (e.g., Gunicorn)
2. Configure a reverse proxy (e.g., Nginx)
3. Set up environment variables for sensitive information
4. Use a production-grade database (e.g., PostgreSQL)

## Best Practices

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Handle exceptions and log errors appropriately
- Keep the application modular and maintain separation of concerns

## Troubleshooting

- Check application logs for error messages
- Verify Azure AI service credentials and quotas
- Ensure database migrations are up to date

For any questions or issues, please contact the lead developer or create an issue in the project repository.

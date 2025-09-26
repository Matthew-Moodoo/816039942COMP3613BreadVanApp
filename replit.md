# Flask MVC Template - Replit Setup

## Overview
This is a Flask web application template that follows the MVC (Model-View-Controller) pattern. The project has been successfully imported and configured to run in the Replit environment.

## Project Architecture
- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: HTML templates with Jinja2 templating engine
- **Database**: SQLite (with PostgreSQL support available)
- **Authentication**: JWT-based authentication system
- **Admin Panel**: Flask-Admin for administrative interface
- **File Uploads**: Flask-Reuploaded for handling file uploads
- **Testing**: Python pytest + Node.js/Mocha for e2e testing

## Recent Changes (September 25, 2025)
- ✅ Installed Python 3.11 and all required dependencies
- ✅ Created custom Flask configuration for Replit environment
- ✅ Configured Flask to run on 0.0.0.0:5000 (required for Replit proxy)
- ✅ Initialized database with all necessary tables
- ✅ Set up Flask development server workflow
- ✅ Configured deployment settings for production using Gunicorn
- ✅ Verified application is working correctly

## Current State
The application is **fully functional** and ready for development:

- **Development Server**: Running on port 5000 with hot reload
- **Database**: Initialized with SQLite (empty, ready for data)
- **Authentication**: JWT system configured and working
- **Admin Panel**: Accessible at /admin
- **Static Files**: CSS and JS files loading correctly
- **Deployment**: Configured for Replit autoscale deployment

## Key Features
- User authentication and authorization
- Admin dashboard with Flask-Admin
- File upload capabilities
- Database migrations with Flask-Migrate
- CORS enabled for API access
- Comprehensive testing setup

## Environment Configuration
The application uses a custom configuration (`App/custom_config.py`) that:
- Binds to 0.0.0.0:5000 for Replit compatibility
- Allows all hosts for proxy access
- Supports both SQLite and PostgreSQL databases
- Enables debug mode for development

## User Preferences
- This project follows Python Flask conventions
- Uses SQLAlchemy ORM for database operations
- Implements JWT for stateless authentication
- Follows MVC architectural pattern

## Next Steps
The application is ready for:
- Adding custom models and controllers
- Creating additional views and templates
- Implementing business logic
- Adding user registration and login features
- Deploying to production with the publish button
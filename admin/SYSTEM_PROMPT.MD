# SYSTEM PROMPT / ARQUITECTURA DEL PROYECTO

You are an expert in Python, Flask, and scalable API development. This project manages two distinct presentation layers (JSON and HTML) using a shared core logic.

## Key Principles
- Write concise, technical responses with accurate Python examples.
- Business logic is prohibited in Controllers and Views. Direct database access from Controllers and Views is prohibited (must use the Service layer).
- Use functional, declarative programming; avoid classes where possible except for Flask views.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., `blueprints/user_routes.py`).
- Favor named exports for routes and utility functions.
- Use the Receive an Object, Return an Object (RORO) pattern where applicable.
- Architecture: Use separate Blueprints to manage output responsibilities (JSON vs HTML).
- Services: The Service must be fully agnostic; its output (RORO) must serve both JSON and HTML.
- Reusability: Maximize Service code reuse. If two endpoints need the same data, they must call the same Service function.
- Separation: Mixing rendering code (Jinja) and serialization code (Marshmallow) in the same Controller is prohibited.

## Architecture: Dual Controller with Shared Core
The application is structured into two presentation "arms" that share the same "brain" (`core/services/`).

1. The Brain (`core/services/` layer)
   - Rule: 100% Flask-independent. Returns only pure Python data (dict, list).
2. API Arm (JSON) (`web/blueprints/api/`)
   - Role: Serve data to external applications.
   - Golden Rule: Only return JSON.
   - Flow: Call Service → Use Marshmallow to serialize → Return `jsonify(...)`.
3. Web Arm (HTML/Jinja) (`web/blueprints/web/`)
   - Role: Serve web pages to the browser.
   - Golden Rule: Must render the page.
   - Rule: Only place allowed to use `flask.render_template()`.
   - Calling Marshmallow is prohibited in this Blueprint.

## Jinja
- Data Flow: The Web Controller must obtain processed data from the Service and unpack it for Jinja (return `render_template('template.html', **data)`).
- Logic in Templates: No business logic or database queries within Jinja templates. Templates are for presentation only.
- Filters and Macros: Use custom filters for presentation manipulation (date format, currency). Use macros for reusable HTML components.
- Template Inheritance: Use Jinja's template inheritance (`extends`, `block`) for a base layout to ensure consistency.

## Python/Flask
- Use `def` for function definitions.
- Use type hints for all function signatures where possible.
- File structure: Flask app initialization, blueprints, models, utilities, config.
- Avoid unnecessary curly braces in conditional statements.
- For single-line statements in conditionals, omit curly braces.
- Use concise, one-line syntax for simple conditional statements (e.g., `if condition: do_something()`).

## Error Handling and Validation
- Prioritize error handling and edge cases:
  - Handle errors and edge cases at the beginning of functions.
  - Use early returns for error conditions to avoid deeply nested if statements.
  - Place the happy path last in the function for improved readability.
  - Avoid unnecessary `else` statements; use the if-return pattern instead.
  - Use guard clauses to handle preconditions and invalid states early.
  - Implement proper error logging and user-friendly error messages.
  - Use custom error types or error factories for consistent error handling.

## Dependencies
- Flask
- Flask-RESTful (for RESTful API development)
- Flask-SQLAlchemy (for ORM)
- Flask-Migrate (for database migrations)
- Marshmallow (for serialization/deserialization)
- Flask-JWT-Extended (for JWT authentication)

## Flask-Specific Guidelines
- Use Flask application factories for better modularity and testing.
- Organize routes using Flask Blueprints for better code organization.
- Use Flask-RESTful for building RESTful APIs with class-based views.
- Implement custom error handlers for different types of exceptions.
- Use Flask's `before_request`, `after_request`, and `teardown_request` decorators for request lifecycle management.
- Utilize Flask extensions for common functionalities (e.g., Flask-SQLAlchemy, Flask-Migrate).
- Use Flask's config object for managing different configurations (development, testing, production).
- Implement proper logging using Flask's `app.logger`.
- Use Flask-Session for handling authentication and authorization.

## Performance Optimization
- Use Flask-Caching for caching frequently accessed data.
- Implement database query optimization techniques (e.g., eager loading, indexing).
- Use connection pooling for database connections.
- Implement proper database session management.
- Use background tasks for time-consuming operations (e.g., Celery with Flask).

## Key Conventions
1. Use Flask's application context and request context appropriately.
2. Prioritize API performance metrics (response time, latency, throughput).
3. Structure the application:
   - Use blueprints for modularizing the application.
   - Implement a clear separation of concerns (routes, business logic, data access).
   - Use environment variables for configuration management.

## Database Interaction
- Use Flask-SQLAlchemy for ORM operations.
- Implement database migrations using Flask-Migrate.
- Use SQLAlchemy's session management properly, ensuring sessions are closed after use.

## Serialization and Validation
- Use Marshmallow for object serialization/deserialization and input validation.
- Create schema classes for each model to handle serialization consistently.

## Authentication and Authorization
- Implement session-based authentication using Flask-Session.
- Use decorators for protecting routes that require authentication.

## API Documentation
- Use Flask-RESTX or Flasgger for Swagger/OpenAPI documentation.
- Ensure all endpoints are documented with request/response schemas.

## Deployment
- Use environment variables for sensitive information and configuration.

Refer to Flask documentation for detailed information on Views, Blueprints, and Extensions for best practices.

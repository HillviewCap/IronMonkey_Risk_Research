# IronMonkey Risk Research Developer Setup Guide

This guide provides instructions for setting up the development environment for the IronMonkey Risk Research platform.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10+ (https://www.python.org/downloads/)
- Node.js 18+ and npm (https://nodejs.org/)
- Git (https://git-scm.com/downloads)
- PostgreSQL 15+ (optional for local development, can use Docker instead)
- Docker (optional, for containerized services) (https://www.docker.com/products/docker-desktop/)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/ironmonkey-risk-research.git
cd ironmonkey-risk-research
```

### 2. Create a Python Virtual Environment

#### Using venv
```bash
python -m venv venv
```

#### Activate the virtual environment

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Tailwind CSS

```bash
# Navigate to the project root
cd path/to/ironmonkey-risk-research

# Install Tailwind CSS and dependencies
npm init -y
npm install tailwindcss@latest postcss@latest autoprefixer@latest
```

### 5. Create Tailwind Configuration

```bash
npx tailwindcss init
```

Update the `tailwind.config.js` file:

```javascript
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/src/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### 6. Create CSS Input File

Create a file at `app/static/src/input.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles go here */
```

### 7. Configure Environment Variables

Create a `.env` file in the project root:

```
# Flask configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ironmonkey

# Elasticsearch configuration
ELASTICSEARCH_URL=http://localhost:9200

# Redis configuration
REDIS_URL=redis://localhost:6379/0
```

### 8. Set Up the Database

If you're using a local PostgreSQL installation:

```bash
# Create the database
createdb ironmonkey
```

Run migrations to create the schema:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 9. Start Development Services (Docker)

For convenience, you can use Docker to run required services:

```bash
# Start PostgreSQL, Elasticsearch, and Redis
docker-compose up -d
```

### 10. Build Tailwind CSS

```bash
# Run the Tailwind build process
npx tailwindcss -i ./app/static/src/input.css -o ./app/static/dist/css/output.css --watch
```

### 11. Run the Application

```bash
# Start the Flask development server
flask run
```

Access the application at http://localhost:5000

## Development Workflow

### CSS Changes

When making CSS changes:

1. Edit the `app/static/src/input.css` file or add Tailwind classes directly to HTML
2. The watch process will automatically rebuild the CSS
3. Refresh your browser to see the changes

### Database Changes

When making database model changes:

1. Update the SQLAlchemy models in the `app/models` directory
2. Generate a new migration:
   ```bash
   flask db migrate -m "Description of changes"
   ```
3. Apply the migration:
   ```bash
   flask db upgrade
   ```

### Adding Dependencies

When adding new Python dependencies:

1. Install the package:
   ```bash
   pip install package-name
   ```
2. Update requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Common Issues and Solutions

### PostgreSQL Connection Issues

If you encounter database connection issues:

1. Ensure PostgreSQL is running
2. Check your connection string in the `.env` file
3. Verify you have created the database

### Elasticsearch Issues

If Elasticsearch is not responding:

1. Check if Elasticsearch is running: `curl -X GET "localhost:9200"`
2. Ensure the ELASTICSEARCH_URL in your `.env` file is correct

### Redis Issues

If you experience session or caching problems:

1. Verify Redis is running: `redis-cli ping`
2. Check the REDIS_URL in your `.env` file

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)

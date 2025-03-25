# AI Blog CMS

A backend API for an AI-powered blog content management system built with Flask.

## Overview

This project provides a robust backend API for managing blog content with AI-assisted features, including:

- User authentication and authorization
- Blog post creation, editing, and publishing
- Category and tag management
- AI-powered content suggestions
- Automated SEO optimization
- Content analytics

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger/OpenAPI
- **AI Features**: Integration with OpenAI APIs

## Project Structure

```
ai-blog-cms/
├── app/                  # Application package
│   ├── __init__.py       # Initialize Flask app
│   ├── config.py         # Configuration settings
│   ├── models/           # Database models
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   ├── schemas/          # Request/response schemas
│   └── utils/            # Helper functions
├── tests/                # Test cases
├── migrations/           # Database migrations
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- virtualenv (recommended)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/aniketsinghdshgsonic/ai-blog-cms.git
   cd ai-blog-cms
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update the values:
   ```
   cp .env.example .env
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the development server:
   ```
   python run.py
   ```

## API Documentation

Once the server is running, access the API documentation at:
```
http://localhost:5000/api/docs
```

## Development

### Running Tests

```
pytest
```

### Code Style

This project follows PEP 8 guidelines. You can check your code style with:

```
flake8
```

## License

[MIT](LICENSE)

## Contact

If you have any questions or feedback, please contact the project maintainer.

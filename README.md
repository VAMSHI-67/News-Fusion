# NewsFusion

A full-stack news aggregator web application built with Django and Scrapy. NewsFusion aggregates news from multiple Indian sources, providing a centralized dashboard for users to view trending news and search for specific topics.

## Features

- User authentication (register, login, logout)
- Dashboard showing trending news articles
- Keyword-based news search
- Web crawler using Scrapy to fetch news from Indian sources
- Deduplication using SHA256 hashing
- Admin interface to manage news sources

## Tech Stack

- **Backend & Frontend**: Django (with Django templates)
- **Web Crawler**: Scrapy (integrated with Django)
- **Database**: SQLite (for simplicity, can be replaced with MySQL)
- **Authentication**: Django's built-in User model

## Installation

1. Clone the repository
```
git clone <repository-url>
cd newsfusion
```

2. Install the dependencies
```
pip install django scrapy python-dotenv
```

3. Apply migrations
```
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser (for admin access)
```
python manage.py createsuperuser
```

5. Run the development server
```
python manage.py runserver
```

6. Access the application at `http://127.0.0.1:8000/`

## Setting Up News Sources

1. Log in to the admin panel at `http://127.0.0.1:8000/admin/`
2. Add news sources under the `NewsSource` model with the following information:
   - Name (e.g., "Times of India")
   - URL (e.g., "https://timesofindia.indiatimes.com/")
   - Set "Is Active" to True

## How the Crawler Works

The crawler is integrated with Django and runs in the background:

1. It automatically triggers when users visit the dashboard if no articles exist
2. Users can trigger keyword-specific crawls via the search page
3. Crawled data is automatically deduplicated using SHA256 hashing

## Project Structure

- `newsfusion/` - Main Django project
- `newsapp/` - Django app for user interface and models
- `crawler/` - Django app with Scrapy integration
  - `crawler/spiders/` - Scrapy spiders for different news sources
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JS, images)

## Usage

1. Register a new account or login
2. Browse trending news on the dashboard
3. Use the search bar to find news on specific topics

## Admin Interface

Access the admin interface at `http://127.0.0.1:8000/admin/` to:
- Manage news sources (add, edit, disable)
- View and manage news articles
- Manage user accounts 
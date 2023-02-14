# Micro-blog
Simple service for text blogging. Users can post articles in their blogs and
find articles from another authors by simple recommendation system.

Screenshots:
> TODO

## Features
- Simple and intuitive API
- API authorization with access tokens
- Docker Compose support
- Unit testing

## TODO:
> - Saving user files into object storage (e.g user avatar, article images)
> - Article creation with blocks like headers, paragraphs, images, etc.
> - Sorting articles by different filters (popularity, creation time and etc.)
> - Articles search system
> - User comments under articles
> - Password and E-Mail changing function

## Technology stack
- Backend: Python, FastAPI, SQLAlchemy, Dependency Injector, PostgreSQL, Redis,
etc.
- Frontend: _TODO_

## Installation
Type following command into your terminal to clone this repository:
```bash
git clone https://github.com/arsuhinars/micro-blog.git
```
Then go inside created directory with this command:
```bash
cd micro-blog
```

Ensure that [Docker](https://www.docker.com/) is installed into your system. Then
run next command:
```bash
docker compose up --build -d
```
It will build images, create and run containers with all needed services in the
background. To disable service and remove containers, type next command:
```bash
docker compose down
```

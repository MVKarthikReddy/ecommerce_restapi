
```markdown
# Ecommerce API with WebSockets and Redis Caching

## Overview

This project is a Django-based e-commerce API that includes features such as product and category management, cart and order processing, and real-time notifications using WebSockets. Redis is used for caching to enhance performance.

## Features

- JWT-based user authentication
- Product and category management
- Cart and order handling with item management
- Real-time notifications via WebSockets for order status updates
- Redis caching for performance optimization

## Technologies

- **Backend**: Django, Django Rest Framework
- **WebSockets**: Django Channels
- **Database**: PostgreSQL
- **Caching**: Redis
- **Authentication**: JWT (JSON Web Tokens)

---

## Setup Instructions

### Prerequisites

Ensure you have the following installed on your machine:

- Python 3.8+
- PostgreSQL
- Redis
- Virtualenv 

### 1. Clone the Repository

```bash
git clone https://github.com/MVKarthikReddy/ecommerce_restapi.git
cd ecommerce_restapi
```

### 2. Create and Activate Virtual Environment

```bash

python -m venv venv
venv\Scripts\activate

```

### 3. Install Dependencies

```bash
# To install requirements
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

1. Install PostgreSQL if you haven't already.
2. Create a new database for the project.
3. Update your `settings.py` file with the correct database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecommerce_db',
        'USER': 'ecommerce_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Migrate Database

Run the following command to apply the migrations:

```bash
python manage.py migrate
```

### 6. Setup Redis for Caching

1. Install Redis and start the Redis server.

   

3. Add Redis settings to your `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 7. Setup WebSockets (Django Channels)

1. Install `Django Channels`:

```bash
pip install channels
```

2. Add Channels to `INSTALLED_APPS` and configure ASGI settings in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'channels',
]

ASGI_APPLICATION = 'ecommerce_restapi.asgi.application'
```

3. Create `asgi.py` in your root folder:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

from shop import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/orders/(?P<order_id>\d+)/$', consumers.OrderConsumer.as_asgi()),
        ])
    ),
})
```

### 8. Create Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

Follow the instructions to create your admin credentials.

### 9. Run the Development Server

```bash
python manage.py runserver
```

The app should now be running at `http://localhost:8000`.

---

## Testing WebSockets

1. Open multiple browser tabs.
2. Authenticate the user in one tab.
3. Connect to the WebSocket server using `/ws/orders/<int:user_id>/`.
4. Change the order status in the Django admin, and observe real-time updates in the WebSocket connection.

### WebSocket Test URL

```
ws://localhost:8000/ws/orders/<int:user_id>/
```

---

## API Endpoints

For API endpoints consider **thunder Client** Collection which is added.

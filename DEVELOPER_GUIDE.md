# EcoStore Developer Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Development Environment Setup](#development-environment-setup)
4. [Project Structure](#project-structure)
5. [Key Components](#key-components)
6. [Database Schema](#database-schema)
7. [API Documentation](#api-documentation)
8. [Telegram Bot Integration](#telegram-bot-integration)
9. [Deployment](#deployment)
10. [Contributing Guidelines](#contributing-guidelines)

## Project Overview

EcoStore is a Django-based e-commerce platform with Telegram bot integration. It provides a complete solution for online shopping, order management, and customer interaction through both web and Telegram interfaces.

### Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Bot Framework**: python-telegram-bot
- **Frontend**: Django Templates with HTML/CSS/JavaScript

## System Architecture

The system is built with a modular architecture using Django apps:

1. **core**: Authentication, user management, and core functionality
2. **store**: E-commerce functionality (products, orders, transactions)
3. **front**: Web interface and user-facing views
4. **eco**: Main Django project settings and configuration

Additionally, there's a standalone Telegram bot implementation (`bot.py`) that interacts with the Django backend through the database.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### Local Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd ecostore
```

2. **Set up a virtual environment (optional if using Docker)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run with Docker Compose**

```bash
docker-compose up
```

4. **Run migrations (if not using Docker)**

```bash
python manage.py migrate
```

5. **Create a superuser (if not using Docker)**

```bash
python manage.py createsuperuser
```

6. **Run the development server (if not using Docker)**

```bash
python manage.py runserver
```

7. **Run the Telegram bot (if not using Docker)**

```bash
python bot.py
```

## Project Structure

```
ecostore/
├── core/                   # User authentication and core functionality
│   ├── migrations/         # Database migrations
│   ├── templates/          # Core templates
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # Core data models
│   ├── serializers.py      # API serializers
│   ├── urls.py             # URL routing
│   ├── utils.py            # Utility functions
│   └── views.py            # View controllers
│
├── store/                  # E-commerce functionality
│   ├── migrations/         # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # E-commerce data models
│   ├── permissions.py      # API permissions
│   ├── serializers.py      # API serializers
│   ├── urls.py             # URL routing
│   └── views.py            # View controllers
│
├── front/                  # Web interface
│   ├── migrations/         # Database migrations
│   ├── templates/          # Frontend templates
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── context_processors.py # Template context processors
│   ├── forms.py            # Form definitions
│   ├── models.py           # Frontend models
│   ├── urls.py             # URL routing
│   └── views.py            # View controllers
│
├── eco/                    # Django project settings
│   ├── __init__.py
│   ├── asgi.py             # ASGI configuration
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
│
├── bot.py                  # Telegram bot implementation
├── check_or_create_superuser.py # Utility for Docker setup
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker build configuration
├── Dockerfile.db          # Database Docker configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Key Components

### Core App

The `core` app handles user authentication and core functionality:

- **Custom User Model**: Phone-based authentication with OTP verification
- **Ticket System**: Customer support ticket management

### Store App

The `store` app manages all e-commerce functionality:

- **Product Management**: Products, details, and pricing
- **Store Management**: Multiple stores with product availability
- **Order Processing**: Complete order lifecycle
- **Wallet System**: Customer wallet and transactions

### Front App

The `front` app provides the web interface for customers:

- **User Interface**: Templates and views for customer interaction
- **Forms**: User input handling
- **Context Processors**: Template data enrichment

### Telegram Bot

The `bot.py` file implements the Telegram bot interface:

- **Command Handlers**: Process user commands
- **Conversation Handlers**: Manage multi-step interactions
- **Database Integration**: Interact with the Django database

## Database Schema

### Core Models

- **User**: Custom user model with phone authentication
  - Fields: phone, otp, user_code, standard Django user fields

- **Ticket**: Customer support ticket system
  - Fields: order, user, title, description, status, created_at

### Store Models

- **Customer**: Links users to the e-commerce system
  - Fields: name, telegram_id, user

- **Wallet**: Customer wallet for transactions
  - Fields: amount, customer

- **Product**: Product information
  - Fields: asin, title, created_at

- **ProductDetails**: Detailed product information
  - Fields: product, description, pricing, list_price, images, feature_bullets, customization_options

- **Store**: Store information
  - Fields: owner, name, address, score, website, phone, created_at

- **StoreProduct**: Product availability in stores
  - Fields: store, product, price, stock, url, created_at

- **Cart** and **CartItem**: Shopping cart functionality
  - Fields: customer, product, quantity, etc.

- **Order** and **OrderItem**: Customer orders
  - Fields: customer, created_at, product, quantity, unit_price, etc.

- **OrderStatus**: Order status tracking
  - Fields: order, status, status_change

- **OrderInvoice**: Order payment information
  - Fields: amount, status, order, description, photo, created_at

- **Transaction**: Financial transactions
  - Fields: amount, status, wallet, etc.

## API Documentation

### Authentication

The API uses token-based authentication. To authenticate:

1. Send a POST request to `/api/token/` with phone and password
2. Use the returned token in the Authorization header: `Authorization: Token <token>`

### Endpoints

#### User Management

- `GET /api/users/me/`: Get current user information
- `PUT /api/users/me/`: Update user information

#### Products

- `GET /api/products/`: List all products
- `GET /api/products/{id}/`: Get product details
- `GET /api/stores/{store_id}/products/`: List products in a store

#### Orders

- `GET /api/orders/`: List user orders
- `POST /api/orders/`: Create a new order
- `GET /api/orders/{id}/`: Get order details
- `PUT /api/orders/{id}/status/`: Update order status

#### Wallet

- `GET /api/wallet/`: Get wallet information
- `POST /api/wallet/transactions/`: Create a new transaction

## Telegram Bot Integration

The Telegram bot is implemented in `bot.py` and interacts with the Django backend through the database.

### Bot Setup

1. Create a bot on Telegram using BotFather
2. Get the bot token and update the `TOKEN` variable in `bot.py`
3. Run the bot using `python bot.py`

### Bot Architecture

The bot uses the python-telegram-bot library and follows a command-handler pattern:

- **Command Handlers**: Process specific commands like `/start` and `/help`
- **Message Handlers**: Process text messages and button interactions
- **Callback Query Handlers**: Process inline button callbacks

### Database Integration

The bot connects directly to the PostgreSQL database to read and write data. Key operations include:

- Checking if a user exists in the system
- Creating new customers and orders
- Updating order status
- Retrieving wallet information

## Deployment

### Docker Deployment

The project includes Docker configuration for easy deployment:

1. Update environment variables in `docker-compose.yml` if needed
2. Run `docker-compose up -d` to start the services in detached mode
3. Access the web application at http://localhost:8000

### Manual Deployment

For manual deployment to a server:

1. Set up a PostgreSQL database
2. Configure Django settings in `eco/settings.py`
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`
5. Set up a production web server (Nginx, Apache) with WSGI/ASGI
6. Configure the Telegram bot to run as a service

## Contributing Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write comments for complex logic

### Development Workflow

1. Create a feature branch from `main`
2. Implement your changes
3. Write tests for new functionality
4. Run tests: `python manage.py test`
5. Submit a pull request

### Testing

- Write unit tests for models and views
- Test the Telegram bot functionality manually
- Ensure all tests pass before submitting a pull request

---

This developer guide provides an overview of the EcoStore project. For more detailed information, please refer to the code documentation and comments within the source files.
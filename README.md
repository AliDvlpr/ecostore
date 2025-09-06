# EcoStore - E-commerce Platform with Telegram Bot Integration

## Overview

EcoStore is a comprehensive e-commerce platform built with Django that integrates with Telegram for order management and customer interaction. The system allows users to browse products, place orders, manage their accounts, and track their order status through both a web interface and a Telegram bot.

## Key Features

- **Multi-channel Shopping Experience**: Web interface and Telegram bot integration
- **User Authentication**: Phone-based authentication with OTP verification
- **Product Management**: Comprehensive product catalog with details, images, and pricing
- **Store Management**: Multiple stores with product availability and pricing
- **Order Processing**: Complete order lifecycle from creation to delivery
- **Wallet System**: Digital wallet for customers to manage their funds
- **Transaction Tracking**: Detailed transaction history and status tracking
- **Admin Dashboard**: Comprehensive admin interface for managing all aspects of the platform

## System Architecture

The project is structured into several Django apps:

1. **core**: Handles user authentication, profile management, and core functionality
2. **store**: Manages products, orders, transactions, and the e-commerce functionality
3. **front**: Provides the web interface for customers
4. **eco**: Main Django project settings and configuration

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Installation and Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd ecostore
```

2. **Run with Docker Compose**

```bash
docker-compose up
```

This will start three services:
- PostgreSQL database
- Django web application (available at http://localhost:8000)
- Telegram bot service

3. **Access the admin interface**

Navigate to http://localhost:8000/admin and log in with the superuser credentials (automatically created during setup).

## Using the Web Interface

1. **Registration and Login**
   - Register with your phone number
   - Verify with OTP
   - Complete your profile

2. **Browsing Products**
   - View product catalog
   - Filter by categories
   - View product details and pricing from different stores

3. **Placing Orders**
   - Add products to cart
   - Select store and quantity
   - Complete checkout

4. **Managing Account**
   - View order history
   - Check wallet balance
   - Update profile information

## Using the Telegram Bot

1. **Start the bot**: Send `/start` to the bot
2. **Register**: Share your phone number when prompted
3. **Main Menu**:
   - New Order 🛒
   - My Orders 📋
   - Help ℹ️
   - My Account 🍃

4. **Placing an Order**:
   - Select "New Order 🛒"
   - Follow the prompts to provide product link, size, color, and description
   - Confirm your order

5. **Checking Orders**:
   - Select "My Orders 📋"
   - View status of all your orders

## Admin Guide

### Managing Products

1. Access the admin interface at `/admin`
2. Navigate to Products section
3. Add new products with ASIN, title, and details
4. Upload product images and set pricing

### Managing Orders

1. View all orders in the Orders section
2. Update order status (Pending, Accepted, Complete, Failed, Sending, Received)
3. Process payments and manage invoices

### Managing Users

1. View and edit user profiles
2. Manage customer wallets
3. Handle support tickets

## Development

### Project Structure

```
ecostore/
├── core/               # User authentication and core functionality
├── store/              # E-commerce functionality
├── front/              # Web interface
├── eco/                # Django project settings
├── bot.py              # Telegram bot implementation
├── docker-compose.yml  # Docker configuration
└── requirements.txt    # Python dependencies
```

### Key Models

- **User**: Custom user model with phone authentication
- **Customer**: Links users to the e-commerce system
- **Product**: Product information and details
- **Store**: Store information and product availability
- **Order**: Customer orders and status
- **Wallet**: Customer wallet for transactions
- **Transaction**: Financial transactions in the system

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL service is running
   - Verify database credentials in settings

2. **Telegram Bot Not Responding**
   - Verify the bot token in bot.py
   - Check the bot service is running

3. **Web Interface Not Loading**
   - Check Django server logs
   - Verify port 8000 is not in use by another application

## Support

if there is any bugs create a issue

## License

---

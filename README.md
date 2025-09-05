# TimelyCabs - Taxi Booking System

A comprehensive FastAPI-based taxi booking and management system with authentication, user management, and scalable architecture.

## 🚀 Features

- **Authentication System**: OTP-based phone authentication
- **User Management**: Role-based access control (Rider, Driver, Owner, Admin, Support)
- **Scalable Architecture**: Clean separation of concerns with services, models, and API layers
- **Database Support**: MySQL with SQLAlchemy ORM
- **Security**: JWT tokens, password hashing, rate limiting, security headers
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Auto-generated API documentation
- **Deployment**: Docker and Docker Compose support
- **Monitoring**: Health checks and logging

## 📁 Project Structure

```
timelycabs/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/                # API version 1
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── users.py       # User management endpoints
│   │       └── health.py      # Health check endpoints
│   ├── core/                  # Core application components
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database configuration
│   │   ├── security.py        # Security utilities
│   │   ├── middleware.py      # Custom middleware
│   │   └── exceptions.py      # Custom exceptions
│   ├── models/                # Database models
│   │   ├── base.py           # Base model classes
│   │   ├── user.py           # User-related models
│   │   └── auth.py           # Authentication models
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py           # Authentication schemas
│   │   ├── user.py           # User schemas
│   │   └── common.py         # Common schemas
│   ├── services/              # Business logic services
│   │   ├── base.py           # Base service class
│   │   ├── auth_service.py   # Authentication service
│   │   ├── user_service.py   # User management service
│   │   └── otp_service.py    # OTP service
│   ├── utils/                 # Utility functions
│   │   ├── logging.py        # Logging utilities
│   │   ├── validators.py     # Validation utilities
│   │   └── helpers.py        # Helper functions
│   └── main.py               # Application entry point
├── tests/                     # Test suite
│   ├── conftest.py           # Test configuration
│   ├── test_auth.py          # Authentication tests
│   └── test_users.py         # User management tests
├── scripts/                   # Database scripts
├── deployments/               # Deployment configurations
├── docs/                      # Documentation
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── nginx.conf                 # Nginx configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- MySQL 8.0+
- Redis (optional, for caching)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd timelycabs
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE timelycabs;
   
   # Run database initialization
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health/

## 📚 API Documentation

### Available Endpoints

- `POST /api/v1/auth/request-otp` - Request OTP for phone verification
- `POST /api/v1/auth/verify-otp` - Verify OTP and authenticate user
- `POST /api/v1/auth/complete-profile` - Complete user profile
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/health/` - Application health check

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## 🔧 Configuration

The application uses environment variables for configuration. Key settings:

- `ENVIRONMENT`: Application environment (development, production, testing)
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `SMS_PROVIDER`: SMS provider for OTP delivery
- `LOG_LEVEL`: Logging level

See `.env.example` for all available configuration options.

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
   ```bash
   export ENVIRONMENT=production
   export DATABASE_URL=mysql+pymysql://user:pass@host:port/db
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Setup SSL certificates** (for HTTPS)
   ```bash
   # Place certificates in ssl/ directory
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

### Kubernetes Deployment

See `deployments/kubernetes/` directory for Kubernetes manifests.

## 📊 Monitoring

The application includes:

- **Health checks** for load balancer integration
- **Structured logging** with request IDs
- **Rate limiting** to prevent abuse
- **Security headers** for protection
- **Database connection monitoring**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/redoc`

## 🔄 Version History

- **v1.0.0** - Initial release with authentication and user management
- **v1.1.0** - Added comprehensive testing and deployment configurations
- **v1.2.0** - Enhanced security and monitoring features
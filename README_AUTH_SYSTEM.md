# Timelycabs Authentication System

This document describes the OTP-based authentication system implemented for the Timelycabs taxi booking platform.

## Overview

The authentication system uses phone number verification with OTP (One-Time Password) for secure user authentication. The system supports both new user registration and existing user login through a unified flow.

## Database Schema

### Tables

1. **users** - Stores user information
2. **roles** - Defines user roles in the system
3. **user_roles** - Many-to-many relationship between users and roles
4. **otp_logs** - Stores OTP generation and verification
5. **sessions** - Manages user authentication tokens

### Key Features

- Phone number as primary identifier
- OTP verification before login
- Automatic user creation for new phone numbers
- Role-based access control
- Session management for multi-device login
- Rate limiting for OTP requests

## API Endpoints

### 1. Request OTP
**POST** `/auth/request-otp`

Request:
```json
{
  "phone": "+919876543210"
}
```

Response:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "otp_id": 12345
}
```

### 2. Verify OTP
**POST** `/auth/verify-otp`

Request:
```json
{
  "phone": "+919876543210",
  "otp": "123456",
  "device_info": "Android 14 | Pixel 7"
}
```

Response (existing user):
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "user_id": 101,
    "full_name": "Mayur Karale",
    "gender": "male",
    "phone": "+919876543210",
    "phone_verified": true,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00",
    "roles": [
      {
        "role_id": 1,
        "role_name": "rider",
        "description": "Regular taxi booking rider"
      }
    ]
  },
  "auth_token": "eyJhbGciOi..."
}
```

Response (new user):
```json
{
  "success": true,
  "message": "OTP verified, complete profile required",
  "is_new_user": true,
  "phone": "+919876543210",
  "auth_token": "temp_token_for_onboarding"
}
```

### 3. Complete Profile
**POST** `/auth/complete-profile`

Request:
```json
{
  "auth_token": "temp_token_for_onboarding",
  "full_name": "Mayur Karale",
  "gender": "male"
}
```

Response:
```json
{
  "success": true,
  "message": "Profile completed, login successful",
  "user": {
    "user_id": 101,
    "full_name": "Mayur Karale",
    "gender": "male",
    "phone": "+919876543210",
    "phone_verified": true,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00",
    "roles": [
      {
        "role_id": 1,
        "role_name": "rider",
        "description": "Regular taxi booking rider"
      }
    ]
  },
  "auth_token": "final_login_token"
}
```

### 4. Logout
**POST** `/auth/logout`

Request:
```json
{
  "auth_token": "final_login_token"
}
```

Response:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## Authentication Flow

### For New Users:
1. User enters phone number → Request OTP
2. User receives OTP via SMS
3. User enters OTP → Verify OTP
4. System creates user account with phone number
5. System returns temporary token for profile completion
6. User provides name and gender → Complete Profile
7. System creates permanent session and returns final token

### For Existing Users:
1. User enters phone number → Request OTP
2. User receives OTP via SMS
3. User enters OTP → Verify OTP
4. System finds existing user
5. System creates session and returns authentication token

## Security Features

1. **Rate Limiting**: OTP requests are limited to prevent abuse
2. **OTP Expiry**: OTPs expire after 5 minutes
3. **Session Management**: Secure token-based sessions with expiry
4. **Phone Verification**: All users must verify their phone number
5. **Role-based Access**: Users are assigned appropriate roles

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/timelycabs

# OTP Configuration
OTP_EXPIRY_MINUTES=5
SESSION_EXPIRY_DAYS=7

# SMS Configuration (for production)
SMS_PROVIDER=twilio
SMS_ACCOUNT_SID=your_account_sid
SMS_AUTH_TOKEN=your_auth_token
SMS_FROM_NUMBER=your_twilio_number
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   # Create database
   mysql -u root -p -e "CREATE DATABASE timelycabs;"
   
   # Run schema
   mysql -u root -p timelycabs < scripts/database_schema.sql
   ```

3. **Environment Configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

4. **Run Application**:
   ```bash
   python run.py
   ```

## Testing

### Using curl:

1. **Request OTP**:
   ```bash
   curl -X POST "http://localhost:8000/auth/request-otp" \
        -H "Content-Type: application/json" \
        -d '{"phone": "+919876543210"}'
   ```

2. **Verify OTP** (check logs for OTP):
   ```bash
   curl -X POST "http://localhost:8000/auth/verify-otp" \
        -H "Content-Type: application/json" \
        -d '{"phone": "+919876543210", "otp": "123456", "device_info": "Test Device"}'
   ```

3. **Complete Profile** (for new users):
   ```bash
   curl -X POST "http://localhost:8000/auth/complete-profile" \
        -H "Content-Type: application/json" \
        -d '{"auth_token": "temp_token", "full_name": "Test User", "gender": "male"}'
   ```

4. **Logout**:
   ```bash
   curl -X POST "http://localhost:8000/auth/logout" \
        -H "Content-Type: application/json" \
        -d '{"auth_token": "your_auth_token"}'
   ```

## Production Considerations

1. **SMS Integration**: Replace placeholder SMS service with Twilio, AWS SNS, or similar
2. **Rate Limiting**: Implement proper rate limiting middleware
3. **Logging**: Add comprehensive logging for security monitoring
4. **Monitoring**: Set up alerts for failed authentication attempts
5. **Backup**: Regular database backups
6. **SSL**: Use HTTPS in production
7. **Token Security**: Consider using JWT tokens with proper signing

## Error Handling

The system handles various error scenarios:

- Invalid phone number format
- OTP rate limiting
- Invalid or expired OTP
- Invalid authentication tokens
- Database connection issues
- SMS delivery failures

All errors return appropriate HTTP status codes and descriptive messages.

## File Structure

```
timelycabs/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth_service.py
│   └── routers/
│       ├── __init__.py
│       └── auth.py
├── scripts/
│   └── database_schema.sql
├── requirements.txt
├── run.py
├── env.example
└── README_AUTH_SYSTEM.md
```

## Support

For issues or questions about the authentication system, please refer to the main project documentation or create an issue in the project repository.

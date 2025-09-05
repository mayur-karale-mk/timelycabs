-- Timelycabs Authentication System Database Schema
-- This script creates all necessary tables for OTP-based authentication
-- Database: sql12796707 (FreeSQLDatabase)

-- Users table - stores user information
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(150),
    gender ENUM('male','female','other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    phone_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Roles table - defines user roles in the system
CREATE TABLE roles (
    role_id INT NOT NULL AUTO_INCREMENT,
    role_name ENUM('rider','driver','owner','admin','support') NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- User roles table - many-to-many relationship between users and roles
CREATE TABLE user_roles (
    user_role_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id INT NOT NULL,
    assigned_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_role_id),
    UNIQUE KEY user_id (user_id, role_id),
    KEY role_id (role_id),
    CONSTRAINT user_roles_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT user_roles_ibfk_2 FOREIGN KEY (role_id) REFERENCES roles (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- OTP logs table - stores OTP generation and verification
CREATE TABLE otp_logs (
    otp_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(phone)
);

-- Sessions table - manages user authentication tokens
CREATE TABLE sessions (
    session_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    auth_token VARCHAR(255) UNIQUE NOT NULL,
    device_info VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Insert default roles
INSERT INTO roles (role_name, description) VALUES
('rider', 'Regular taxi booking rider'),
('driver', 'Taxi driver'),
('owner', 'Taxi fleet owner'),
('admin', 'System administrator'),
('support', 'Customer support representative');

-- Create indexes for better performance
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_otp_logs_phone_created ON otp_logs(phone, created_at);
CREATE INDEX idx_sessions_auth_token ON sessions(auth_token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

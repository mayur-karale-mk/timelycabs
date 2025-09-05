-- Migration script to update 'customer' role to 'rider' role
-- Run this script if you have an existing database with 'customer' role

-- First, update the enum type to include 'rider' (MySQL doesn't support direct enum modification)
-- We need to recreate the table with the new enum

-- Create a temporary table with the new structure
CREATE TABLE roles_new (
    role_id INT NOT NULL AUTO_INCREMENT,
    role_name ENUM('rider','driver','owner','admin','support') NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Copy existing data, replacing 'customer' with 'rider'
INSERT INTO roles_new (role_id, role_name, description)
SELECT 
    role_id,
    CASE 
        WHEN role_name = 'customer' THEN 'rider'
        ELSE role_name
    END as role_name,
    CASE 
        WHEN role_name = 'customer' THEN 'Regular taxi booking rider'
        ELSE description
    END as description
FROM roles;

-- Drop the old table
DROP TABLE roles;

-- Rename the new table
RENAME TABLE roles_new TO roles;

-- Update any existing user_roles references
-- This is handled automatically by the foreign key constraints

-- Verify the migration
SELECT * FROM roles;

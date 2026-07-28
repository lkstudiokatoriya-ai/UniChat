-- ===========================
-- Create Database
-- ===========================

CREATE DATABASE IF NOT EXISTS polytechnic_hub;

USE polytechnic_hub;

-- ===========================
-- Users Table
-- ===========================

CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    phone VARCHAR(20),

    state VARCHAR(100),

    branch VARCHAR(100),

    semester VARCHAR(20),

    profile_image VARCHAR(255) DEFAULT 'default.png',

    role ENUM('student','teacher','admin') DEFAULT 'student',

    is_verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP

);

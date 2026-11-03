-- Database Schema para Práctica de SQL Injection en Login
CREATE DATABASE IF NOT EXISTS seguridad_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE seguridad_db;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Almacenamiento plano en versión vulnerable
    password_hash VARCHAR(255) NOT NULL, -- Hash seguro bcrypt
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, password_hash, role) VALUES 
('admin', 'admin123', '$2y$10$e0MYzXyjpJS7Pd0RVvHwHe1aKxR.K9yHk2NqV4b5W5U5V5U5V5U5V', 'administrator'),
('fsabido', 'guitar2026', '$2y$10$4N2M8s7K9p1L3v5W7X9Y1e3F5G7H9I1J3K5L7M9N1O3P5Q7R9S1T3', 'student'),
('snoh', 'profesor2026', '$2y$10$9X1Y3Z5A7B9C1D3E5F7G9H1I3J5K7L9M1N3O5P7Q9R1S3T5U7V9W1', 'docente');

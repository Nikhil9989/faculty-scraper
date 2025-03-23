-- Faculty Database Schema
-- This schema defines the structure for storing faculty data from universities

-- Universities table to store university information
CREATE TABLE universities (
    university_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    website VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table to store department information
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    university_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    website VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(university_id)
);

-- Faculty table to store basic faculty information
CREATE TABLE faculty (
    faculty_id SERIAL PRIMARY KEY,
    department_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    profile_url VARCHAR(200),
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Research interests table to store faculty research interests
CREATE TABLE research_interests (
    interest_id SERIAL PRIMARY KEY,
    faculty_id INT NOT NULL,
    interest VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

-- Publications table to store faculty publications
CREATE TABLE publications (
    publication_id SERIAL PRIMARY KEY,
    faculty_id INT NOT NULL,
    title VARCHAR(300) NOT NULL,
    authors VARCHAR(500),
    year INT,
    venue VARCHAR(200),
    url VARCHAR(300),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

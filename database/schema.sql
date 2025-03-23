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

-- Create index on university name for faster searches
CREATE INDEX idx_university_name ON universities(name);

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

-- Create indexes for faster department lookups
CREATE INDEX idx_department_university_id ON departments(university_id);
CREATE INDEX idx_department_name ON departments(name);

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

-- Create indexes for faster faculty lookups and searches
CREATE INDEX idx_faculty_department_id ON faculty(department_id);
CREATE INDEX idx_faculty_last_name ON faculty(last_name);
CREATE INDEX idx_faculty_email ON faculty(email);
CREATE INDEX idx_faculty_last_first_name ON faculty(last_name, first_name);

-- Research interests table to store faculty research interests
CREATE TABLE research_interests (
    interest_id SERIAL PRIMARY KEY,
    faculty_id INT NOT NULL,
    interest VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

-- Create indexes for faster interest lookups
CREATE INDEX idx_interest_faculty_id ON research_interests(faculty_id);
-- Create a GIN index for fast text search on interests
CREATE INDEX idx_interest_text ON research_interests USING GIN (to_tsvector('english', interest));

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

-- Create indexes for faster publication lookups
CREATE INDEX idx_publication_faculty_id ON publications(faculty_id);
CREATE INDEX idx_publication_year ON publications(year);
-- Create a GIN index for fast text search on publication titles
CREATE INDEX idx_publication_title ON publications USING GIN (to_tsvector('english', title));

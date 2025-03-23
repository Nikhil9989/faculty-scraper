# Faculty Database

This directory contains database schemas and related tools for storing faculty data scraped from university websites.

## SQL Schema

The `schema.sql` file defines a relational database schema for storing faculty information in a PostgreSQL database.

### Tables

1. **universities**
   - Stores information about each university
   - Fields: university_id, name, location, website

2. **departments**
   - Stores information about university departments
   - Fields: department_id, university_id, name, website

3. **faculty**
   - Stores basic faculty information
   - Fields: faculty_id, department_id, first_name, last_name, title, email, profile_url

4. **research_interests**
   - Stores faculty research interests (many-to-one relationship with faculty)
   - Fields: interest_id, faculty_id, interest

5. **publications**
   - Stores faculty publications (many-to-one relationship with faculty)
   - Fields: publication_id, faculty_id, title, authors, year, venue, url

### Data Model

The schema follows this hierarchical structure:
- Each university has many departments
- Each department has many faculty members
- Each faculty member has many research interests and publications

### Usage

To set up the database using this schema:

```bash
# Create a PostgreSQL database
createdb faculty_db

# Import the schema
psql -d faculty_db -f schema.sql
```

## Importing Scraped Data

You can import data from the scraped JSON files using the provided import script (to be implemented).

### Example:

```bash
python database/import_data.py --input faculty_data.json --db-name faculty_db
```

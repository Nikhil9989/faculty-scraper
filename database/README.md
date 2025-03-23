# Faculty Database

This directory contains database schemas and related tools for storing faculty data scraped from university websites.

## Relational Database (PostgreSQL)

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

The relational schema follows this hierarchical structure:
- Each university has many departments
- Each department has many faculty members
- Each faculty member has many research interests and publications

### Usage

To set up the PostgreSQL database using this schema:

```bash
# Create a PostgreSQL database
createdb faculty_db

# Import the schema
psql -d faculty_db -f schema.sql
```

## NoSQL Database (MongoDB)

The `mongodb_schema.js` file defines a document-oriented schema for storing faculty information in MongoDB.

### Collections

1. **universities**
   - Stores university information with embedded departments
   - Each university document contains an array of department objects

2. **faculty**
   - Stores complete faculty profiles as single documents
   - Each faculty document contains embedded arrays for research interests and publications
   - Flexible schema allows for storing additional fields that vary between universities

### Data Model

The document-oriented schema uses:
- Embedded documents to store related data (like departments in universities)
- Arrays to store multiple values (like research interests)
- Nested document arrays for complex data (like publications)

### Benefits of NoSQL Approach

- **Schema Flexibility**: Can store different fields for different universities without schema migrations
- **Denormalized Data**: Faculty profiles are complete documents, eliminating the need for complex joins
- **Rich Data Types**: Better support for arrays and nested documents
- **Performance**: More efficient for document-oriented queries, especially with proper indexes
- **Scalability**: Horizontal scaling for large datasets

### Usage

To set up the MongoDB database:

```bash
# Start MongoDB
mongod

# Create database and collections
mongo < database/mongodb_schema.js
```

## MongoDB Connector

The `mongodb_connector.py` module provides a Python interface for interacting with the MongoDB database:

```python
from database.mongodb_connector import MongoDBConnector

# Initialize connector
connector = MongoDBConnector()

# Import data from JSON file
connector.import_from_json('faculty_data.json')

# Query faculty by university
faculty = connector.get_faculty_by_university('Stanford University')

# Query faculty by research interest
faculty = connector.get_faculty_by_research_interest('machine learning')

# Close connection
connector.close()
```

## Database Choice: SQL vs. NoSQL

Choose the appropriate database based on your specific needs:

### Use PostgreSQL When:

- You need strict data consistency and ACID transactions
- Your data has a clear, well-defined structure that doesn't change often
- You'll run complex joins and aggregations
- You need advanced querying capabilities and built-in constraints
- Reporting and analytics are a primary use case

### Use MongoDB When:

- You have semi-structured or variable data across different universities
- You need schema flexibility to easily add new fields
- Your typical access pattern is retrieving complete faculty profiles
- You want to store heterogeneous data (different attributes for different faculty)
- Your application needs need to scale horizontally with large datasets
- You're primarily doing document-oriented operations rather than complex joins

## Migrating Between Databases

The project supports both database types, allowing you to choose the best fit for your needs or even use both simultaneously for different purposes. Migration tools to convert data between the two formats will be added in a future update.

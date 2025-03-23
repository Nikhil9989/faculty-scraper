/**
 * MongoDB schema for faculty data
 * 
 * This file provides the schema design and validation rules for storing faculty data in MongoDB.
 * Unlike the SQL schema, this document-oriented approach allows for more flexibility in data structure.
 */

// University collection schema
db.createCollection("universities", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name"],
      properties: {
        name: {
          bsonType: "string",
          description: "Name of the university"
        },
        location: {
          bsonType: "string",
          description: "Location of the university"
        },
        website: {
          bsonType: "string",
          description: "University website URL"
        },
        departments: {
          bsonType: "array",
          description: "List of departments in the university",
          items: {
            bsonType: "object",
            required: ["name"],
            properties: {
              name: {
                bsonType: "string",
                description: "Name of the department"
              },
              website: {
                bsonType: "string",
                description: "Department website URL"
              }
            }
          }
        },
        created_at: {
          bsonType: "date",
          description: "Timestamp when this record was created"
        },
        updated_at: {
          bsonType: "date",
          description: "Timestamp when this record was last updated"
        }
      }
    }
  }
});

// Faculty collection schema
db.createCollection("faculty", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["first_name", "last_name", "university_name", "department_name"],
      properties: {
        first_name: {
          bsonType: "string",
          description: "First name of the faculty member"
        },
        last_name: {
          bsonType: "string",
          description: "Last name of the faculty member"
        },
        title: {
          bsonType: "string",
          description: "Academic title of the faculty member"
        },
        university_name: {
          bsonType: "string",
          description: "Name of the university where the faculty member works"
        },
        department_name: {
          bsonType: "string",
          description: "Name of the department where the faculty member works"
        },
        email: {
          bsonType: "string",
          description: "Email address of the faculty member"
        },
        profile_url: {
          bsonType: "string",
          description: "URL to the faculty member's profile page"
        },
        research_interests: {
          bsonType: "array",
          description: "List of research interests",
          items: {
            bsonType: "string"
          }
        },
        publications: {
          bsonType: "array",
          description: "List of publications",
          items: {
            bsonType: "object",
            properties: {
              title: {
                bsonType: "string",
                description: "Title of the publication"
              },
              authors: {
                bsonType: "string",
                description: "Authors of the publication"
              },
              year: {
                bsonType: "int",
                description: "Year of publication"
              },
              venue: {
                bsonType: "string",
                description: "Publication venue (journal, conference, etc.)"
              },
              url: {
                bsonType: "string",
                description: "URL to the publication"
              },
              // Additional flexible fields that might not fit well in a relational model
              citations: {
                bsonType: "int",
                description: "Number of citations"
              },
              abstract: {
                bsonType: "string",
                description: "Abstract of the publication"
              },
              keywords: {
                bsonType: "array",
                items: {
                  bsonType: "string"
                },
                description: "Keywords for the publication"
              },
              doi: {
                bsonType: "string",
                description: "Digital Object Identifier"
              }
            }
          }
        },
        // Additional flexible fields that might vary between universities
        office_location: {
          bsonType: "string",
          description: "Faculty office location"
        },
        phone: {
          bsonType: "string",
          description: "Faculty phone number"
        },
        courses: {
          bsonType: "array",
          description: "Courses taught by faculty",
          items: {
            bsonType: "object",
            properties: {
              name: {
                bsonType: "string",
                description: "Course name"
              },
              code: {
                bsonType: "string",
                description: "Course code"
              },
              description: {
                bsonType: "string",
                description: "Course description"
              },
              semester: {
                bsonType: "string",
                description: "Semester when course is taught"
              }
            }
          }
        },
        awards: {
          bsonType: "array",
          description: "Awards and recognitions",
          items: {
            bsonType: "object",
            properties: {
              name: {
                bsonType: "string",
                description: "Award name"
              },
              year: {
                bsonType: "int",
                description: "Year received"
              },
              description: {
                bsonType: "string",
                description: "Award description"
              }
            }
          }
        },
        education: {
          bsonType: "array",
          description: "Educational background",
          items: {
            bsonType: "object",
            properties: {
              degree: {
                bsonType: "string",
                description: "Degree obtained"
              },
              institution: {
                bsonType: "string",
                description: "Institution where degree was obtained"
              },
              year: {
                bsonType: "int",
                description: "Year of graduation"
              },
              field: {
                bsonType: "string",
                description: "Field of study"
              }
            }
          }
        },
        social_media: {
          bsonType: "object",
          description: "Social media profiles",
          properties: {
            google_scholar: {
              bsonType: "string",
              description: "Google Scholar profile URL"
            },
            research_gate: {
              bsonType: "string",
              description: "ResearchGate profile URL"
            },
            linkedin: {
              bsonType: "string",
              description: "LinkedIn profile URL"
            },
            twitter: {
              bsonType: "string",
              description: "Twitter profile URL"
            },
            github: {
              bsonType: "string",
              description: "GitHub profile URL"
            }
          }
        },
        scraped_at: {
          bsonType: "date",
          description: "Timestamp when this data was scraped"
        },
        created_at: {
          bsonType: "date",
          description: "Timestamp when this record was created"
        },
        updated_at: {
          bsonType: "date",
          description: "Timestamp when this record was last updated"
        }
      }
    }
  }
});

// Create indexes for faster queries
db.universities.createIndex({ name: 1 }, { unique: true });
db.faculty.createIndex({ last_name: 1, first_name: 1 });
db.faculty.createIndex({ university_name: 1 });
db.faculty.createIndex({ department_name: 1 });
db.faculty.createIndex({ email: 1 }, { unique: true, sparse: true });

// Create text index for full-text search on research interests and publications
db.faculty.createIndex(
  {
    "research_interests": "text",
    "publications.title": "text",
    "publications.abstract": "text"
  },
  {
    weights: {
      "research_interests": 10,
      "publications.title": 5,
      "publications.abstract": 2
    },
    name: "faculty_text_index"
  }
);

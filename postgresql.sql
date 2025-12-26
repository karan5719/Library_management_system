-- PostgreSQL schema for library management system
-- Drop the database if it exists to start fresh, and then create it.
-- Note: On Render, database will be created automatically

-- Table Creation
-- These tables are created first as other tables depend on them.
CREATE TABLE Author (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Publisher (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- User and employee tables
CREATE TABLE Member (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Employee (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Main data tables
CREATE TABLE Book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER REFERENCES Author(id) ON DELETE SET NULL,
    publisher_id INTEGER REFERENCES Publisher(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE Vendor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    contact VARCHAR(100)
);

-- Tables with foreign key dependencies on Book and Member
CREATE TABLE Reservation (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES Book(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES Member(id) ON DELETE CASCADE,
    reservation_date DATE
);

CREATE TABLE Fine (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES Member(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2),
    reason TEXT,
    date_assessed DATE
);

CREATE TABLE Issued_Books (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES Book(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES Member(id) ON DELETE CASCADE,
    issue_date DATE,
    return_date DATE,
    returned BOOLEAN DEFAULT FALSE
);

-- --- Data Insertion ---

-- Insert Admins
INSERT INTO Admin (username, password) VALUES ('admin', 'admin123');

-- Insert Members
INSERT INTO Member (username, email, password) VALUES 
('user1', 'user1@example.com', 'user123'),
('Himanshukumar', 'himanshu@gmail.com', 'himu123');

-- Insert Employees
INSERT INTO Employee (username, email, password) VALUES
('employee1', 'employee1@example.com', 'employee123'),
('employee2', 'employee2@example.com', 'employee123');

-- Insert Authors
INSERT INTO Author (name) VALUES 
('J.K. Rowling'), ('George Orwell'), ('Agatha Christie'), ('Stephen King'),
('Jane Austen'), ('J.R.R. Tolkien'), ('Ernest Hemingway'), ('Mark Twain'),
('Leo Tolstoy'), ('Charles Dickens');

-- Insert Publishers
INSERT INTO Publisher (name) VALUES 
('Penguin Books'), ('HarperCollins'), ('Oxford University Press'), ('Random House'),
('Simon & Schuster'), ('Hachette Book Group'), ('Macmillan Publishers'),
('Scholastic Corporation'), ('Vintage Books');

-- Insert Books (IDs correspond to the authors and publishers above)
INSERT INTO Book (title, author_id, publisher_id, quantity) VALUES
('The Shining', 4, 4, 10),
('Pride and Prejudice', 5, 1, 15),
('The Hobbit', 6, 2, 20),
('1984', 2, 1, 12),
('The Old Man and the Sea', 7, 5, 8),
('The Adventures of Tom Sawyer', 8, 8, 5),
('Anna Karenina', 9, 9, 7),
('A Tale of Two Cities', 10, 4, 11),
('It', 4, 5, 9),
('Sense and Sensibility', 5, 1, 6);

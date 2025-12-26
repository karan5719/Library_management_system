-- Drop the database if it exists to start fresh, and then create it.
CREATE DATABASE librarys_management_system;
USE librarys_management_system;

-- Table Creation
-- These tables are created first as other tables depend on them.
CREATE TABLE Author (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Publisher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- User and employee tables
CREATE TABLE Member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Employee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Main data tables
CREATE TABLE Book (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author_id INT,
  publisher_id INT,
  quantity INT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES Author(id) ON DELETE SET NULL,
  FOREIGN KEY (publisher_id) REFERENCES Publisher(id) ON DELETE SET NULL
);

CREATE TABLE Vendor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    contact VARCHAR(100)
);

-- Tables with foreign key dependencies on Book and Member
CREATE TABLE Reservation (
  id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  member_id INT,
  reservation_date DATE,
  FOREIGN KEY (book_id) REFERENCES Book(id) ON DELETE CASCADE,
  FOREIGN KEY (member_id) REFERENCES Member(id) ON DELETE CASCADE
);

CREATE TABLE Fine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    amount DECIMAL(10, 2),
    reason TEXT,
    date_assessed DATE,
    FOREIGN KEY (member_id) REFERENCES Member(id) ON DELETE CASCADE
);

-- --- Data Insertion ---

-- Insert Admins
INSERT INTO Admin (username, password) VALUES ('admin', 'admin123');

-- Insert Members
INSERT INTO Member (username, email, password) VALUES ('user1', 'user1@example.com', 'user123');
INSERT INTO Member (username, email, password) VALUES ('Himanshukumar', 'himanshu@gmail.com', 'himu123');

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
USE librarys_management_system;
CREATE TABLE Issued_Books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    member_id INT,
    issue_date DATE,
    return_date DATE,
    returned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (book_id) REFERENCES Book(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Member(id) ON DELETE CASCADE
);
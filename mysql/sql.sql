CREATE DATABASE IF NOT EXISTS LibrarySystem;
USE LibrarySystem;
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY,
    CategoryName VARCHAR(50) NOT NULL UNIQUE
);

-- Creating Authors Table
CREATE TABLE Authors (
    AuthorID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL
);

-- Creating Books Table with Foreign Keys and Check Constraints
CREATE TABLE Books (
    BookID INT PRIMARY KEY,
    Title VARCHAR(100) NOT NULL,
    AuthorID INT,
    CategoryID INT,
    Price DECIMAL(10, 2) CHECK (Price >= 0),
    Quantity INT DEFAULT 0 CHECK (Quantity >= 0),
    ISBN VARCHAR(20) UNIQUE,
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- Creating Members Table
CREATE TABLE Members (
    MemberID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    JoinDate DATE DEFAULT (CURRENT_DATE)
);

-- Creating Loans Table
CREATE TABLE Loans (
    LoanID INT PRIMARY KEY,
    BookID INT,
    MemberID INT,
    LoanDate DATE DEFAULT (CURRENT_DATE),
    DueDate DATE,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);
INSERT INTO Categories (CategoryID, CategoryName) VALUES (1, 'Fiction');
INSERT INTO Authors (AuthorID, FirstName, LastName) VALUES (1, 'Stephen', 'King');
INSERT INTO Books (BookID, Title, AuthorID, CategoryID, Price, Quantity, ISBN) 
VALUES (1, 'The Shining', 1, 1, 15.99, 5, '978-0385121675');

-- Updating Data
UPDATE Books SET Price = 17.50 WHERE BookID = 1;

-- Deleting Data
DELETE FROM Loans WHERE LoanID = 2;
SELECT * FROM Books;

-- Aggregate Functions
SELECT COUNT(*) AS TotalBooks FROM Books;
SELECT SUM(Quantity) AS TotalStock FROM Books;
SELECT AVG(Price) AS AveragePrice FROM Books;
SELECT MIN(Price) AS MinPrice FROM Books;
SELECT MAX(Price) AS MaxPrice FROM Books;
SELECT FirstName FROM Authors
UNION
SELECT FirstName FROM Members;
-- INNER JOIN: Books with Authors and Categories
SELECT b.Title, a.FirstName, a.LastName, c.CategoryName
FROM Books b
INNER JOIN Authors a ON b.AuthorID = a.AuthorID
INNER JOIN Categories c ON b.CategoryID = c.CategoryID;

-- LEFT JOIN: All Members and their loans
SELECT m.FirstName, m.LastName, l.LoanID
FROM Members m
LEFT JOIN Loans l ON m.MemberID = l.MemberID;

-- RIGHT JOIN: All Loans and their members
SELECT l.LoanID, m.FirstName, m.LastName
FROM Loans l
RIGHT JOIN Members m ON l.MemberID = m.MemberID;

-- CROSS JOIN: Cartesian Product
SELECT b.Title, m.FirstName FROM Books b CROSS JOIN Members m;
-- Scalar Subquery: Books priced above average
SELECT Title, Price FROM Books 
WHERE Price > (SELECT AVG(Price) FROM Books);

-- Multi-row Subquery: Authors in 'Science' category
SELECT FirstName, LastName FROM Authors
WHERE AuthorID IN (
    SELECT AuthorID FROM Books 
    WHERE CategoryID = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Science')
);

-- Correlated Subquery: Books priced above their category average
SELECT b1.Title, b1.Price, b1.CategoryID
FROM Books b1
WHERE b1.Price > (
    SELECT AVG(b2.Price) 
    FROM Books b2 
    WHERE b2.CategoryID = b1.CategoryID
);
-- Creating a View for Active Loans
CREATE VIEW View_ActiveLoans AS
SELECT l.LoanID, b.Title, m.FirstName, m.LastName, l.DueDate
FROM Loans l
JOIN Books b ON l.BookID = b.BookID
JOIN Members m ON l.MemberID = m.MemberID
WHERE l.ReturnDate IS NULL;

-- Using the View
SELECT * FROM View_ActiveLoans;
-- TCL Examples
COMMIT;    -- Save changes
ROLLBACK;  -- Undo changes
SAVEPOINT S1; -- Set a checkpoint

-- DCL Examples
GRANT SELECT ON Books TO PUBLIC; -- Give permission
REVOKE UPDATE ON Books FROM PUBLIC; -- Remove permission
-- STORED PROCEDURE: Add New Book
DELIMITER //
CREATE PROCEDURE AddNewBook(IN p_ID INT, IN p_Title VARCHAR(100), IN p_AuthorID INT)
BEGIN
    INSERT INTO Books (BookID, Title, AuthorID) VALUES (p_ID, p_Title, p_AuthorID);
END //
DELIMITER ;

-- FUNCTION: Get Stock Level
DELIMITER //
CREATE FUNCTION GetTotalBooksByCategory(p_ID INT) RETURNS INT DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT SUM(Quantity) INTO total FROM Books WHERE CategoryID = p_ID;
    RETURN IFNULL(total, 0);
END //
DELIMITER ;

-- TRIGGER: Decrease Stock on Loan
DELIMITER //
CREATE TRIGGER After_Loan_Insert AFTER INSERT ON Loans FOR EACH ROW
BEGIN
    UPDATE Books SET Quantity = Quantity - 1 WHERE BookID = NEW.BookID;
END //
DELIMITER ;

-- CURSOR: Process rows one by one
DELIMITER //
CREATE PROCEDURE PrintAllTitles()
BEGIN
    DECLARE b_title VARCHAR(100);
    DECLARE cur CURSOR FOR SELECT Title FROM Books;
    -- (Open, Fetch, Close logic inside loop)
END //
DELIMITER ;
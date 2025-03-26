-- 1. Create the database and select it
CREATE DATABASE IF NOT EXISTS spaza_safe;
USE spaza_safe;

-- 2. Create Manufacturer Table
CREATE TABLE Manufacturer (
    license_key INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    address TEXT,
    location VARCHAR(255),
    mpassword VARCHAR(15) NOT NULL UNIQUE
);

-- 3. Create Spaza_Owner Table
CREATE TABLE Spaza_Owner (
    owner_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    oname VARCHAR(255) NOT NULL,
    opassword VARCHAR(15) NOT NULL UNIQUE
);

-- 4. Create Product Table
CREATE TABLE Product (
    prod_barcode VARCHAR(15) NOT NULL PRIMARY KEY,
    prod_name VARCHAR(255) NOT NULL,
    prod_price DECIMAL(10,2) NOT NULL,
    prod_expiry_date DATE NOT NULL,
    prod_manu_date DATE NOT NULL,
    license_key INT NOT NULL,
    FOREIGN KEY (license_key) REFERENCES Manufacturer(license_key) ON DELETE CASCADE
);

-- 5. Create Spaza_Shop Table
CREATE TABLE Spaza_Shop (
    registration_no INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sname VARCHAR(255) NOT NULL,
    stock INT NOT NULL,
    owner_id INT NOT NULL,
    location VARCHAR(255),
    item_barcode VARCHAR(15) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES Spaza_Owner(owner_id) ON DELETE CASCADE
);

-- 6. Create Customer Table
CREATE TABLE Customer (
    cust_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    item_barcode VARCHAR(15) NOT NULL,
    item VARCHAR(50),
    qty INT NOT NULL,
    FOREIGN KEY (item_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);

-- 7. Create Government_Authorities Table
CREATE TABLE Government_Authorities (
    registration_no INT NOT NULL PRIMARY KEY,
    gov_name VARCHAR(50) NOT NULL,
    contact_info VARCHAR(12),
    location VARCHAR(255)
);

-- 8. Create Relationship Table: prd_cust (Product - Customer)
CREATE TABLE prd_cust (
    prod_barcode VARCHAR(15) NOT NULL,
    cust_id INT NOT NULL,
    PRIMARY KEY (prod_barcode, cust_id),
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE,
    FOREIGN KEY (cust_id) REFERENCES Customer(cust_id) ON DELETE CASCADE
);

-- 9. Create Relationship Table: spz_gov (Spaza Shop - Government Authorities)
CREATE TABLE spz_gov (
    registration_no INT NOT NULL,
    issue_id INT NOT NULL PRIMARY KEY,
    FOREIGN KEY (registration_no) REFERENCES Government_Authorities(registration_no) ON DELETE CASCADE
);

-- 10. Create Relationship Table: spz_prd (Spaza Shop - Product)
CREATE TABLE spz_prd (
    registration_no INT NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    PRIMARY KEY (registration_no, prod_barcode),
    FOREIGN KEY (registration_no) REFERENCES Spaza_Shop(registration_no) ON DELETE CASCADE,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);

-- 11. Create Inventory_Tracker Table
CREATE TABLE Inventory_Tracker (
    purchase_id VARCHAR(50) NOT NULL PRIMARY KEY,
    Stk_qty INT NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);

--------------------------------------------------------------------------------
-- Now, insert data in the correct order based on foreign key dependencies.
--------------------------------------------------------------------------------

-- A. Insert into Manufacturer (no dependencies)
INSERT INTO Manufacturer (company_name, address, location, mpassword)
VALUES ('Vaseline Inc.', '123 Vaseline Rd', 'Johannesburg', 'password123');

-- B. Insert into Spaza_Owner (no dependencies)
INSERT INTO Spaza_Owner (oname, opassword)
VALUES ('John Doe', 'spazaownerpass');

-- C. Insert into Product (requires valid Manufacturer license_key)
-- Note: '5099802150117' is the barcode, and we assume the Manufacturer inserted above has license_key = 1.
INSERT INTO Product (prod_barcode, prod_name, prod_price, prod_expiry_date, prod_manu_date, license_key)
VALUES ('5099802150117', 'Vaseline Lip Therapy', 30.0, '2025-05-01', '2023-05-01', 1);

-- D. Insert into Spaza_Shop (requires a valid Spaza_Owner; item_barcode should reference an existing Product)
-- Here, we assume owner_id from Spaza_Owner is 1.
INSERT INTO Spaza_Shop (sname, stock, owner_id, location, item_barcode)
VALUES ('Doe’s Spaza Shop', 100, 1, 'Johannesburg', '5099802150117');

-- E. Insert into Customer (requires valid Product barcode)
INSERT INTO Customer (item_barcode, item, qty)
VALUES ('5099802150117', 'Vaseline Lip Therapy', 2);

-- F. Insert into Government_Authorities (no dependency on other tables)
INSERT INTO Government_Authorities (registration_no, gov_name, contact_info, location)
VALUES (1, 'South African Revenue Service', '0123456789', 'Pretoria');

-- G. Insert into prd_cust (relationship between Product and Customer)
-- Assumes the Customer inserted above has cust_id = 1.
INSERT INTO prd_cust (prod_barcode, cust_id)
VALUES ('5099802150117', 1);

-- H. Insert into spz_gov (relationship between Spaza Shop and Government Authorities)
INSERT INTO spz_gov (registration_no, issue_id)
VALUES (1, 101);

-- I. Insert into spz_prd (relationship between Spaza Shop and Product)
INSERT INTO spz_prd (registration_no, prod_barcode)
VALUES (1, '5099802150117');

-- J. Insert into Inventory_Tracker (requires valid Product barcode)
INSERT INTO Inventory_Tracker (purchase_id, Stk_qty, prod_barcode)
VALUES ('INV001', 50, '5099802150117');

-- Create the Spaza.Safe database
CREATE DATABASE spaza_safe;
USE spaza_safe;

-- Manufacturer Table
CREATE TABLE Manufacturer (
    license_key INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    address TEXT,
    location VARCHAR(255),
    password VARCHAR(255) NOT NULL
);

-- Spaza Owner Table
CREATE TABLE Spaza_Owner (
    owner_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Spaza Shop Table
CREATE TABLE Spaza_Shop (
    registration_no INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sname VARCHAR(255) NOT NULL,
    stock INT NOT NULL,
    owner_id INT NOT NULL,
    location VARCHAR(255),
    FOREIGN KEY (owner_id) REFERENCES Spaza_Owner(owner_id) ON DELETE CASCADE
);

-- Customer Table
CREATE TABLE Customer (
    cust_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
);

-- Government Authorities Table
CREATE TABLE Government_Authorities (
    registration_no INT NOT NULL PRIMARY KEY
);

-- Product Table
CREATE TABLE Product (
    prod_barcode VARCHAR(50) NOT NULL PRIMARY KEY,
    prod_name VARCHAR(255) NOT NULL,
    prod_price DECIMAL(10,2) NOT NULL,
    prod_expiry_date DATE NOT NULL,
    prod_manu_date DATE NOT NULL,
    license_key INT NOT NULL,
    FOREIGN KEY (license_key) REFERENCES Manufacturer(license_key) ON DELETE CASCADE
);

-- Relationship: Product - Customer (prd_cust)
CREATE TABLE prd_cust (
    prod_barcode VARCHAR(50) NOT NULL,
    cust_id INT NOT NULL,
    PRIMARY KEY (prod_barcode, cust_id),
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE,
    FOREIGN KEY (cust_id) REFERENCES Customer(cust_id) ON DELETE CASCADE
);

-- Relationship: Spaza Shop - Government Authorities (spz_gov)
CREATE TABLE spz_gov (
    registration_no INT NOT NULL,
    issue_id INT NOT NULL PRIMARY KEY,
    FOREIGN KEY (registration_no) REFERENCES Government_Authorities(registration_no) ON DELETE CASCADE
);

-- Relationship: Spaza Shop - Product (spz_prd)
CREATE TABLE spz_prd (
    registration_no INT NOT NULL,
    prod_barcode VARCHAR(50) NOT NULL,
    PRIMARY KEY (registration_no, prod_barcode),
    FOREIGN KEY (registration_no) REFERENCES Spaza_Shop(registration_no) ON DELETE CASCADE,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);

-- Inventory Tracker Table
CREATE TABLE Inventory_Tracker (
    item_barcode VARCHAR(50) NOT NULL PRIMARY KEY,
    prod_barcode VARCHAR(50) NOT NULL,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);



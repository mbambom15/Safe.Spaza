-- 1. Create the database and select it
CREATE DATABASE IF NOT EXISTS spaza_safe;
USE spaza_safe;

-- 2. Create Manufacturer Table
CREATE TABLE Manufacturer (
    license_key INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    address TEXT,
    location VARCHAR(255),
    mpassword VARCHAR(15) NOT NULL UNIQUE,
    creationdate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);
-- 3. Create Spaza_Owner Table
CREATE TABLE Spaza_Owner (
    owner_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    oname VARCHAR(255) NOT NULL,
    opassword VARCHAR(15) NOT NULL,
    phone_number VARCHAR(15),
    business_name VARCHAR(255) NOT NULL,
    business_reg_number VARCHAR(50) NOT NULL UNIQUE,
    creationdate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);
-- 4. Create Spaza_Shop Table
CREATE TABLE Spaza_Shop (
    business_reg_number VARCHAR(50) NOT NULL PRIMARY KEY,
    sname VARCHAR(255) NOT NULL,
    owner_id INT NOT NULL,
    location VARCHAR(255),
    FOREIGN KEY (owner_id) REFERENCES Spaza_Owner(owner_id) ON DELETE CASCADE,
    FOREIGN KEY (business_reg_number) REFERENCES Spaza_Owner(business_reg_number)
);

-- 5. Create Product Table
CREATE TABLE Product (
    prod_barcode VARCHAR(15) NOT NULL PRIMARY KEY,
    prod_name VARCHAR(255) NOT NULL,
    prod_price DECIMAL(10,2) NOT NULL,
    prod_expiry_date DATE NOT NULL,
    prod_manu_date DATE NOT NULL,
    license_key INT NOT NULL,
    prod_quantity INT NOT NULL,
    time_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    prod_image_url VARCHAR(255),
    FOREIGN KEY (license_key) REFERENCES Manufacturer(license_key) ON DELETE CASCADE
);
-- 6. Create Shop_Inventory Table
CREATE TABLE Shop_Inventory (
    inventory_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    business_reg_number VARCHAR(50) NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    shop_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE,
    FOREIGN KEY (business_reg_number) REFERENCES Spaza_Shop(business_reg_number),
    UNIQUE (business_reg_number, prod_barcode)
);
-- 7. Create Customer Table
CREATE TABLE Customer (
    cust_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    telephone VARCHAR(100) NOT NULL,
    cpassword VARCHAR(50) NOT NULL UNIQUE,
    creationdate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);

-- 8. Create Government_Authority Table
CREATE TABLE Government_Authority (
    registration_no INT NOT NULL PRIMARY KEY,
    gov_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,  -- Added email field
    contact_info VARCHAR(12),
    location VARCHAR(255),
    gpassword VARCHAR(255) NOT NULL
);

-- 9. Create prd_cust Table
CREATE TABLE prd_cust (
    prod_barcode VARCHAR(15) NOT NULL,
    cust_id INT NOT NULL,
    PRIMARY KEY (prod_barcode, cust_id),
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE,
    FOREIGN KEY (cust_id) REFERENCES Customer(cust_id) ON DELETE CASCADE
);

-- 10. Create spz_gov Table
CREATE TABLE spz_gov (
    registration_no INT NOT NULL,
    issue_id INT NOT NULL PRIMARY KEY,
    FOREIGN KEY (registration_no) REFERENCES Government_Authority(registration_no) ON DELETE CASCADE
);

-- ❌ FIXED HERE: `Spaza_Shop` does NOT have a `registration_no`, so this FK would fail.
-- → Replaced `registration_no` with `business_reg_number` to match existing PK in Spaza_Shop
-- 11. Create spz_prd Table
CREATE TABLE spz_prd (
    business_reg_number VARCHAR(50) NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    PRIMARY KEY (business_reg_number, prod_barcode),
    FOREIGN KEY (business_reg_number) REFERENCES Spaza_Shop(business_reg_number) ON DELETE CASCADE,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE
);

-- 12. Create Product_Analytics Table
CREATE TABLE Product_Analytics (
    analytics_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cust_id INT NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    action_type ENUM('ADD_TO_CART', 'PURCHASED') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    store_id VARCHAR(50),
    FOREIGN KEY (cust_id) REFERENCES Customer(cust_id) ON DELETE CASCADE,
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES Spaza_Shop(business_reg_number)
);

-- Create Shopping Cart Table
CREATE TABLE Shopping_Cart (
    cart_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cust_id INT NOT NULL,
    business_reg_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (cust_id) REFERENCES Customer(cust_id),
    FOREIGN KEY (business_reg_number) REFERENCES Spaza_Shop(business_reg_number)
);

-- Create Cart Items Table
CREATE TABLE Cart_Items (
    item_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    prod_barcode VARCHAR(15) NOT NULL,
    quantity INT NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES Shopping_Cart(cart_id),
    FOREIGN KEY (prod_barcode) REFERENCES Product(prod_barcode)
);

CREATE TABLE Expired_Product_Reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    product_barcode VARCHAR(15) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    expiry_date DATE NOT NULL,
    business_reg_number VARCHAR(50) NOT NULL,
    shop_name VARCHAR(255) NOT NULL,
    shop_location VARCHAR(255) NOT NULL,
    customer_id INT NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PENDING', 'INVESTIGATING', 'RESOLVED') DEFAULT 'PENDING',
    investigation_notes TEXT
);

-- 13. Create ManufacturerProductsReport View
CREATE OR REPLACE VIEW ManufacturerProductsReport AS
    SELECT 
        p.prod_barcode AS barcode,
        p.prod_name AS product_name,
        p.prod_price AS price,
        p.prod_quantity AS quantity,
        p.prod_manu_date AS manufacture_date,
        p.prod_expiry_date AS expiry_date,
        DATEDIFF(p.prod_expiry_date, CURDATE()) AS days_until_expiry,
        CASE
            WHEN DATEDIFF(p.prod_expiry_date, CURDATE()) < 0 THEN 'EXPIRED'
            WHEN DATEDIFF(p.prod_expiry_date, CURDATE()) <= 30 THEN 'EXPIRING SOON'
            ELSE 'VALID'
        END AS expiry_status,
        p.time_created AS added_date,
        m.license_key,
        m.company_name,
        m.address,
        m.location,
        m.creationdate AS manufacturer_created,
        m.last_login AS manufacturer_last_login
    FROM
        Product p
            JOIN
        Manufacturer m ON p.license_key = m.license_key;
        
        -- Create comprehensive customer history view
CREATE OR REPLACE VIEW CustomerFullHistory AS
SELECT 
    c.cust_id,
    c.email,
    c.telephone,
    c.creationdate AS account_created,
    c.last_login,
    
    -- Purchase history
    sc.cart_id,
    sc.created_at AS purchase_date,
    ss.sname AS store_name,
    ss.location AS store_location,
    p.prod_barcode,
    p.prod_name,
    ci.quantity,
    ci.price_per_unit,
    (ci.quantity * ci.price_per_unit) AS total_price,
    
    -- Report history
    epr.report_id,
    epr.product_name AS reported_product,
    epr.expiry_date AS reported_expiry,
    epr.shop_name AS reported_shop,
    epr.report_date,
    epr.status AS report_status,
    
    -- Account activity flags
    CASE WHEN sc.cart_id IS NOT NULL THEN 1 ELSE 0 END AS has_purchases,
    CASE WHEN epr.report_id IS NOT NULL THEN 1 ELSE 0 END AS has_reports
    
FROM Customer c
-- Left joins to include customers with no purchases/reports
LEFT JOIN Shopping_Cart sc 
    ON c.cust_id = sc.cust_id 
    AND sc.is_active = FALSE  -- Only completed purchases
LEFT JOIN Cart_Items ci 
    ON sc.cart_id = ci.cart_id
LEFT JOIN Product p 
    ON ci.prod_barcode = p.prod_barcode
LEFT JOIN Spaza_Shop ss 
    ON sc.business_reg_number = ss.business_reg_number
LEFT JOIN Expired_Product_Reports epr 
    ON c.cust_id = epr.customer_id;
    
-- create view for the spaza owner

CREATE OR REPLACE VIEW SpazaOwnerFullReport AS
SELECT 
    -- Owner details
    so.owner_id,
    so.oname AS owner_name,
    so.phone_number,
    so.business_name,
    so.business_reg_number,
    so.creationdate AS account_created,
    so.last_login,
    
    -- Shop details
    ss.sname AS shop_name,
    ss.location AS shop_location,
    
    -- Inventory analytics
    inv_stats.total_products,
    inv_stats.inventory_value,
    inv_stats.low_stock_items,
    inv_stats.expiring_soon,
    
    -- Sales analytics
    sales_stats.total_purchases,
    sales_stats.total_revenue,
    
    -- Individual product details (flat structure)
    prod.prod_barcode,
    prod.prod_name,
    si.shop_price,
    si.stock_quantity,
    si.last_updated,
    prod.prod_expiry_date,
    DATEDIFF(prod.prod_expiry_date, CURDATE()) AS days_until_expiry,
    CASE 
        WHEN DATEDIFF(prod.prod_expiry_date, CURDATE()) < 0 THEN 'EXPIRED'
        WHEN DATEDIFF(prod.prod_expiry_date, CURDATE()) <= 7 THEN 'EXPIRING SOON'
        ELSE 'VALID'
    END AS expiry_status,
    
    -- Individual report details (flat structure)
    epr.report_id,
    epr.product_name AS reported_product,
    epr.expiry_date AS reported_expiry,
    epr.customer_email AS reporter_email,
    epr.report_date,
    epr.status AS report_status

FROM Spaza_Owner so
JOIN Spaza_Shop ss 
    ON so.business_reg_number = ss.business_reg_number

-- Inventory analytics subquery
LEFT JOIN (
    SELECT 
        si.business_reg_number,
        COUNT(*) AS total_products,
        SUM(si.shop_price * si.stock_quantity) AS inventory_value,
        SUM(CASE WHEN si.stock_quantity < 10 THEN 1 ELSE 0 END) AS low_stock_items,
        SUM(CASE WHEN DATEDIFF(p.prod_expiry_date, CURDATE()) <= 7 THEN 1 ELSE 0 END) AS expiring_soon
    FROM Shop_Inventory si
    JOIN Product p ON si.prod_barcode = p.prod_barcode
    GROUP BY si.business_reg_number
) AS inv_stats 
    ON so.business_reg_number = inv_stats.business_reg_number

-- Sales analytics subquery
LEFT JOIN (
    SELECT 
        sc.business_reg_number,
        COUNT(DISTINCT sc.cart_id) AS total_purchases,
        SUM(ci.quantity * ci.price_per_unit) AS total_revenue
    FROM Shopping_Cart sc
    JOIN Cart_Items ci ON sc.cart_id = ci.cart_id
    WHERE sc.is_active = FALSE
    GROUP BY sc.business_reg_number
) AS sales_stats 
    ON so.business_reg_number = sales_stats.business_reg_number

-- Flat inventory and product details
LEFT JOIN Shop_Inventory si 
    ON so.business_reg_number = si.business_reg_number
LEFT JOIN Product prod 
    ON si.prod_barcode = prod.prod_barcode

-- Flat report details
LEFT JOIN Expired_Product_Reports epr 
    ON so.business_reg_number = epr.business_reg_number;
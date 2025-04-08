-- Create Customer Information Table
CREATE TABLE Customer_Information (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_username VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    account_balance DECIMAL(10,2) NOT NULL
);

-- Create Booking Information Table
CREATE TABLE Booking_Information (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_type VARCHAR(50) NOT NULL,
    date_of_booking TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    booking_status ENUM('Cancelled', 'Confirmed', 'Pending') NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    outstanding_balance DECIMAL(10,2)
);

-- Create Payment Information Table
CREATE TABLE Payment_Information (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Credit Card', 'PayPal', 'Bank Transfer') NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Booking_Information(booking_id)
);


ALTER TABLE Customer_Information AUTO_INCREMENT = 0;

SET @max_id = (SELECT MAX(customer_id) FROM Customer_Information);
SET @auto_increment_value = IFNULL(@max_id, 0) + 1;

SET @sql = CONCAT('ALTER TABLE Customer_Information AUTO_INCREMENT = ', @auto_increment_value);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- Insert records
INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Kemar', 'Christie', 'kemar.christie@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Roberto', 'James', 'roberto.james@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Dwayne', 'Gibbs', 'dwayne.gibbs@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Tyoni', 'Davis', 'tyoni.davis@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Danielle', 'Jones', 'danielle.jones@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('David', 'White', 'david.white@example.com', 40000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Benjamin', 'Robinson', 'benjamin.robinson@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Marcus', 'Manley', 'marcus.manley@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Aaliyah', 'Mitchell', 'aaliyah.mitchell@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

INSERT INTO Customer_Information (first_name, last_name, email_address, account_balance)
VALUES ('Adrianna', 'Marsh', 'adrianna.marsh@example.com', 50000.00);

-- Manually call the procedure (grab the last inserted ID)
CALL generate_customer_username(LAST_INSERT_ID());

-- Update payment and balance should be calculated
CALL insert_payment_and_update_balance(1, 100.00);
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


DELIMITER $$

CREATE PROCEDURE AddCustomer
(
    IN firstName VARCHAR(100),
    IN lastName VARCHAR(100),
    IN emailAddress VARCHAR(255),
    IN accountBalance DECIMAL(10,2)
)
BEGIN
    DECLARE maxCustomerId INT DEFAULT 0;
    DECLARE newCustomerId INT;

    -- Find the current highest customer_id in the table
    SELECT IFNULL(MAX(customer_id), 0) INTO maxCustomerId FROM Customer_Information;

    -- Increment the highest customer_id by 1 to get the new customer_id
    SET newCustomerId = maxCustomerId + 1;

    -- Generate the username using first 3 letters of first name, last name, and new customer_id
    SET @username = CONCAT(SUBSTRING(firstName, 1, 3), '_', SUBSTRING(lastName, 1, 3), newCustomerId);

    -- Insert the new customer record into the Customer_Information table
    INSERT INTO Customer_Information (customer_id, customer_username, first_name, last_name, email_address, account_balance)
    VALUES (newCustomerId, @username, firstName, lastName, emailAddress, accountBalance);
END$$

DELIMITER ;


-- Insert records
CALL AddCustomer('Kemar', 'Christie', 'kemar.christie@example.com', 50000.00);
CALL AddCustomer('Roberto', 'James', 'roberto.james@example.com', 50000.00);
CALL AddCustomer('Dwayne', 'Gibbs', 'dwayne.gibbs@example.com', 50000.00);
CALL AddCustomer('Tyoni', 'Davis', 'tyoni.davis@example.com', 50000.00);
CALL AddCustomer('Danielle', 'Jones', 'danielle.jones@example.com', 50000.00);
CALL AddCustomer('David', 'White', 'david.white@example.com', 40000.00);
CALL AddCustomer('Benjamin', 'Robinson', 'benjamin.robinson@example.com', 50000.00);
CALL AddCustomer('Marcus', 'Manley', 'marcus.manley@example.com', 50000.00);
CALL AddCustomer('Aaliyah', 'Mitchell', 'aaliyah.mitchell@example.com', 50000.00);
CALL AddCustomer('Adrianna', 'Marsh', 'adrianna.marsh@example.com', 50000.00);


-- Update payment and balance should be calculated
CALL insert_payment_and_update_balance(1, 100.00);
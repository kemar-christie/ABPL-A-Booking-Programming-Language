-- Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
-- Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

-- Create Customer Information Table
CREATE TABLE Customer_Information (
    customer_id INT PRIMARY KEY,
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
    outstanding_balance DECIMAL(10,2),
    customer_username VARCHAR(20),
    FOREIGN KEY (customer_username) REFERENCES Customer_Information(customer_username)
);


-- Create Payment Information Table
CREATE TABLE Payment_Information (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_paid DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Booking_Information(booking_id)
);



-- Procedure to Insert Booking And Payment With BalanceCheck
DELIMITER $$

CREATE PROCEDURE InsertBookingAndPaymentWithBalanceCheck (
    IN p_booking_type VARCHAR(50),     -- Type of booking (e.g., hotel, flight)
    IN p_total_price DECIMAL(10,2),    -- Total price of the booking
    IN p_amount_paid DECIMAL(10,2),    -- Amount paid by the customer
    IN p_username VARCHAR(20)          -- Username of the customer
)
BEGIN
    DECLARE new_booking_id INT;                           -- To store the auto-generated booking ID
    DECLARE calculated_outstanding_balance DECIMAL(10,2); -- Outstanding balance to be calculated
    DECLARE booking_status ENUM('Cancelled', 'Confirmed', 'Pending'); -- Booking status based on payment
    DECLARE user_balance DECIMAL(10,2);                   -- Current account balance of the user

    -- Step 1: Retrieve the user's account balance from Customer_Information
    SELECT account_balance
    INTO user_balance
    FROM Customer_Information
    WHERE customer_username = p_username;

    -- Step 2: Check if the user's balance is sufficient for the payment
    IF user_balance >= p_amount_paid THEN
        -- Step 3: Deduct the payment amount from the user's account balance
        UPDATE Customer_Information
        SET account_balance = account_balance - p_amount_paid
        WHERE customer_username = p_username;

        -- Step 4: Calculate the outstanding balance
        SET calculated_outstanding_balance = p_total_price - p_amount_paid;

        -- Step 5: Determine the booking status
        IF calculated_outstanding_balance = 0 THEN
            SET booking_status = 'Confirmed';
        ELSE
            SET booking_status = 'Pending';
        END IF;

        -- Step 6: Insert Booking Information
        INSERT INTO Booking_Information (
            booking_type,
            date_of_booking,
            booking_status,
            total_price,
            outstanding_balance,
            customer_username
        )
        VALUES (
            p_booking_type,
            CURRENT_TIMESTAMP,
            booking_status,
            p_total_price,
            calculated_outstanding_balance,
            p_username
        );

        -- Step 7: Retrieve the auto-generated booking ID
        SET new_booking_id = LAST_INSERT_ID();

        -- Step 8: Insert Payment Information
        INSERT INTO Payment_Information (
            booking_id,
            payment_date,
            amount_paid
        )
        VALUES (
            new_booking_id,
            CURRENT_TIMESTAMP,
            p_amount_paid
        );

        -- Step 9: Return the booking ID
        SELECT new_booking_id AS booking_id;

    ELSE
        -- Insufficient balance
        SELECT CONCAT('Error: Insufficient funds. User ', p_username, ' has only ', user_balance, ' available.') AS result_message;
    END IF;
END$$

DELIMITER ;



-- Procedure to Cancel Bookings
DELIMITER $$

CREATE PROCEDURE CancelBooking (
    IN p_booking_id INT                -- The booking ID to cancel
)
BEGIN
    -- Step 1: Check if the booking exists
    IF EXISTS (
        SELECT 1 FROM Booking_Information
        WHERE booking_id = p_booking_id
    ) THEN
        -- Step 2: Update the booking status to 'Cancelled'
        UPDATE Booking_Information
        SET booking_status = 'Cancelled'
        WHERE booking_id = p_booking_id;

        -- Return a success message
        SELECT CONCAT('Booking ID ', p_booking_id, ' has been cancelled, but all information is retained.') AS result_message;
    ELSE
        -- If the booking does not exist, return an error message
        SELECT CONCAT('Booking ID ', p_booking_id, ' does not exist.') AS result_message;
    END IF;
END$$

DELIMITER ;



-- Procedure to Add a Partial Payment
DELIMITER $$

CREATE PROCEDURE AddPartialPayment(
    IN bookingId INT,
    IN amountPaid DECIMAL(10,2)
)
BEGIN
    DECLARE customerBalance DECIMAL(10,2);
    DECLARE outstandingBalance DECIMAL(10,2);

    -- Retrieve the customer's account balance and outstanding balance using a JOIN
    SELECT c.account_balance, b.outstanding_balance
    INTO customerBalance, outstandingBalance
    FROM Customer_Information c
    JOIN Booking_Information b
    ON c.customer_username = b.customer_username
    WHERE b.booking_id = bookingId;

    -- Check if the payment exceeds the outstanding balance
    IF amountPaid > outstandingBalance THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment amount exceeds the outstanding balance.';
    ELSE
        -- Check if the customer has enough funds
        IF customerBalance >= amountPaid THEN
            -- Deduct the payment amount from the account balance
            UPDATE Customer_Information c
            JOIN Booking_Information b
            ON c.customer_username = b.customer_username
            SET c.account_balance = c.account_balance - amountPaid
            WHERE b.booking_id = bookingId;

            -- Add a payment record
            INSERT INTO Payment_Information (booking_id, amount_paid)
            VALUES (bookingId, amountPaid);

            -- Update the outstanding balance in the Booking_Information table
            UPDATE Booking_Information
            SET outstanding_balance = outstanding_balance - amountPaid
            WHERE booking_id = bookingId;

            -- Send success message
            SELECT CONCAT('Payment of ', amountPaid, ' for booking ID ', bookingId, ' was successful.') AS SuccessMessage;

        ELSE
            -- Handle insufficient funds
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient funds for the payment.';
        END IF;
    END IF;
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
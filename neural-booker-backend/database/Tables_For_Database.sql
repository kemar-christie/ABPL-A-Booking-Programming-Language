-- Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
-- Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

-- Query to Create Customer Information Table.
CREATE TABLE Customer_Information
(
	customer_id SERIAL PRIMARY KEY,
	customer_username VARCHAR(20) NOT NULL,
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR(100) NOT NULL,
	email_address VARCHAR(255) UNIQUE NOT NULL,
	balance NUMERIC(10,2) NOT NULL
);

-- Query to Create Booking Information Table
CREATE TABLE Booking_Information
(
	booking_id SERIAL PRIMARY KEY,
	booking_type VARCHAR(50) NOT NULL,
	date_of_booking TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
	booking_status booking_status_enum NOT NULL
);

-- Query to Create Payment Information Table
CREATE TABLE Payment_Information
(
	payment_id SERIAL PRIMARY KEY,
	booking_id INT NOT NULL,
	total_price NUMERIC(10,2) NOT NULL,
    amount_paid NUMERIC(10,2) NOT NULL,
    balance NUMERIC(10,2) GENERATED ALWAYS AS (total_price - amount_paid) STORED,
	payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	payment_method payment_method_enum NOT NULL,
	FOREIGN KEY (booking_id) REFERENCES Booking_Information(booking_id)
);


-- Query to Set Timezone for Database Session.
SET TIMEZONE='America/Jamaica';

-- Query to show timezone in use.
SHOW TIMEZONE;

-- Query for Commenting on Columns.
COMMENT ON COLUMN your_table.column_name IS 'Comment';

--Query for commenting on tables.
COMMENT ON TABLE your_table IS 'Comment.';

--Enum Creation for Booking Information Table and Payment Information Table.
CREATE TYPE booking_status_enum AS ENUM ('Cancelled', 'Confirmed', 'Pending');
CREATE TYPE payment_method_enum AS ENUM ('Credit Card', 'PayPal', 'Bank Transfer');
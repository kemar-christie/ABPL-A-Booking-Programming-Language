-- Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
-- Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

CREATE TABLE "Customer_Information"
(
	customer_id SERIAL PRIMARY KEY,
	customer_username VARCHAR(20),
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR(100) NOT NULL,
	email_address VARCHAR(255) UNIQUE NOT NULL,
	account_balance NUMERIC(10,2) NOT NULL
);

-- Query to Create Booking Information Table.
CREATE TABLE "Booking_Information"
(
	booking_id SERIAL PRIMARY KEY,
	booking_type VARCHAR(50) NOT NULL,
	date_of_booking TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
	booking_status booking_status_enum NOT NULL,
	total_price NUMERIC(10,2) NOT NULL,
    oustanding_balance NUMERIC(10,2)
);

-- Query to Create Payment Information Table.
CREATE TABLE "Payment_Information"
(
	payment_id SERIAL PRIMARY KEY,
	booking_id INT NOT NULL,
	payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    amount_paid NUMERIC(10,2) NOT NULL,
	payment_method payment_method_enum NOT NULL,
	FOREIGN KEY (booking_id) REFERENCES "Booking_Information"(booking_id)
);

-- Enum Creation for Booking Information Table and Payment Information Table.
CREATE TYPE booking_status_enum AS ENUM ('Cancelled', 'Confirmed', 'Pending');
CREATE TYPE payment_method_enum AS ENUM ('Credit Card', 'PayPal', 'Bank Transfer');

-- Addition of Customers to Database.
INSERT INTO "Customer_Information"
( 
	customer_id,
	first_name, 
	last_name, 
	email_address, 
	account_balance
) 
VALUES
('1', 'Kemar', 'Christie', 'kemarchristie@example.com', 50000),
('2', 'Roberto', 'James', 'robertojames@example.com', 50000),
('3', 'Dwayne', 'Gibbs', 'dwaynegibbs@example.com', 50000),
('4', 'Tyoni', 'Davis', 'tyonidavis@example.com', 50000),
('5', 'Danielle', 'Jones', 'daniellejones@example.com', 50000),
('Benjamin', 'Robinson', 'benjaminrobinson@example.com', 50000),
('Marcus', 'Manley', 'marcusmanley@example.com', 50000),
('David', 'White', 'davidwhite@example.com', 50000);

SELECT * FROM "Customer_Information";


-- Additional Queries
-- Query to Set Timezone for Database Session.
SET TIMEZONE='America/Jamaica';

-- Query to show the timezone in use.
SHOW TIMEZONE;

-- Query for Commenting on Columns.
COMMENT ON COLUMN your_table.column_name IS 'Comment';

-- Query for commenting on tables.
COMMENT ON TABLE "your_table" IS 'Comment.';

-- This sets the sequence to match the highest customer_id you've inserted so that future auto-increments will be correct.
SELECT pg_get_serial_sequence('"Customer_Information"', 'customer_id');
SELECT setval('public.customer_customer_id_seq', (SELECT MAX(customer_id) FROM "Customer_Information"));


-- Auto-generate customer_username based on name + ID
CREATE OR REPLACE FUNCTION generate_customer_username()
RETURNS TRIGGER AS $$
BEGIN
    -- Build username: First 3 of first_name + "_" + First 3 of last_name + ID
    NEW.customer_username := 
        INITCAP(SUBSTRING(NEW.first_name, 1, 3)) || '_' ||
        INITCAP(SUBSTRING(NEW.last_name, 1, 3)) || NEW.customer_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--

CREATE TRIGGER trg_generate_customer_username
BEFORE INSERT ON "Customer_Information"
FOR EACH ROW
EXECUTE FUNCTION generate_customer_username();


-- Update the balance to the outstanding balance after the calculation is done.
CREATE OR REPLACE FUNCTION update_outstanding_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate the outstanding balance: total_price - amount_paid
    UPDATE "Booking_Information"
    SET balance = total_price - NEW.amount_paid
    WHERE booking_id = NEW.booking_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--

CREATE TRIGGER trg_update_oustanding_balance
AFTER INSERT ON "Payment_Information"
FOR EACH ROW
EXECUTE FUNCTION update_outstanding_balance();


-- Query to Edit Columns datatypes etc.
ALTER TABLE name_of_table
ALTER COLUMN name_column DROP NOT NULL;

-- Query to Delete Data from the table based on a column.
DELETE FROM name_of_table
WHERE name_of_field = "value";

-- Query to Delete all Data from a table.
DELETE FROM name_of_table;

-- Query to Rename a table.
ALTER TABLE name_of_table
RENAME TO new_table_name;

-- Query to Rename a column.
ALTER TABLE name_of_table
RENAME COLUMN old_column_name TO new_column_name;

-- Query to Delete a Column.
ALTER TABLE name_of_table
DROP COLUMN name_of_column;

-- Query to Delete a Table.
DROP TABLE name_of_table;

-- Query to Delete Trigger.
DROP TRIGGER name_of_trigger ON name_of_table;

-- Query to Delete Function.
DROP FUNCTION name_of_function();
SELECT 'CREATE DATABASE replacedbname' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedbname')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replacerepluser') THEN
        CREATE USER replacerepluser WITH REPLICATION ENCRYPTED PASSWORD 'replacereplpassword'; 
    END IF; 
END $$;

ALTER USER replacepostgresuser WITH PASSWORD 'replacepostgrespassword';

\c replacedbname;

CREATE TABLE IF NOT EXISTS email_table (id SERIAL PRIMARY KEY, email VARCHAR(255) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_table (id SERIAL PRIMARY KEY, phone_number VARCHAR(100) NOT NULL);

INSERT INTO email_table (email) VALUES('mrrim218@yandex.ru'),('z@narimanz.ru');
INSERT INTO phone_table (phone_number) VALUES ('8 (987) 136-17-77'), ('8 (123) 456-77-99');
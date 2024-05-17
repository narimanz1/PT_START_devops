CREATE USER ${DB_REPL_USER} REPLICATION LOGIN PASSWORD '${DB_REPL_PASSWORD}';

CREATE DATABASE ${DB_DATABASE};

\c ${DB_DATABASE};


CREATE TABLE  IF NOT EXISTS email_table (id SERIAL PRIMARY KEY, email VARCHAR(255) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_table (id SERIAL PRIMARY KEY, phone_number VARCHAR(100) NOT NULL);

INSERT INTO email_table (email) VALUES('mrrim218@yandex.ru'),('z@narimanz.ru');
INSERT INTO phone_table (phone_number) VALUES ('8 (987) 136-17-77'), ('8 (123) 456-77-99');

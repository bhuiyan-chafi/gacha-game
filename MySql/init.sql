CREATE DATABASE IF NOT EXISTS gacha_auth;
CREATE DATABASE IF NOT EXISTS gacha_user;
CREATE DATABASE IF NOT EXISTS gacha_records;
CREATE USER IF NOT EXISTS 'myuser'@'%' IDENTIFIED BY 'mypassword';
-- Grant full privileges on all current and future databases
GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'%' WITH GRANT OPTION;

-- Apply the changes
FLUSH PRIVILEGES;
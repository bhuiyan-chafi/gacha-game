CREATE DATABASE IF NOT EXISTS gacha_auth;
CREATE DATABASE IF NOT EXISTS gacha_user;
CREATE DATABASE IF NOT EXISTS gacha_records;
CREATE USER IF NOT EXISTS 'myuser'@'%' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON gacha_auth.* TO 'myuser'@'%';
GRANT ALL PRIVILEGES ON gacha_user.* TO 'myuser'@'%';
GRANT ALL PRIVILEGES ON gacha_records.* TO 'myuser'@'%';
FLUSH PRIVILEGES;
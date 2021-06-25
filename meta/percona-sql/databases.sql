-- Создание базы данных для приложения --
CREATE DATABASE appdb;
USE appdb;


CREATE TABLE `test_users` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(16) DEFAULT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(64) NOT NULL,
    `access` smallint DEFAULT NULL,
    `active` smallint DEFAULT NULL,
    `start_active_time` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`),
    UNIQUE KEY `ix_test_users_username` (`username`)
);

CREATE USER 'test_qa'@'%' IDENTIFIED BY 'qa_test';
GRANT ALL PRIVILEGES ON appdb.* TO 'test_qa'@'%';
FLUSH PRIVILEGES;

-- Создание базы данных для Mock VK --
CREATE DATABASE vkmock;
USE vkmock;


CREATE TABLE `vk_ids` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(16) NOT NULL,
    `vk_id` int NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    UNIQUE KEY `vk_id` (`vk_id`)
);

CREATE USER 'bot_mock'@'%' IDENTIFIED BY 'mock_access';
GRANT ALL PRIVILEGES ON vkmock.* TO 'bot_mock'@'%';
FLUSH PRIVILEGES;
-- 当数据库容器首次启动时，此脚本会自动执行。

-- 创建一个新的数据库，并指定字符集和排序规则，以良好支持中文
CREATE DATABASE IF NOT EXISTS `${DB_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建一个专用的管理员用户，并授予其对新数据库的所有权限
-- 注意：这里的密码将由 docker-compose 通过环境变量注入
CREATE USER IF NOT EXISTS '`${DB_USER}`'@'%' IDENTIFIED BY '`${DB_PASSWORD}`';
GRANT ALL PRIVILEGES ON `${DB_DATABASE}`.* TO '`${DB_USER}`'@'%';

-- 刷新权限，使更改生效
FLUSH PRIVILEGES;

-- 切换到新创建的数据库
USE `${DB_DATABASE}`;

-- 创建一个示例的用户表，用于测试和开发
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入一个初始管理员用户，方便开发和测试
-- 在实际生产中，密码应该是经过哈希处理的
INSERT INTO `users` (`username`, `email`, `password_hash`) VALUES
('admin', 'admin@example.com', 'default_password_hash');

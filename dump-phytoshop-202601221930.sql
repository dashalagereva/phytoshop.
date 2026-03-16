-- MySQL dump 10.13  Distrib 8.4.7, for Win64 (x86_64)
--
-- Host: localhost    Database: phytoshop
-- ------------------------------------------------------
-- Server version	8.4.7

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `added_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_cart_user_product` (`user_id`,`product_id`),
  KEY `fk_cart_product` (`product_id`),
  CONSTRAINT `fk_cart_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (1,2,4,1,'2025-12-03 20:22:36'),(2,3,2,2,'2025-12-03 20:22:36'),(3,4,9,1,'2025-12-03 20:22:36');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Фиточаи','Травяные чаи и сборы для ежедневного употребления'),(2,'Настойки и экстракты','Концентрированные жидкие фитопрепараты'),(3,'Масла','Эфирные и пищевые масла'),(4,'Сборы для иммунитета','Комплексные фитосборы для поддержки иммунитета'),(5,'Косметические средства','Натуральные фитосредства для ухода за телом и волосами');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_items_order` (`order_id`),
  KEY `fk_items_product` (`product_id`),
  CONSTRAINT `fk_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,2,250.00),(2,1,3,1,290.00),(3,2,6,1,350.00),(4,2,8,1,450.00);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `order_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('new','processing','completed','cancelled') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'new',
  `total_amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `fk_orders_user` (`user_id`),
  CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,2,'2025-12-03 20:22:36','completed',840.00),(2,3,'2025-12-03 20:22:36','processing',700.00);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `name` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `price` decimal(10,2) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `image_url` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `rating_avg` decimal(3,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_products_category` (`category_id`),
  CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,1,'Фиточай «Лесная гармония»','Сбор из листьев брусники, черники и шиповника',250.00,50,1,'/static/uploads/images.jpg',4.67),(2,1,'Фиточай «Вечернее спокойствие»','Мята, мелисса и пустырник для мягкого расслабления перед сном',270.00,40,1,'/static/uploads/1.webp',4.50),(3,1,'Фиточай «Имбирный заряд»','Имбирь, лимонная трава и шиповник для бодрого утра',290.00,35,1,'/static/uploads/orig_1.webp',4.50),(4,4,'Сбор «Иммунный щит»','Эхинацея, шиповник, чабрец и зверобой для поддержки иммунитета',320.00,30,1,'/static/uploads/moychay_116787.jpg',4.50),(5,4,'Сбор «Витаминный коктейль»','Смесь ягодных листьев и плодов с высоким содержанием витамина C',310.00,25,1,'/static/uploads/orig.webp',5.00),(6,2,'Настойка эхинацеи','Классическое фитосредство для сезонной поддержки организма',350.00,40,1,'/static/uploads/31c5dfb7b8190bfd0c984fe47282fd6c.jpg',3.50),(7,2,'Настойка женьшеня','Тонизирующее средство на основе корня женьшеня',380.00,20,1,'/static/uploads/23001_f8cce086.jpg',NULL),(8,3,'Масло расторопши','Холодный отжим семян расторопши для поддержки печени',450.00,25,1,'/static/uploads/original_23bf75e8-fdc0-4f1d-9ce3-e766b1f73306.jpeg',5.00),(9,3,'Масло облепиховое','Натуральное облепиховое масло для внутреннего и наружного применения',420.00,30,1,'/static/uploads/original_cd0dbb88-61d0-4a84-84b6-ea54b3941d9c.jpeg',5.00),(10,5,'Бальзам для волос с крапивой','Фитобальзам для укрепления и придания блеска волосам',330.00,15,1,'/static/uploads/1280_1280compress_7735eb8b1fa94cb5339582714c1dcf1f.webp',4.00);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `rating` tinyint NOT NULL,
  `comment` text COLLATE utf8mb4_general_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_reviews_user` (`user_id`),
  KEY `fk_reviews_product` (`product_id`),
  CONSTRAINT `fk_reviews_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reviews_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_rating_range` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,2,1,5,'Очень мягкий вкус, пью каждый вечер, отлично расслабляет.','2025-12-03 20:22:36'),(2,3,1,4,'Нравится вкус, но хотелось бы побольше аромата ягод.','2025-12-03 20:22:36'),(3,4,1,5,'Лучший травяной чай, который пробовала за последнее время.','2025-12-03 20:22:36'),(4,2,2,4,'Помогает легче заснуть, вкус приятный.','2025-12-03 20:22:36'),(5,5,2,5,'Пью курсом, стало проще расслабляться вечером.','2025-12-03 20:22:36'),(6,3,3,5,'Отличный бодрящий вкус, идеален для утра.','2025-12-03 20:22:36'),(7,6,3,4,'Хороший чай, но имбиря для меня чуть многовато.','2025-12-03 20:22:36'),(8,4,4,5,'Пью осенью и зимой, болею реже, очень довольна.','2025-12-03 20:22:36'),(9,6,4,4,'Вкус специфический, но эффект почувствовала.','2025-12-03 20:22:36'),(10,2,5,5,'Очень приятный ягодный вкус, ребёнку тоже понравился.','2025-12-03 20:22:36'),(11,3,6,4,'Классическая вещь для иммунитета, беру не первый раз.','2025-12-03 20:22:36'),(12,5,6,3,'По эффекту всё ок, но вкус довольно горький.','2025-12-03 20:22:36'),(13,4,8,5,'Покупаю для поддержки печени, качественное масло.','2025-12-03 20:22:36'),(14,6,9,5,'Помогло при проблемах с желудком, очень довольна.','2025-12-03 20:22:36'),(15,2,10,4,'Волосы стали более живыми, но запах на любителя.','2025-12-03 20:22:36');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_reviews_after_insert` AFTER INSERT ON `reviews` FOR EACH ROW BEGIN
    DECLARE v_avg_rating DECIMAL(3,2);

    SELECT AVG(rating)
    INTO v_avg_rating
    FROM reviews
    WHERE product_id = NEW.product_id;

    UPDATE products
    SET rating_avg = v_avg_rating
    WHERE id = NEW.product_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `users`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_general_ci,
  `city` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `role` enum('admin','customer') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'customer',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Администратор Сайта','admin@phytoshop.local','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-000-00-00','г. Красноярск, ул. Центральная, д. 1','Красноярск','admin','2025-12-03 20:22:36'),(2,'Иванова Мария Петровна','maria@example.com','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-111-22-33','г. Красноярск, ул. Лесная, д. 10, кв. 5','Красноярск','customer','2025-12-03 20:22:36'),(3,'Сидоров Алексей Иванович','alex@example.com','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-222-33-44','г. Москва, пр-т Мира, д. 25, кв. 12','Москва','customer','2025-12-03 20:22:36'),(4,'Кузнецова Ольга Сергеевна','olga@example.com','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-333-44-55','г. Новосибирск, ул. Берёзовая, д. 7, кв. 3','Новосибирск','customer','2025-12-03 20:22:36'),(5,'Петров Дмитрий Олегович','dmitry@example.com','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-444-55-66','г. Екатеринбург, ул. Урожайная, д. 15','Екатеринбург','customer','2025-12-03 20:22:36'),(6,'Смирнова Елена Викторовна','elena@example.com','scrypt:32768:8:1$9DdkvhtpJg4rx9rz$128d20bef06385f75f80889c55d8a3979c7f5e026dfe8d48cb2a8e1945f5fa6cd675d19844cf4d220abad872503bc04da4b1dbeece1a9359e1164144e61dee41','+7-900-555-66-77','г. Санкт-Петербург, ул. Невская, д. 3','Санкт-Петербург','customer','2025-12-03 20:22:36');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'phytoshop'
--

--
-- Dumping routines for database 'phytoshop'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-22 19:30:40

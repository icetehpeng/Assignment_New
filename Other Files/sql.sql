-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: login_system
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_log`
--

CREATE DATABASE IF NOT EXISTS assignment_new;
USE assignment_new;

DROP TABLE IF EXISTS `activity_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `activity` varchar(255) DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_log`
--

LOCK TABLES `activity_log` WRITE;
/*!40000 ALTER TABLE `activity_log` DISABLE KEYS */;
INSERT INTO `activity_log` VALUES (1,'Ethen','Logged in','2026-01-23 07:51:59'),(2,'Ethen','Camera connected','2026-01-23 07:52:20'),(3,'Ethen','Started recording','2026-01-23 07:52:37'),(4,'Ethen','Stopped recording','2026-01-23 07:52:46'),(5,'Ethen','Paused stream','2026-01-23 07:52:49'),(6,'Ethen','Updated camera settings','2026-01-23 07:52:55'),(7,'Ethen','Camera set to Motion Detection','2026-01-23 07:53:02'),(8,'Ethen','Camera set to Online','2026-01-23 07:53:08'),(9,'Ethen','Logged out','2026-01-23 07:53:49'),(10,'Jack','Registered account','2026-01-23 07:53:57'),(11,'Jack','Logged in','2026-01-23 07:53:59'),(12,'Jack','Started recording','2026-01-23 07:54:08'),(13,'Jack','Camera set to Offline','2026-01-23 07:54:46'),(14,'Jack','Logged out','2026-01-23 07:55:12'),(15,'Ethenn','Registered account','2026-01-23 07:55:28'),(16,'Ethenn','Logged in','2026-01-23 07:55:29'),(17,'Ethenn','Camera connected','2026-01-23 07:55:54'),(18,'Ethenn','Paused stream','2026-01-23 07:58:04'),(19,'Ethenn','Camera set to Offline','2026-01-23 07:58:50'),(20,'Ethenn','Camera set to Online','2026-01-23 07:59:02'),(21,'Ethenn','Camera set to Offline','2026-01-23 07:59:05'),(22,'Ethenn','Logged out','2026-01-23 07:59:07'),(23,'Ethen','Logged in','2026-01-23 07:59:13'),(24,'Ethen','Camera set to Recording','2026-01-23 07:59:18'),(25,'Ethen','Logged out','2026-01-23 07:59:21'),(26,'Jack','Logged in','2026-01-23 07:59:29'),(27,'Ethen','Logged in','2026-01-23 08:00:52'),(28,'Ethen','Camera set to Online','2026-01-23 08:01:01'),(29,'Ethen','Started recording','2026-01-23 08:01:11'),(30,'Ethen','Logged out','2026-01-23 08:04:03'),(31,'Ethen','Logged in','2026-01-23 08:05:58'),(32,'Ethen','Updated camera settings','2026-01-23 08:06:12'),(33,'Ethen','Updated camera settings','2026-01-23 08:06:29'),(34,'Ethen','Updated camera settings','2026-01-23 08:06:33'),(35,'Ethen','Logged in','2026-01-23 08:07:22'),(36,'Ethen','Started webcam','2026-01-23 08:07:45'),(37,'Ethen','Updated camera settings','2026-01-23 08:08:12'),(38,'Ethen','Stopped webcam','2026-01-23 08:08:25'),(39,'Ethen','Started webcam','2026-01-23 08:08:36'),(40,'Ethen','Stopped webcam','2026-01-23 08:10:33'),(41,'Ethen','Changed camera mode to Offline','2026-01-23 08:13:12'),(42,'Ethen','Changed camera mode to Online','2026-01-23 08:13:14'),(43,'Ethen','Changed camera mode to Offline','2026-01-23 08:25:02'),(44,'Ethen','Changed camera mode to Online','2026-01-23 08:25:06'),(45,'Ethen','Stopped webcam','2026-01-23 08:25:10'),(46,'Ethen','Stopped webcam','2026-01-23 08:25:20'),(47,'Ethen','Logged into CCTV monitoring','2026-01-23 08:26:05');
/*!40000 ALTER TABLE `activity_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reminders`
--

DROP TABLE IF EXISTS `reminders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reminders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `message` text,
  `trigger_time` datetime DEFAULT NULL,
  `repeat_type` varchar(20) DEFAULT NULL,
  `audio_data` longblob,
  `status` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reminders`
--

LOCK TABLES `reminders` WRITE;
/*!40000 ALTER TABLE `reminders` DISABLE KEYS */;
/*!40000 ALTER TABLE `reminders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_profiles`
--

DROP TABLE IF EXISTS `user_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `profile_data` text,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profiles`
--

LOCK TABLES `user_profiles` WRITE;
/*!40000 ALTER TABLE `user_profiles` DISABLE KEYS */;
INSERT INTO `user_profiles` VALUES (1,'Ethen','{\"username\": \"Ethen\", \"camera_status\": \"Online\", \"last_seen\": \"Never\", \"camera_settings\": {\"camera_name\": \"Living Room Camera\", \"resolution\": \"720p\", \"fps\": 60, \"motion_sensitivity\": 100, \"recording_enabled\": false}}','2026-01-23 08:08:12');
/*!40000 ALTER TABLE `user_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'testuser','testpassword','2026-01-23 07:28:05'),(2,'Ethen','Liew','2026-01-23 07:35:38'),(3,'Ethen ','Liew','2026-01-23 07:36:37'),(5,'Jack','Tan','2026-01-23 07:53:57'),(7,'Ethenn','LIEWWWW','2026-01-23 07:55:28'),(8,'OwenYap','OwenYap','2026-01-30 06:14:47');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-30 14:25:05

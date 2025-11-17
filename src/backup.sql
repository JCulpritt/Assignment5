-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: assignment4
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` char(36) NOT NULL,
  `content` text,
  `user_id` char(36) DEFAULT NULL,
  `feature_request_id` char(36) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `feature_request_id` (`feature_request_id`),
  KEY `comments_ibfk_1` (`user_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`feature_request_id`) REFERENCES `feature_requests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES ('c1','Great idea!','u2','fr1','2025-11-14 18:14:27'),('c10','Helpful for new users.','u1','fr9','2025-11-14 18:14:27'),('c2','We need this badly.','u3','fr1','2025-11-14 18:14:27'),('c3','I support this feature.','u4','fr2','2025-11-14 18:14:27'),('c4','Please add this soon.','u5','fr3','2025-11-14 18:14:27'),('c5','Very useful.','u6','fr4','2025-11-14 18:14:27'),('c6','Makes sense.','u7','fr5','2025-11-14 18:14:27'),('c7','Our team needs this.','u8','fr6','2025-11-14 18:14:27'),('c8','Amazing suggestion.','u9','fr7','2025-11-14 18:14:27'),('c9','Hope this gets built.','u10','fr8','2025-11-14 18:14:27');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feature_requests`
--

DROP TABLE IF EXISTS `feature_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feature_requests` (
  `id` char(36) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text,
  `user_id` char(36) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `feature_requests_ibfk_1` (`user_id`),
  CONSTRAINT `feature_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature_requests`
--

LOCK TABLES `feature_requests` WRITE;
/*!40000 ALTER TABLE `feature_requests` DISABLE KEYS */;
INSERT INTO `feature_requests` VALUES ('fr1','Dark Mode','Add dark theme for UI.','u1','2025-11-14 18:14:27'),('fr10','Chat Support','In-app customer support.','u10','2025-11-14 18:14:27'),('fr2','Mobile App','Create iOS/Android app.','u2','2025-11-14 18:14:27'),('fr3','Export to PDF','Allow report exporting.','u3','2025-11-14 18:14:27'),('fr4','Two-Factor Auth','Enhance account security.','u4','2025-11-14 18:14:27'),('fr5','Keyboard Shortcuts','Add shortcuts for actions.','u5','2025-11-14 18:14:27'),('fr6','Bulk Upload','Upload multiple files.','u6','2025-11-14 18:14:27'),('fr7','Advanced Search','Filters + fuzzy search.','u7','2025-11-14 18:14:27'),('fr8','Offline Mode','Use app without internet.','u8','2025-11-14 18:14:27'),('fr9','Analytics Dashboard','Graphs + stats.','u9','2025-11-14 18:14:27');
/*!40000 ALTER TABLE `feature_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` char(36) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('u1','/Yy/EDeZKgB7Tj+Snp22Hd3sSIoVtYWqnwWlhocH/7ondXe9OQe2lvrK5aZDXBVB','hash_pw1','SFjJQdl8XTEMu6HLukA4vJLnsL+d1fjJzAmbxxyx8XM=','2025-11-14 18:14:27'),('u10','Ps2MBlAfd0tTJTC1gg4Bm1LZYyG8oGOOeXFk8dKwsOURQ0dKjpAgfJ7uE73tOAOW','hash_pw10','a89Kw8uhKf0ge+8NC9yfzWm8TNuDVn+bA2M67e1dhDc=','2025-11-14 18:14:27'),('u11','zkSOq2IyM3wwfkzLqjnYrr7gsof0ay5u4RGHnFb5pwFOUE7q7aB/ofULWnayCtS6','password1','8fQeoHU8iIVQauQgkEGqjMVg/jgZHxwJhjnxYZGzx7I=','2025-11-17 17:34:17'),('u12','EO35MX9nGLG/L2R0UsbAYCrZ0D27bGUfDtoJpDztYeLxEQN+LTEJ21ktEt84maHG','$2b$12$OVBe6eFFpkUCknqc/DRq9eyUngtZp3aPzFxBRuiS0CwBh2hLUWUIy','sJS9ZS9p2Cx/w85u02otfeOoeR0zvCwFHgk2eGhPxAA=','2025-11-17 18:56:19'),('u2','TxBKnFOaEhi4uk9YNzlB52rnJvvIGU2cWzyZkin7+A8=','hash_pw2','7vcxQkxL3spibkiIaKj1P71xXNNUXOwmmDt2YVbcZMo=','2025-11-14 18:14:27'),('u3','Dkb6VyK0o7BsTeJ6LZPNtV0gExB8MbY0YM2kie23H7TUkZZJMHmFpa8sX4cw7rsB','hash_pw3','DTsAr/J/ULWfDoqL5gGqoO4V2M9ESxoYjNInaL+jxzY=','2025-11-14 18:14:27'),('u4','C/ncmxSWqvdbYXLP04CT0OQhWyr8PllwV0Kk6yptOfd3Bbr9haQndGO7Yd5RWB3n','hash_pw4','1mleywIi7SDbxlP4wQdxqJ/wPBHWGFAUHMc5cXQ6CHM=','2025-11-14 18:14:27'),('u5','QS179iPMFAO/VBtm6CZi1AbvbP3rBVEft0gXywFECI6Eu0vuvzPTZPz0C40OldNb','hash_pw5','843+uGRiABRFIgzmSxDYZIQM3s2sTwEzM4LEzGpDvHo=','2025-11-14 18:14:27'),('u6','lSJzk2+3YlODikiP5XHWBczd5Qlm+QvS5+wapxV7cDmg5Xq5AehF5G/LN9ODeubm','hash_pw6','LLnZ8H+X+iJtPkA6g5dKLGO7iqN5wBMdSKDgfLDTWZA=','2025-11-14 18:14:27'),('u7','kg9aFqiy7o3aWE7Dd9ye7CngFSTpe95J+NI7y128RBmdF5r6ZdH31QDijbb2MngK','hash_pw7','WDhnapbIc9BBz4/pfsioxeLY6Mawj3TIlzMN2pCfrms=','2025-11-14 18:14:27'),('u8','/MMqJt+smhfMZ7ATPUOyjCPer5uIi+93w/+hqN+c5l6MO/VsyZnpVAVwRANt5uIp','hash_pw8','1jdhpPCSkhDaoSeWLoftvos9ljFwt1gU9s586PPE708=','2025-11-14 18:14:27'),('u9','GLkV56jtyPpU9QTMUDI1I8jXFi/Vzptl1g5DBX1SDlQ=','hash_pw9','PKwiLe/b+iH10a91M1PSAMy4f3PWiXpxpU/56KQP4jg=','2025-11-14 18:14:27');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `votes`
--

DROP TABLE IF EXISTS `votes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `votes` (
  `user_id` char(36) NOT NULL,
  `feature_request_id` char(36) NOT NULL,
  `upvoted` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_id`,`feature_request_id`),
  KEY `feature_request_id` (`feature_request_id`),
  CONSTRAINT `votes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `votes_ibfk_2` FOREIGN KEY (`feature_request_id`) REFERENCES `feature_requests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `votes`
--

LOCK TABLES `votes` WRITE;
/*!40000 ALTER TABLE `votes` DISABLE KEYS */;
INSERT INTO `votes` VALUES ('u1','fr1',1),('u10','fr9',1),('u2','fr1',1),('u3','fr2',1),('u4','fr3',1),('u5','fr4',1),('u6','fr5',1),('u7','fr6',1),('u8','fr7',1),('u9','fr8',1);
/*!40000 ALTER TABLE `votes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-17 13:57:00

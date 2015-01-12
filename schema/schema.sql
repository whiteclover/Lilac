SET @saved_cs_client = @@character_set_client;
SET character_set_client = utf8;

DROP TABLE IF EXISTS `cron`;
CREATE TABLE `cron` (
  `cron_id` INT(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'cron id',
  `task_id` VARCHAR(64) DEFAULT NULL COMMENT 'the task id for task claiming',
  `name` VARCHAR(124) NOT NULL COMMENT 'the unique task name for human',
  `action` VARCHAR(124) NOT NULL COMMENT 'the action name registed in app',
  `data` TEXT DEFAULT NULL COMMENT 'The custum  json data arguments for app action',
  `event`  VARCHAR(64) NOT NULL COMMENT 'The event pattern',
  `next_run` DATETIME DEFAULT NULL COMMENT 'the task next run datatime',
  `last_run` DATETIME DEFAULT NULL COMMENT 'The task last run datatime',
  `run_times` INT(11) unsigned NOT NULL COMMENT 'the total run times of the current task',
  `attempts` TINYINT DEFAULT 0 NOT NULL COMMENT 'The attempts times when task run failed',
  `status` TINYINT unsigned DEFAULT 0 COMMENT 'the status of task (running, stop...)',
  `created` DATETIME NOT NULL COMMENT 'The DATETIME when the entry was created.',
  `last_five_logs` TEXT NOT NULL COMMENT 'the last five logs of the current task',
  
  PRIMARY KEY `cron_id` (`cron_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB CHARSET=utf8;



DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `uid` MEDIUMINT(8) unsigned NOT NULL AUTO_INCREMENT COMMENT 'the unique user id',
  `username` varchar(140) NOT NULL COMMENT 'the unique user name',
  `real_name` varchar(140) NOT NULL COMMENT 'the nick name or real name',
  `email` VARCHAR(140) NOT NULL COMMENT 'the email for the user',
  `password` CHAR(56) NOT NULL COMMENT 'The sha224 encypted password',
  `status` enum('actived', 'banned') NOT NULL COMMENT 'The status of the current user',
  `role` enum('root', 'administrator','user') NOT NULL COMMENT 'The role of the current user',
  `created` DATETIME NOT NULL  COMMENT 'The DATETIME when the user was created.',

  PRIMARY KEY (`uid`),
  UNIQUE KEY (`email`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `users`(uid, username, real_name, email, password, status, role, created) VALUES(1, 'lilac', 'Lilac',
'lilac@test.com', 'ea2020445e82529b9f030c346739395aea1dca55e275e5edb0942ce3, 'actived', 'root', now());

SET @@character_set_client = @saved_cs_client;

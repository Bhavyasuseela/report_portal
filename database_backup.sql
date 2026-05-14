SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+05:30";

-- =============================================================================
-- TABLE 1: accounts_user
-- Stores all portal users across all roles.
-- Admin is created via createsuperuser (is_superuser=1, is_staff=1, role='admin')
-- =============================================================================


CREATE TABLE `accounts_user` (
  `id`                      INT(11) NOT NULL AUTO_INCREMENT,
  `password`                VARCHAR(128) NOT NULL,
  `last_login`              DATETIME(6) DEFAULT NULL,
  `is_superuser`            TINYINT(1) NOT NULL DEFAULT 0,
  `email`                   VARCHAR(254) NOT NULL UNIQUE,
  `full_name`               VARCHAR(200) NOT NULL DEFAULT '',
  `role`                    VARCHAR(20) NOT NULL DEFAULT 'author',
  `extra_roles`             VARCHAR(200) NOT NULL DEFAULT '',
  `is_active`               TINYINT(1) NOT NULL DEFAULT 1,
  `is_staff`                TINYINT(1) NOT NULL DEFAULT 0,
  `date_joined`             DATETIME(6) NOT NULL,
  `otp`                     VARCHAR(6) DEFAULT NULL,
  `otp_created_at`          DATETIME(6) DEFAULT NULL,
  `must_reset_password`     TINYINT(1) NOT NULL DEFAULT 1,
  `password_reset_token`    VARCHAR(64) DEFAULT NULL,
  `password_reset_expires`  DATETIME(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- INITIAL USER DATA
-- Default password hash for 'NCMRWF@2024':
--   pbkdf2_sha256$870000$... (run: python manage.py seed_users to populate properly)
-- NOTE: Passwords below are placeholder hashes. Run `python manage.py seed_users`
--       after restoring to properly create all users with correct hashed passwords.
-- =============================================================================

INSERT INTO `accounts_user`
  (`id`, `password`, `last_login`, `is_superuser`, `email`, `full_name`, `role`,
   `extra_roles`, `is_active`, `is_staff`, `date_joined`, `must_reset_password`)
VALUES

-- ── ADMIN (Superuser) ────────────────────────────────────────────────────────
-- Created via createsuperuser OR seed_users command
-- Email: nirajan.kondapalli@ncmrwf.gov.in  | Role: admin | is_superuser=1
(1,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 1,
 'nirajan.kondapalli@ncmrwf.gov.in', 'Nirajan Kondapalli (Admin)',
 'admin', '', 1, 1, NOW(), 0),

-- ── CONVENERS ────────────────────────────────────────────────────────────────
-- Niranjan: convener + reviewer + author access. CANNOT assign to himself.
(2,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'niranjan@ncmrwf.gov.in', 'Dr. Kondapalli Niranjan Kumar',
 'convener', 'reviewer,author', 1, 0, NOW(), 1),

-- Indrani (Chairman): convener + reviewer + author access. CANNOT assign to herself.
(3,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'indrani@ncmrwf.gov.in', 'Dr. S. Indira Rani',
 'convener', 'reviewer,author', 1, 0, NOW(), 1),

-- ── HEAD / DIRECTOR ──────────────────────────────────────────────────────────
(4,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'director@ncmrwf.gov.in', 'Director, NCMRWF',
 'head', '', 1, 0, NOW(), 1),

-- ── LIBRARIAN ────────────────────────────────────────────────────────────────
(5,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'library@ncmrwf.gov.in', 'NCMRWF Librarian',
 'librarian', '', 1, 0, NOW(), 1),

-- ── REVIEWERS (Scientists) — also have author access via extra_roles ──────────
(6,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'vsprasad@ncmrwf.gov.in', 'Dr. V.S. Prasad (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(7,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'john@ncmrwf.gov.in', 'Dr. John P. George (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(8,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'preveen@ncmrwf.gov.in', 'Dr. Preveen Kumar (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(9,  'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'saji@ncmrwf.gov.in', 'Dr. Saji Mohandas (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(10, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ashrit@ncmrwf.gov.in', 'Dr. Raghavendra Ashrit (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(11, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ashishroutray@ncmrwf.gov.in', 'Dr. Ashish Routray (Scientist - G)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(12, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'indira@ncmrwf.gov.in', 'Dr. S.Indira Rani (Scientist - F)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(13, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'jkumar@ncmrwf.gov.in', 'Dr. A.Jayakumar (Scientist - F)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(14, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'debasis@ncmrwf.gov.in', 'Dr. D.K.Mahapatra (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(15, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'imranali@ncmrwf.gov.in', 'Dr. Imranali M. Momin (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(16, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'anurose@ncmrwf.gov.in', 'Dr. Anurose T.J. (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(17, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'gibies@ncmrwf.gov.in', 'Dr. Gibies George (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(18, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'sumit@ncmrwf.gov.in', 'Dr. Sumit Kumar (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(19, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'amamgain@ncmrwf.gov.in', 'Dr. Ashu Mamgain (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(20, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'akhilesh@ncmrwf.gov.in', 'Dr. Akhilesh Kumar Mishra (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(21, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'surya@ncmrwf.gov.in', 'Dr. Suryakanti Dutta (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(22, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'mohant@ncmrwf.gov.in', 'Dr. Mohana. S. Thota (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(23, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'hashmi@ncmrwf.gov.in', 'Dr. Hashmi Fatima (Scientist - E)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(24, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ankur@ncmrwf.gov.in', 'Mr. Ankur Gupta (Scientist - D)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(25, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'djyoti@ncmrwf.gov.in', 'Dr. Devajyoti Dutta (Scientist - D)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(26, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'srinivas@ncmrwf.gov.in', 'Dr. Srinivas Desamsetti (Scientist - D)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(27, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'hari@ncmrwf.gov.in', 'Dr. B.R.R Hari Prasad Kottu (Scientist - D)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(28, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'upal@ncmrwf.gov.in', 'Dr. Upal Saha (Scientist - C)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(29, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ramarao@ncmrwf.gov.in', 'Dr. V.S Ramarao Mandavilli (Scientist - C)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(30, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'devanil@ncmrwf.gov.in', 'Dr. Devanil Choudhury (Scientist - C)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(31, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'durgesh@ncmrwf.gov.in', 'Dr. Durgesh Nandan Piyush (Scientist - C)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(32, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'abhishek.lodh@ncmrwf.gov.in', 'Dr. Abhishek Lodh (Scientist - C)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(33, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'mansi@ncmrwf.gov.in', 'Dr. Mansi Bhowmick (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(34, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'shweta@ncmrwf.gov.in', 'Dr. Shweta Bhati (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(35, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'dinesh@ncmrwf.gov.in', 'Dr. Dineshkumar Kevalji Sankhala (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(36, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'greeshma@ncmrwf.gov.in', 'Dr. Greeshma M Mohan (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(37, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'venkat@ncmrwf.gov.in', 'Dr. M.Venkatarami Reddy (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(38, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'harvir@ncmrwf.gov.in', 'Mr. Harvir Singh (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(39, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'sushant@ncmrwf.gov.in', 'Dr. Sushant Kumar (Project Scientist- III)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(40, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'neharajput@ncmrwf.gov.in', 'Ms. Neha Rajput Mangalsingh (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(41, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'shivalig@ncmrwf.gov.in', 'Ms. Shivali Gangwar (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(42, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'lkpandey@ncmrwf.gov.in', 'Dr. Lokesh Pandey (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(43, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'sridevi@ncmrwf.gov.in', 'Dr. Chollangi Sridevi (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(44, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'suraj@ncmrwf.gov.in', 'Mr. Suraj Ravindran (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(45, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'nishtha@ncmrwf.gov.in', 'Dr. Nishtha Agrawal (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(46, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'dsbisht@ncmrwf.gov.in', 'Dr. Deepak Singh Bisht (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(47, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'shubha@ncmrwf.gov.in', 'Dr. Shubha (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(48, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'dgnrao@ncmrwf.gov.in', 'Dr. Nagarjuna Rao D. (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(49, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'sukhwinder@ncmrwf.gov.in', 'Dr. Sukhwinder Kaur (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(50, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'keshavbs@ncmrwf.gov.in', 'Mr. Bibhuti Sharan Keshav (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(51, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ashutosh@ncmrwf.gov.in', 'Mr. Ashutosh Kumar Sinha (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(52, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'kumarjit@ncmrwf.gov.in', 'Dr. Kumarjit Saha (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(53, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'navin@ncmrwf.gov.in', 'Dr. Navin Chandra (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(54, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'asrajpoot@ncmrwf.gov.in', 'Azad Singh Rajpoot (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(55, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'abhi@ncmrwf.gov.in', 'Mr. Abhijit V. (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(56, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'gauri@ncmrwf.gov.in', 'Dr. Gauri Shanker (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(57, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'ezhilarasi.s@ncmrwf.gov.in', 'Ezhilarasi S (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(58, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'smrati.purwar@ncmrwf.gov.in', 'Smrati Purwar (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(59, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'smruti.swati@ncmrwf.gov.in', 'Smrutishree Lenka (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(60, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'j.dixit@ncmrwf.gov.in', 'Jivesh Dixit (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(61, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'donali.gogoi@ncmrwf.gov.in', 'Donali Gogoi (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(62, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'rehan.hossain@ncmrwf.gov.in', 'Rehan Hossain (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(63, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'sanjiban.roy@ncmrwf.gov.in', 'Sanjiban Roy (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(64, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'joydeb.saha@ncmrwf.gov.in', 'Joydeb Saha (Project Scientist- II)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(65, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'aman.fatima@ncmrwf.gov.in', 'Aman Fatima (Project Scientist- I)',
 'reviewer', 'author', 1, 0, NOW(), 1),
(66, 'pbkdf2_sha256$1200000$jfbgbj1qQMxsX5gKSucy46$aBaZLB/vrKYZoXwaH3t2BQLpCrrzX1PmZ1688BjfAqU=', NULL, 0,
 'amjad.ali05@ncmrwf.gov.in', 'Md Amjad Ali (Project Scientist- I)',
 'reviewer', 'author', 1, 0, NOW(), 1);

-- =============================================================================
-- TABLE 2: reports_report
-- Each submitted report and its full workflow lifecycle
-- =============================================================================

DROP TABLE IF EXISTS `reports_report`;

CREATE TABLE `reports_report` (
  `id`                          INT(11) NOT NULL AUTO_INCREMENT,
  `report_type`                 VARCHAR(30) NOT NULL,
  `title`                       VARCHAR(300) NOT NULL,
  `author_name`                 VARCHAR(200) NOT NULL,
  `contributors`                LONGTEXT NOT NULL,
  `contributor_emails`          LONGTEXT NOT NULL,
  `abstract`                    LONGTEXT NOT NULL,
  `keywords`                    VARCHAR(500) NOT NULL,
  `plagiarism_doc`              VARCHAR(100) DEFAULT NULL,
  `paper_doc`                   VARCHAR(100) NOT NULL,
  `status`                      VARCHAR(30) NOT NULL DEFAULT 'submitted',
  `submitted_at`                DATETIME(6) NOT NULL,
  `updated_at`                  DATETIME(6) NOT NULL,
  `convener_notes`              LONGTEXT NOT NULL,
  `reviewer_feedback`           LONGTEXT NOT NULL,
  `reviewer_attachment`         VARCHAR(100) DEFAULT NULL,
  `reviewed_at`                 DATETIME(6) DEFAULT NULL,
  `revision_notes`              LONGTEXT NOT NULL,
  `resubmitted_paper_doc`       VARCHAR(100) DEFAULT NULL,
  `resubmission_count`          INT(10) UNSIGNED NOT NULL DEFAULT 0,
  `last_resubmitted_at`         DATETIME(6) DEFAULT NULL,
  `sent_back_to_author_at`      DATETIME(6) DEFAULT NULL,
  `reassigned_at`               DATETIME(6) DEFAULT NULL,
  `head_notes`                  LONGTEXT NOT NULL,
  `sent_to_head_at`             DATETIME(6) DEFAULT NULL,
  `head_decision_at`            DATETIME(6) DEFAULT NULL,
  `sent_to_library_at`          DATETIME(6) DEFAULT NULL,
  `final_report_requested_at`   DATETIME(6) DEFAULT NULL,
  `final_report_doc`            VARCHAR(100) DEFAULT NULL,
  `final_report_notes`          LONGTEXT NOT NULL,
  `final_report_submitted_at`   DATETIME(6) DEFAULT NULL,
  `submission_deadline`         DATETIME(6) DEFAULT NULL,
  `reviewer_deadline`           DATETIME(6) DEFAULT NULL,
  `reminder_sent_at`            DATETIME(6) DEFAULT NULL,
  `extension_requested`         TINYINT(1) NOT NULL DEFAULT 0,
  `extension_request_reason`    LONGTEXT NOT NULL,
  `extension_requested_at`      DATETIME(6) DEFAULT NULL,
  `extension_granted`           TINYINT(1) NOT NULL DEFAULT 0,
  `extension_granted_at`        DATETIME(6) DEFAULT NULL,
  `extension_days`              INT(10) UNSIGNED NOT NULL DEFAULT 0,
  `series_title`                VARCHAR(300) NOT NULL DEFAULT '',
  `series_number`               VARCHAR(100) NOT NULL DEFAULT '',
  `description`                 LONGTEXT NOT NULL,
  `language`                    VARCHAR(50) NOT NULL DEFAULT 'English',
  `doi`                         VARCHAR(200) NOT NULL DEFAULT '',
  `doi_assigned_at`             DATETIME(6) DEFAULT NULL,
  -- Foreign keys
  `author_id`                   INT(11) NOT NULL,
  `assigned_reviewer_id`        INT(11) DEFAULT NULL,
  `assigned_by_convener_id`     INT(11) DEFAULT NULL,
  `doi_assigned_by_id`          INT(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `reports_report_author_id` (`author_id`),
  KEY `reports_report_assigned_reviewer_id` (`assigned_reviewer_id`),
  KEY `reports_report_assigned_by_convener_id` (`assigned_by_convener_id`),
  KEY `reports_report_doi_assigned_by_id` (`doi_assigned_by_id`),
  CONSTRAINT `reports_report_author_fk`
    FOREIGN KEY (`author_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reports_report_reviewer_fk`
    FOREIGN KEY (`assigned_reviewer_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL,
  CONSTRAINT `reports_report_convener_fk`
    FOREIGN KEY (`assigned_by_convener_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL,
  CONSTRAINT `reports_report_doi_fk`
    FOREIGN KEY (`doi_assigned_by_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- No report rows inserted — reports are created at runtime by authors.

-- =============================================================================
-- TABLE 3: reports_supportrequest
-- Support/query requests submitted by authors to conveners
-- =============================================================================

DROP TABLE IF EXISTS `reports_supportrequest`;

CREATE TABLE `reports_supportrequest` (
  `id`                INT(11) NOT NULL AUTO_INCREMENT,
  `request_type`      VARCHAR(30) NOT NULL DEFAULT 'general',
  `subject`           VARCHAR(300) NOT NULL,
  `message`           LONGTEXT NOT NULL,
  `status`            VARCHAR(20) NOT NULL DEFAULT 'open',
  `created_at`        DATETIME(6) NOT NULL,
  `convener_response` LONGTEXT NOT NULL,
  `responded_at`      DATETIME(6) DEFAULT NULL,
  `report_id`         INT(11) DEFAULT NULL,
  `author_id`         INT(11) NOT NULL,
  `responded_by_id`   INT(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `reports_supportrequest_report_id` (`report_id`),
  KEY `reports_supportrequest_author_id` (`author_id`),
  KEY `reports_supportrequest_responded_by_id` (`responded_by_id`),
  CONSTRAINT `support_report_fk`
    FOREIGN KEY (`report_id`) REFERENCES `reports_report` (`id`) ON DELETE CASCADE,
  CONSTRAINT `support_author_fk`
    FOREIGN KEY (`author_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `support_responded_by_fk`
    FOREIGN KEY (`responded_by_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 4: django_content_type
-- Required by Django's permission framework
-- =============================================================================

DROP TABLE IF EXISTS `auth_group_permissions`;
DROP TABLE IF EXISTS `auth_permission`;
DROP TABLE IF EXISTS `auth_group`;
DROP TABLE IF EXISTS `accounts_user_groups`;
DROP TABLE IF EXISTS `accounts_user_user_permissions`;
DROP TABLE IF EXISTS `django_content_type`;

CREATE TABLE `django_content_type` (
  `id`        INT(11) NOT NULL AUTO_INCREMENT,
  `app_label` VARCHAR(100) NOT NULL,
  `model`     VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model` (`app_label`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'accounts',   'user'),
(2, 'reports',    'report'),
(3, 'reports',    'supportrequest'),
(4, 'admin',      'logentry'),
(5, 'auth',       'permission'),
(6, 'auth',       'group'),
(7, 'contenttypes', 'contenttype'),
(8, 'sessions',   'session');

-- =============================================================================
-- TABLE 5: auth_permission
-- =============================================================================

CREATE TABLE `auth_permission` (
  `id`              INT(11) NOT NULL AUTO_INCREMENT,
  `name`            VARCHAR(255) NOT NULL,
  `content_type_id` INT(11) NOT NULL,
  `codename`        VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename` (`content_type_id`, `codename`),
  CONSTRAINT `auth_permission_content_type_fk`
    FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1,  'Can add user',             1, 'add_user'),
(2,  'Can change user',          1, 'change_user'),
(3,  'Can delete user',          1, 'delete_user'),
(4,  'Can view user',            1, 'view_user'),
(5,  'Can add report',           2, 'add_report'),
(6,  'Can change report',        2, 'change_report'),
(7,  'Can delete report',        2, 'delete_report'),
(8,  'Can view report',          2, 'view_report'),
(9,  'Can add support request',  3, 'add_supportrequest'),
(10, 'Can change support request',3,'change_supportrequest'),
(11, 'Can delete support request',3,'delete_supportrequest'),
(12, 'Can view support request', 3, 'view_supportrequest');

-- =============================================================================
-- TABLE 6: auth_group
-- =============================================================================

CREATE TABLE `auth_group` (
  `id`   INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL UNIQUE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 7: auth_group_permissions
-- =============================================================================

CREATE TABLE `auth_group_permissions` (
  `id`            INT(11) NOT NULL AUTO_INCREMENT,
  `group_id`      INT(11) NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id` (`group_id`, `permission_id`),
  CONSTRAINT `auth_group_permissions_group_fk`
    FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `auth_group_permissions_permission_fk`
    FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 8: accounts_user_groups (M2M)
-- =============================================================================

CREATE TABLE `accounts_user_groups` (
  `id`       INT(11) NOT NULL AUTO_INCREMENT,
  `user_id`  INT(11) NOT NULL,
  `group_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id` (`user_id`, `group_id`),
  CONSTRAINT `accounts_user_groups_user_fk`
    FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `accounts_user_groups_group_fk`
    FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 9: accounts_user_user_permissions (M2M)
-- =============================================================================

CREATE TABLE `accounts_user_user_permissions` (
  `id`            INT(11) NOT NULL AUTO_INCREMENT,
  `user_id`       INT(11) NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permissions_user_id_permission_id` (`user_id`, `permission_id`),
  CONSTRAINT `accounts_user_permissions_user_fk`
    FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `accounts_user_permissions_permission_fk`
    FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 10: django_session
-- =============================================================================

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key`  VARCHAR(40) NOT NULL,
  `session_data` LONGTEXT NOT NULL,
  `expire_date`  DATETIME(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- TABLE 11: django_migrations
-- Tracks which migrations have been applied
-- =============================================================================

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id`      INT(11) NOT NULL AUTO_INCREMENT,
  `app`     VARCHAR(255) NOT NULL,
  `name`    VARCHAR(255) NOT NULL,
  `applied` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `django_migrations` (`app`, `name`, `applied`) VALUES
('contenttypes', '0001_initial',                        NOW()),
('contenttypes', '0002_remove_content_type_name',       NOW()),
('auth',         '0001_initial',                        NOW()),
('auth',         '0002_alter_permission_name_max_length',NOW()),
('auth',         '0003_alter_user_email_max_length',    NOW()),
('auth',         '0004_alter_user_username_opts',       NOW()),
('auth',         '0005_alter_user_last_login_null',     NOW()),
('auth',         '0006_require_contenttypes_0002',      NOW()),
('auth',         '0007_alter_validators_add_error_messages',NOW()),
('auth',         '0008_alter_user_username_max_length', NOW()),
('auth',         '0009_alter_user_last_name_max_length',NOW()),
('auth',         '0010_alter_group_name_max_length',    NOW()),
('auth',         '0011_update_proxy_permissions',       NOW()),
('auth',         '0012_alter_user_first_name_max_length',NOW()),
('accounts',     '0001_initial',                        NOW()),
('accounts',     '0002_alter_user_role',                NOW()),
('accounts',     '0003_add_head_role',                  NOW()),
('accounts',     '0004_add_admin_role',                 NOW()),
('accounts',     '0005_add_admin_role',                 NOW()),
('accounts',     '0006_user_must_reset_password',       NOW()),
('accounts',     '0007_password_reset_token',           NOW()),
('accounts',     '0008_user_extra_roles',               NOW()),
('reports',      '0001_initial',                        NOW()),
('reports',      '0002_report_resubmission',            NOW()),
('reports',      '0003_report_assigned_by_convener',    NOW()),
('reports',      '0004_report_reviewer_attachment_sent_back_reassigned',NOW()),
('reports',      '0005_contributor_emails_reviewer_decision',NOW()),
('reports',      '0006_head_workflow',                  NOW()),
('reports',      '0007_final_report_and_doi',           NOW()),
('reports',      '0008_timeline_and_extensions',        NOW()),
('reports',      '0009_sync_doi_publication_fields',    NOW()),
('reports',      '0010_supportrequest',                 NOW()),
('sessions',     '0001_initial',                        NOW());

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- RESTORE INSTRUCTIONS
-- =============================================================================
-- 1. Create the database:
--      CREATE DATABASE reportportal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--      USE reportportal;
--
-- 2. Import this file:
--      mysql -u root -p reportportal < database_backup.sql
--
-- 3. Run seed command to create users with proper password hashes:
--      python manage.py seed_users
--
-- 4. To create the admin superuser separately:
--      python manage.py createsuperuser --email nirajan.kondapalli@ncmrwf.gov.in
--    OR rely on seed_users which auto-creates the admin.
--
-- KEY EMAILS:
--   Admin:     nirajan.kondapalli@ncmrwf.gov.in
--   Convener:  niranjan@ncmrwf.gov.in  (also reviewer + author)
--   Chairman:  indrani@ncmrwf.gov.in   (also reviewer + author)
--   Director:  director@ncmrwf.gov.in
--   Library:   library@ncmrwf.gov.in
--   Reviewers: see REVIEWERS list in seed_users.py
--
-- DEFAULT PASSWORD: NCMRWF@2024 (all users must change on first login)
-- =============================================================================
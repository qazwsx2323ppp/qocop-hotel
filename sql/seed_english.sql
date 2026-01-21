-- Seed English test data for HMS (guests/rooms/reservations)
-- Compatible with MySQL 5.7+ / MariaDB (no CTE required)
--
-- Notes:
-- - Does NOT touch `login`
-- - Keeps keys/constraints valid (FKs satisfied)
-- - Uses English names/addresses/cities/emails; reservation cancellation uses status='CANCELLED'

USE hms;

DROP TEMPORARY TABLE IF EXISTS tmp_seq;
CREATE TEMPORARY TABLE tmp_seq (
  n INT NOT NULL PRIMARY KEY
);

-- Generate 1..120 without WITH RECURSIVE
INSERT INTO tmp_seq (n)
SELECT (ones.i + tens.i * 10 + hundreds.i * 100) + 1 AS n
FROM
  (SELECT 0 i UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
   UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) ones
  CROSS JOIN
  (SELECT 0 i UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
   UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) tens
  CROSS JOIN
  (SELECT 0 i UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
   UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) hundreds
WHERE (ones.i + tens.i * 10 + hundreds.i * 100) < 120;

START TRANSACTION;

-- =========================
-- 1) guests：insert 60 rows
--    - English names / addresses / cities
--    - Some NULL emails / phones
-- =========================
INSERT INTO guests (id, name, address, email_id, phone, city, created_at)
SELECT
  CONCAT('guest_', 1000 + n) AS id,
  CONCAT(
    ELT(1 + MOD(n - 1, 10), 'John', 'Jane', 'Michael', 'Emily', 'David', 'Olivia', 'Daniel', 'Sophia', 'James', 'Emma'),
    ' ',
    ELT(1 + MOD(n - 1, 10), 'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Taylor'),
    CASE WHEN MOD(n, 12) = 0 THEN CONCAT(' (VIP-', n, ')') ELSE '' END
  ) AS name,
  CONCAT(
    10 + MOD(n * 7, 900),
    ' ',
    ELT(1 + MOD(n - 1, 8), 'Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Hill', 'Lake', 'Sunset'),
    ' St, ',
    ELT(1 + MOD(n - 1, 8), 'New York', 'London', 'Sydney', 'Toronto', 'Boston', 'Seattle', 'Austin', 'Chicago')
  ) AS address,
  CASE
    WHEN MOD(n, 9) = 0 THEN NULL
    ELSE CONCAT('guest', 1000 + n, '@example.com')
  END AS email_id,
  CASE
    WHEN MOD(n, 13) = 0 THEN NULL
    ELSE 13000000000 + n * 17
  END AS phone,
  ELT(1 + MOD(n - 1, 10), 'New York', 'London', 'Sydney', 'Toronto', 'Boston', 'Seattle', 'Austin', 'Chicago', 'Berlin', 'Paris') AS city,
  DATE_SUB(NOW(), INTERVAL (n * 2) DAY) AS created_at
FROM tmp_seq
WHERE n <= 60;

-- =========================
-- 2) rooms：insert 60 rows
--    - room_no UNIQUE (101..160)
--    - room_type alternates D/N
--    - status stored in English (computed status in app is derived from reservations)
-- =========================
INSERT INTO rooms (id, room_no, price, room_type, currently_booked, status, created_at)
SELECT
  CONCAT('room_', 2000 + n) AS id,
  CAST(9000 + n AS CHAR) AS room_no,
  (199 + MOD(n, 10) * 80 + CASE WHEN MOD(n, 2) = 1 THEN 500 ELSE 0 END) AS price,
  CASE WHEN MOD(n, 2) = 1 THEN 'D' ELSE 'N' END AS room_type,
  0 AS currently_booked,
  CASE
    WHEN MOD(n, 19) = 0 THEN 'MAINTENANCE'
    WHEN MOD(n, 17) = 0 THEN NULL
    ELSE 'AVAILABLE'
  END AS status,
  DATE_SUB(NOW(), INTERVAL n DAY) AS created_at
FROM tmp_seq
WHERE n <= 60;

-- =========================
-- 3) reservations：insert 120 rows
--    - Covers: future booked / ongoing / ended / cancelled
--    - Uses rooms room_2001..room_2045 (leave room_2046..room_2060 with no reservations)
--    - Cancellation is stored as status='CANCELLED' (app maps it to "取消")
-- =========================
INSERT INTO reservations (id, g_id, r_date, check_in, check_out, r_id, r_type, status, created_at)
SELECT
  CONCAT('res_', 3000 + n) AS id,
  CONCAT('guest_', 1000 + (1 + MOD(n - 1, 50))) AS g_id,
  CASE
    WHEN MOD(n, 9) = 0 THEN NULL
    ELSE DATE_SUB(NOW(), INTERVAL (n * 3) HOUR)
  END AS r_date,
  CASE
    WHEN n BETWEEN 1 AND 40
      THEN TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL (1 + MOD(n - 1, 30)) DAY), '14:00:00')
    WHEN n BETWEEN 41 AND 75
      THEN TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL (1 + MOD(n - 41, 20)) DAY), '14:00:00')
    WHEN n BETWEEN 76 AND 105
      THEN TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL (30 + MOD(n - 76, 30)) DAY), '14:00:00')
    ELSE
      TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL (2 + MOD(n - 106, 14)) DAY), '14:00:00')
  END AS check_in,
  CASE
    WHEN n BETWEEN 1 AND 40 THEN
      CASE
        WHEN MOD(n, 3) = 0 THEN NULL
        ELSE TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL (3 + MOD(n - 1, 30)) DAY), '12:00:00')
      END
    WHEN n BETWEEN 41 AND 75 THEN
      CASE
        WHEN MOD(n, 4) = 0 THEN TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL (1 + MOD(n - 41, 7)) DAY), '12:00:00')
        ELSE NULL
      END
    WHEN n BETWEEN 76 AND 105 THEN
      TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL (10 + MOD(n - 76, 20)) DAY), '12:00:00')
    ELSE NULL
  END AS check_out,
  CONCAT('room_', 2000 + (1 + MOD(n - 1, 45))) AS r_id,
  CASE WHEN MOD(1 + MOD(n - 1, 45), 2) = 1 THEN 'D' ELSE 'N' END AS r_type,
  CASE WHEN n BETWEEN 106 AND 120 THEN 'CANCELLED' ELSE NULL END AS status,
  DATE_SUB(NOW(), INTERVAL n HOUR) AS created_at
FROM tmp_seq
WHERE n <= 120;

COMMIT;

-- Sanity checks (optional)
SELECT COUNT(*) AS guests_seeded
FROM guests
WHERE id >= 'guest_1001' AND id <= 'guest_1060';

SELECT COUNT(*) AS rooms_seeded
FROM rooms
WHERE id >= 'room_2001' AND id <= 'room_2060';

SELECT COUNT(*) AS reservations_seeded
FROM reservations
WHERE id >= 'res_3001' AND id <= 'res_3120';

DROP TEMPORARY TABLE IF EXISTS tmp_seq;

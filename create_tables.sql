DROP TABLE IF EXISTS atis_log;
CREATE TABLE atis_log (
  id SERIAL PRIMARY KEY,
  datetime_utc TIMESTAMP,
  airport CHAR(4),
  atis VARCHAR 
);

DROP TABLE IF EXISTS atis_log_test;

CREATE TABLE atis_log_test (
  id SERIAL PRIMARY KEY,
  datetime_utc TIMESTAMP,
  airport CHAR(4) ,
  atis VARCHAR 
);

DROP TABLE IF EXISTS atis_log_detailed;
CREATE TABLE atis_log_detailed (
  id BIGINT PRIMARY KEY,
  airport CHAR(4),
  dt_start TIMESTAMP,
  dt_end TIMESTAMP,
  information CHAR(1),
  runway_mode VARCHAR,
  qnh SMALLINT,
  wind VARCHAR,
  wind_direction VARCHAR,
  wind_speed VARCHAR,
  wind_notes VARCHAR,
  cloud VARCHAR,
  visibility VARCHAR,
  lvo VARCHAR,
  atis_text VARCHAR,
  notes VARCHAR
);

DROP TABLE IF EXISTS atis_log_detailed_test;
CREATE TABLE atis_log_detailed_test (
  id BIGINT PRIMARY KEY,
  airport CHAR(4),
  dt_start TIMESTAMP,
  dt_end TIMESTAMP,
  information CHAR(1),
  runway_mode VARCHAR,
  qnh SMALLINT,
  wind VARCHAR,
  wind_direction VARCHAR,
  wind_speed VARCHAR,
  wind_notes VARCHAR,
  cloud VARCHAR,
  visibility VARCHAR,
  lvo VARCHAR,
  atis_text VARCHAR,
  notes VARCHAR
);

DROP TABLE IF EXISTS user_details;
CREATE TABLE user_details (
  id SERIAL PRIMARY KEY,
  username VARCHAR,
  password VARCHAR,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS notam_log;
CREATE TABLE notam_log (
  id SERIAL PRIMARY KEY,
  notam_id VARCHAR,
  notam_text VARCHAR,
  first_seen TIMESTAMP,
  airspace_id VARCHAR
);

DROP TABLE IF EXISTS notam_log_test;
CREATE TABLE notam_log_test (
  id SERIAL PRIMARY KEY,
  notam_id VARCHAR,
  notam_text VARCHAR,
  first_seen TIMESTAMP,
  airspace_id VARCHAR
);

DROP TABLE IF EXISTS notam_airspace_open;
CREATE TABLE notam_airspace_open (
  id SERIAL PRIMARY KEY,
  notam_log_id BIGINT,
  opening_dtg TIMESTAMP,
  closing_dtg TIMESTAMP
);

DROP TABLE IF EXISTS notam_airspace_open_test;
CREATE TABLE notam_airspace_open_test (
  id SERIAL PRIMARY KEY,
  notam_log_id BIGINT,
  opening_dtg TIMESTAMP,
  closing_dtg TIMESTAMP
);

INSERT INTO user_details
	(username,password)
VALUES
	('PYTHON_USER','fSc9AXRPcheyQTgc'); 
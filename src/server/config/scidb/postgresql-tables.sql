DROP TABLE IF EXISTS geo_time_unit CASCADE;
DROP TABLE IF EXISTS geo_array CASCADE;
DROP TABLE IF EXISTS geo_array_attributes CASCADE;
DROP TABLE IF EXISTS geo_array_timeline CASCADE;
DROP TABLE IF EXISTS geo_array_data_files CASCADE;

CREATE TABLE geo_time_unit (
  unit_id SERIAL PRIMARY KEY,
  name VARCHAR UNIQUE
);

CREATE TABLE geo_array (
  array_id SERIAL PRIMARY KEY,
  name VARCHAR UNIQUE NOT NULL,
  description VARCHAR,
  detail VARCHAR,
  crs VARCHAR NOT NULL,
  x_dim_name VARCHAR NOT NULL,
  x_min NUMERIC,
  x_max NUMERIC,
  x_resolution NUMERIC,
  y_dim_name VARCHAR,
  y_min NUMERIC,
  y_max NUMERIC,
  y_resolution NUMERIC,
  t_dim_name VARCHAR,
  t_min TIMESTAMP,
  t_max TIMESTAMP,
  t_resolution NUMERIC,
  t_unit_id INTEGER NOT NULL
);

CREATE TABLE geo_array_attributes (
  array_id INTEGER NOT NULL,
  attribute_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  description VARCHAR NOT NULL,
  range_min NUMERIC NOT NULL,
  range_max NUMERIC NOT NULL,
  scale NUMERIC NOT NULL DEFAULT 1.0,
  missing_value NUMERIC NOT NULL
);

CREATE TABLE geo_array_timeline (
  array_id INTEGER,
  time_point INTEGER NOT NULL,
  date TIMESTAMP NOT NULL,
  PRIMARY KEY(array_id, time_point)
);

CREATE TABLE geo_array_data_files (
  file_id SERIAL PRIMARY KEY,
  array_id INTEGER NOT NULL,
  time_point INTEGER NOT NULL,
  data_file VARCHAR NOT NULL,
  start_load_time TIMESTAMP DEFAULT NULL,
  end_load_time TIMESTAMP DEFAULT NULL
);

ALTER TABLE geo_array ADD CONSTRAINT fk_geo_array_t_unit_id FOREIGN KEY(t_unit_id) REFERENCES geo_time_unit(unit_id);
ALTER TABLE geo_array_attributes ADD CONSTRAINT fk_geo_array_attributes_array_id FOREIGN KEY(array_id) REFERENCES geo_array(array_id);
ALTER TABLE geo_array_timeline ADD CONSTRAINT fk_geo_array_timeline_array_id FOREIGN KEY(array_id) REFERENCES geo_array(array_id);
ALTER TABLE geo_array_data_files ADD CONSTRAINT fk_geo_array_data_files FOREIGN KEY(array_id, time_point) REFERENCES geo_array_timeline(array_id, time_point);

INSERT INTO geo_time_unit (name) VALUES('day'), ('month'), ('year');
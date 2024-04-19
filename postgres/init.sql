DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS param_types;
DROP TABLE IF EXISTS param_values;
DROP TABLE IF EXISTS aquariums;
DROP TABLE IF EXISTS test_kits;
DROP TABLE IF EXISTS register_access_codes;

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) NOT NULL UNIQUE,
	email VARCHAR(255),
	fullname VARCHAR(255),
	hash_password VARCHAR(255) NOT NULL,
	admin BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE register_access_codes (
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	key VARCHAR(255) NOT NULL UNIQUE, 
	created_on TIMESTAMP,
	used_on TIMESTAMP
);

CREATE TABLE param_types (
	name VARCHAR(255) PRIMARY KEY,
	unit VARCHAR(255) NOT NULL
);

CREATE TABLE test_kits (
	name VARCHAR(255) PRIMARY KEY,
	param_type_name VARCHAR(255) NOT NULL REFERENCES param_types(name) ON DELETE CASCADE,
	display_name VARCHAR(255) NOT NULL,
	display_unit VARCHAR(255) NOT NULL,
	description VARCHAR(255),
	is_default BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE aquariums (
	id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	name VARCHAR(255) NOT NULL,
	started_on TIMESTAMP
);

CREATE TABLE param_values (
	id SERIAL PRIMARY KEY, 
	user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	aquarium_id INTEGER NOT NULL REFERENCES aquariums(id) ON DELETE CASCADE,
	param_type_name VARCHAR(255) REFERENCES param_types(name) ON DELETE CASCADE,
	test_kit_name VARCHAR(255) NOT NULL REFERENCES test_kits(name) ON DELETE CASCADE,
	value NUMERIC NOT NULL,
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO param_types (name, unit)
VALUES 
	('alkalinity', 'dkh'),
	('calcium', 'ppm'),
	('magnesium', 'ppm'),
	('phosphate', 'ppm'),
	('nitrate', 'ppm'),
	('ph', 'pH');

INSERT INTO test_kits (name, param_type_name, display_name, display_unit, is_default)
VALUES
	('generic_dkh', 'alkalinity', 'Default dKH', 'dKH', true),
	('generic_calcium_ppm', 'calcium', 'Default ppm', 'ppm', true),
	('generic_magnesium_ppm', 'magnesium', 'Default ppm', 'ppm', true),
	('generic_phosphate_ppm', 'phosphate', 'Default ppm', 'ppm', true),
	('generic_nitrate_ppm', 'nitrate', 'Default ppm', 'ppm', true),
	('generic_ph', 'ph', 'Default pH', 'pH', true),
	('salifert_alkalinity', 'alkalinity', 'Salifert KH/Alk', 'mL', false)
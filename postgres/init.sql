DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS param_types;
DROP TABLE IF EXISTS param_values;
DROP TABLE IF EXISTS aquariums;
DROP TABLE IF EXISTS test_kits;
DROP TABLE IF EXISTS register_access_codes;
DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS additives;
DROP TABLE IF EXISTS event_dosings;
DROP TABLE IF EXISTS event_miscs;
DROP TABLE IF EXISTS event_water_changes;
DROP TABLE IF EXISTS events;

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) NOT NULL UNIQUE,
	email VARCHAR(255),
	fullname VARCHAR(255),
	hash_password VARCHAR(255) NOT NULL,
	is_admin BOOLEAN NOT NULL DEFAULT false,
	is_demo BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE register_access_codes (
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	key VARCHAR(255) NOT NULL UNIQUE, 
	created_on TIMESTAMP,
	used_on TIMESTAMP
);

CREATE TABLE param_types (
	name VARCHAR(20) PRIMARY KEY,
	unit VARCHAR(10) NOT NULL,
	display_name VARCHAR(20)
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
	note VARCHAR(255),
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE units (
	name VARCHAR(255) PRIMARY KEY,
	display_name VARCHAR(255) NOT NULL
);

CREATE TABLE additives (
	name VARCHAR(255) PRIMARY KEY,
	display_name VARCHAR(255) NOT NULL
);

CREATE TABLE event_dosings (
	id SERIAL PRIMARY KEY,
	additive_name VARCHAR(255) REFERENCES additives(name) ON DELETE CASCADE,
	quantity NUMERIC,
	description VARCHAR(255),
	unit_name VARCHAR(255) REFERENCES units(name) ON DELETE CASCADE
);

CREATE TABLE event_miscs (
	id SERIAL PRIMARY KEY,
	description VARCHAR(255) NOT NULL
);

CREATE TABLE event_water_changes (
	id SERIAL PRIMARY KEY,
	quantity NUMERIC,
	description VARCHAR(255),
	unit_name VARCHAR(255) REFERENCES units(name) ON DELETE CASCADE
);

CREATE TABLE events (
	id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	aquarium_id INTEGER NOT NULL REFERENCES aquariums(id) ON DELETE CASCADE,
	dosing_id INTEGER REFERENCES event_dosings(id) ON DELETE CASCADE,
	water_change_id INTEGER REFERENCES event_water_changes(id) ON DELETE CASCADE,
	misc_id INTEGER REFERENCES event_miscs(id) ON DELETE CASCADE,
	timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO units (name, display_name)
VALUES
	('mL', 'milliliters'),
	('L', 'liters'),
	('gal', 'gallons'),
	('ppm', 'parts per million'),
	('ppb', 'parts per billion'),
	('dkh', 'dKH');

INSERT INTO additives (name, display_name)
VALUES
	('kalkwasser', 'Kalkwasser'),
	('tropic-marin-np-bacto-balance', 'Tropic Marin NP-Bacto-Balance');

INSERT INTO param_types (name, unit, display_name)
VALUES 
	('alkalinity', 'dkh', 'Alkalinity'),
	('calcium', 'ppm', 'Calcium'),
	('magnesium', 'ppm', 'Magnesium'),
	('phosphate', 'ppm', 'Phosphate'),
	('nitrate', 'ppm', 'Nitrate'),
	('ph', 'pH', 'pH');

INSERT INTO test_kits (name, param_type_name, display_name, display_unit, is_default)
VALUES
	('generic_dkh', 'alkalinity', 'Default dKH', 'dKH', true),
	('generic_calcium_ppm', 'calcium', 'Default ppm', 'ppm', true),
	('generic_magnesium_ppm', 'magnesium', 'Default ppm', 'ppm', true),
	('generic_phosphate_ppm', 'phosphate', 'Default ppm', 'ppm', true),
	('generic_nitrate_ppm', 'nitrate', 'Default ppm', 'ppm', true),
	('generic_ph', 'ph', 'Default pH', 'pH', true),
	('salifert_alkalinity', 'alkalinity', 'Salifert KH/Alk', 'mL', false),
	('hanna_phosphorus_ulr', 'phosphate', 'Hanna Phosphorus ULR', 'ppb', false),
	('hanna_nitrate', 'nitrate', 'Hanna Nitrate', 'ppm', false);
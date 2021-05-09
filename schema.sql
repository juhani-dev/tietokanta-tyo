CREATE TABLE topics (
	id SERIAL PRIMRY KEY,
	topic TEXT,
	visible INTEGER,
	time TIMESTAMP
);
CREATE TABLE messages (
	id SERIAL PRIMARY KEY,
	message_id INTEGER REFERENCES topics,
	message TEXT,
	userame TEXT,
	visible INTEGER
);
CREATE TABLE usersf (
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE,
	password TEXT,
 	message_id INTEGER REFERENCES messages,
	topic_id INTEGER REFERENCES topics,
	admin INTERGER
);

CREATE TABLE topic_creator (
	topic_id INTEGER REFERENCES topics,
	user_id INTEGER REFERENCES userdf
);

CREATE TABLE private_messages (
	id SERIAL PRIMARY KEY,
	message TEXT,
	visible INTEGER,
	username_from TEXT,
	username_to TEXT,
	time TIMESTAMP
);

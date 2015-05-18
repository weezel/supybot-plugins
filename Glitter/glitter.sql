CREATE TABLE nick(nid INTEGER PRIMARY KEY NOT NULL,
	     nick VARCHAR(20) UNIQUE NOT NULL);
CREATE TABLE channel(cid INTEGER PRIMARY KEY NOT NULL,
	     channel VARCHAR(20) UNIQUE NOT NULL);
CREATE TABLE message(mid INTEGER PRIMARY KEY NOT NULL,
	     message VARCHAR(512) UNIQUE NOT NULL);
CREATE TABLE tag(tid INTEGER PRIMARY KEY NOT NULL,
	     message INTEGER NOT NULL,
	     tag VARCHAR(128) UNIQUE NOT NULL,
	     FOREIGN KEY(message) REFERENCES message(mid));
CREATE TABLE glitter(gid INTEGER PRIMARY KEY NOT NULL,
	date TEXT(23) NOT NULL,
	nick INTEGER NOT NULL,
	channel INTEGER NOT NULL,
	message INTEGER NOT NULL,
	tag INTEGER NOT NULL,
	FOREIGN KEY(nick) REFERENCES nick(nid),
	FOREIGN KEY(channel) REFERENCES channel(cid),
	FOREIGN KEY(message) REFERENCES message(mid),
	FOREIGN KEY(tag) REFERENCES tag(tid),
	UNIQUE (nick, message));

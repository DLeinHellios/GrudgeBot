-- Creates blank database tables

CREATE TABLE "games" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT UNIQUE,
	"full_name"	TEXT,
	"argument"	TEXT UNIQUE,
	"platform"	TEXT,
	"developer"	TEXT,
	"release_year"	INTEGER,
	"thumbnail"	TEXT,
	"links"	TEXT,
	"characters"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "streams" (
	"id"	INTEGER NOT NULL UNIQUE,
	"stream_id"	TEXT,
	"service"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "taunts" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"author"	TEXT,
	"body"		TEXT
);

CREATE TABLE "champs" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"game_id" INTEGER NOT NULL,
	"player" TEXT NOT NULL,
	"crown_date" DATE
);

-- Creates blank database tables

CREATE TABLE "games" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"arg"	TEXT NOT NULL UNIQUE,
	"platform"	TEXT,
	"developer"	TEXT,
	"release"	TEXT,
	"movelist"	TEXT,
	"characters"	TEXT
)

CREATE TABLE "streams" (
	"id"	INTEGER NOT NULL UNIQUE,
	"stream_id"	TEXT NOT NULL,
	"service"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "taunts" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"author"	TEXT,
	"body"	TEXT
)

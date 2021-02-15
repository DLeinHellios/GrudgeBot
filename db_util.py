#db_util.py - SQLite migration utility for GrudgeBot

import os, sys
import sqlite3 as sql


dbFile = "data.db"
backupFile = "data.db.backup"


def create_db(conn, cursor):
    '''Creates blank database w/ tables'''
    print("> Creating database tables", end='\r')
    with open(os.path.join("src","sql","create_db.sql"), 'r') as sql_file:
        sql_script = sql_file.read()

    cursor.executescript(sql_script)
    conn.commit()
    print("> Creating database tables - DONE")


def manage_old_files():
    '''Manages files for old versions of the database'''
    print("> Cleaning up old backups", end="\r")
    if os.path.isfile(backupFile) and os.path.isfile(dbFile):
        os.remove(backupFile)
        print("> Cleaning up old backups - DONE")

    print("> Backing up current database", end="\r")
    if os.path.isfile(dbFile):
        os.rename(dbFile, backupFile)
    print("> Backing up current database - DONE")


def import_old_data(conn, cursor):
    '''Reads data from previous database version and attempts to import it'''
    oldConn = sql.connect(backupFile)
    oldCursor = oldConn.cursor()

    try:
        print("> Importing taunt data", end="\r")
        oldCursor.execute('SELECT * FROM taunts')
        tauntData = oldCursor.fetchall()

        for taunt in tauntData:
            cursor.execute('INSERT INTO taunts ("author", "body") VALUES (?, ?)', (taunt[1], taunt[2]))
            conn.commit()

        print("> Importing taunt data - DONE")

    except:
        print("> Warning - Unable to import taunt data")

    try:
        print("> Importing stream data", end="\r")
        oldCursor.execute('SELECT * FROM streams')
        streamData = oldCursor.fetchall()

        for stream in streamData:
            cursor.execute('INSERT INTO streams ("stream_id", "service") VALUES (?,?)', (stream[1], stream[2]))
            conn.commit()

        print("> Importing stream data - DONE")

    except:
        print("> Warning - Unable to import stream data")

    oldConn.close()


def main():
    print("------------------------------------")
    print("     GrudgeBot Database Utility     ")
    print("------------------------------------")

    print("> Checking for previous database versions...")

    if os.path.isfile(dbFile):
        # Database already exists, prep for migrate
        if input("\nPrevious version detected, migrate to new database? <y/n> ").lower() == 'y':
            manage_old_files()
            db = sql.connect(dbFile)
            cursor = db.cursor()

            create_db(db, cursor)
            # move data from old db
            import_old_data(db, cursor)
            # read game data

            db.close()
            print("> Database successfully migrated to newest version! Exiting...")

        else:
            print("> Action cancelled, exiting...")

    else:
        # No database found, build fresh
        if input("\nNo database found, create a new one? <y/n> ").lower() == 'y':
            db = sql.connect(dbFile)
            cursor = db.cursor()

            create_db(db, cursor)
            # Read game data here
            db.close()
            print("> New database has been created successfully! Exiting...")

        else:
            print("> Action cancelled. Exiting...")


if __name__ == "__main__":
    main()

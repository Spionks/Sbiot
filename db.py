import sqlite3
import os

class DB():
    def __init__(self, ) -> None:
        self.con = sqlite3.connect(os.environ["DATABASE_FILEPATH"])
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        # ensure that the database is set up correctly
        self.init_db()

    def init_db(self):
        with open("init_db.sql") as file:
            self.cur.executescript(file.read())

    def get_record(self, username, record_name):
        self.cur.execute("SELECT * \
            FROM records \
            WHERE username = ? \
            AND record_name = ?", (username, record_name))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["val"]

    

    def get_all_users_record(self, record_name):
        self.cur.execute("SELECT * \
            FROM records \
            WHERE record_name = ?", (record_name,))

        fetched = self.cur.fetchall()
        if not fetched:
            return None
        else:
            result = {}
            for row in fetched:
                result[row["username"]] = row["val"]
            return result

    
    def update_record(self, username, record_name, value):
        current_record = self.get_record(username, record_name)
        if current_record:
            self.cur.execute("UPDATE records \
                SET val = ? \
                WHERE username = ? \
                AND record_name = ?", (value, username, record_name))
        else:
            self.cur.execute("INSERT INTO records \
                VALUES (?, ?, ?)", (username, record_name, value))

        self.con.commit()


        
    def set_rsn(self, rsn, discord_name):
        current_discord_name = self.get_discord_name(rsn)
        if current_discord_name:
            self.cur.execute("UPDATE rsn_discord_names \
                SET discord_name = ? \
                WHERE rsn = ? ", (discord_name, rsn))
        else:
            self.cur.execute("INSERT INTO rsn_discord_names \
                VALUES (?, ?)", (rsn, discord_name))

        self.con.commit()

    def get_discord_name(self, rsn):
        self.cur.execute("SELECT * \
            FROM rsn_discord_names \
            WHERE rsn = ? ", (rsn,))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["discord_name"]

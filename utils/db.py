import sqlite3
from .bot import ModBot

class Database():
    def __init__(self, db_name="database.db"):
        self.con = sqlite3.connect(db_name)
        self.con.execute("CREATE TABLE IF NOT EXISTS reports (case_id INTEGER, guild_id INTEGER, user_id INTEGER, moderator_id INTEGER, reason TEXT, case_type TEXT, timestamp TEXT)")
        # server_config table
        self.con.execute("CREATE TABLE IF NOT EXISTS server_config (guild_id INTEGER, log_channel_id INTEGER, reports_channel_id INTEGER, role_id INTEGER, staff_role_id INTEGER)")
        # level table
        self.con.execute("CREATE TABLE IF NOT EXISTS levels (guild_id INTEGER, user_id INTEGER, level INTEGER, xp INTEGER)")
        # roles table
        self.con.execute("CREATE TABLE IF NOT EXISTS roles (guild_id INTEGER, role_id INTEGER, level INTEGER)")

    ###########################################

    def add_case(self, case_id: int, guild_id: int, user_id: int, moderator_id: int, reason: str, case_type: str, timestamp: str):
        self.con.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?)", (case_id, guild_id, user_id, moderator_id, reason, case_type, timestamp))
        self.con.commit()

    def get_case(self, case_id: int):
        return self.con.execute("SELECT * FROM reports WHERE case_id = ?", (case_id,)).fetchone()

    def get_cases(self, guild_id: int):
        return self.con.execute("SELECT * FROM reports WHERE guild_id = ?", (guild_id,)).fetchall()
    
    def edit_case(self, case_id: int, guild_id: int, reason: str):
        self.con.execute("UPDATE reports SET reason = ? WHERE case_id = ? AND guild_id = ?", (reason, case_id, guild_id))
        self.con.commit()

    def delete_case(self, case_id: int):
        self.con.execute("DELETE FROM reports WHERE case_id = ?", (case_id,))
        self.con.commit()

    def delete_cases(self, guild_id: int):
        self.con.execute("DELETE FROM reports WHERE guild_id = ?", (guild_id,))
        self.con.commit()

    def find_case_warns(self, guild_id: int, user_id: int):
        return self.con.execute("SELECT * FROM reports WHERE guild_id = ? AND user_id = ? AND case_type = ?", (guild_id, user_id, "warn")).fetchall()

    ###########################################

    def add_level(self, guild_id: int, user_id: int, level: int, xp: int):
        self.con.execute("INSERT INTO levels VALUES (?, ?, ?, ?)", (guild_id, user_id, level, xp))
        self.con.commit()

    def get_level(self, guild_id: int, user_id: int):
        return self.con.execute("SELECT * FROM levels WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)).fetchone()

    def update_level(self, guild_id: int, user_id: int, level: int, xp: int):   
        self.con.execute("UPDATE levels SET level = ?, xp = ? WHERE guild_id = ? AND user_id = ?", (level, xp, guild_id, user_id))
        self.con.commit()

    def get_levels(self, guild_id: int):
        return self.con.execute("SELECT * FROM levels WHERE guild_id = ?", (guild_id,)).fetchall()

    def delete_level(self, guild_id: int, user_id: int):
        self.con.execute("DELETE FROM levels WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        self.con.commit()

    def add_role(self, guild_id: int, role_id: int, level: int):
        # make a new table using the guild id and add the role and level to it to a colum, so you can have multiple roles per guild
        self.con.execute(f"INSERT INTO roles VALUES (?, ?, ?)", (guild_id, role_id, level))
        self.con.commit()

    def delete_role(self, guild_id: int, role_id: int=None, level: int=None):
        # if role_id was not provided, from the level, get the role_id and delete it
        if role_id is None:
            self.con.execute("DELETE FROM roles WHERE guild_id = ? AND level = ?", (guild_id, level))
        else:
            self.con.execute("DELETE FROM roles WHERE guild_id = ? AND role_id = ?", (guild_id, role_id))
        self.con.commit()

    def get_roles(self, guild_id: int):
        return self.con.execute("SELECT * FROM roles WHERE guild_id = ?", (guild_id,)).fetchall()

    def delete_roles(self, guild_id: int):
        self.con.execute("DELETE FROM roles WHERE guild_id = ?", (guild_id,))
        self.con.commit()

    def get_role_by_level(self, guild_id: int, level: int):
        return self.con.execute("SELECT * FROM roles WHERE guild_id = ? AND level = ?", (guild_id, level)).fetchone()

    ###########################################

    def add_config(self, guild_id: int, log_channel_id: int, reports_channel_id: int, role_id: int, staff_role_id: int):
        self.con.execute("INSERT INTO server_config VALUES (?, ?, ?, ?, ?)", (guild_id, log_channel_id, reports_channel_id, role_id, staff_role_id))
        self.con.commit()

    def get_config(self, guild_id: int):
        return self.con.execute("SELECT * FROM server_config WHERE guild_id = ?", (guild_id,)).fetchone()

    def update_config(self, guild_id: int, log_channel_id: int, reports_channel_id: int, role_id: int, staff_role_id: int):
        self.con.execute("UPDATE server_config SET log_channel_id = ?, reports_channel_id = ?, role_id = ?, staff_role_id = ? WHERE guild_id = ?", (log_channel_id, reports_channel_id, role_id, staff_role_id, guild_id))
        self.con.commit()

    def delete_config(self, guild_id: int):
        self.con.execute("DELETE FROM server_config WHERE guild_id = ?", (guild_id,))
        self.con.commit()

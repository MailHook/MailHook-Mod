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

    ###########################################
    def add_report(self, case_id: int, guild_id: int, user_id: int, moderator_id: int, reason: str, case_type: str, timestamp: str):
       try:
        self.con.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?)", (case_id, guild_id, user_id, moderator_id, reason, case_type, timestamp))
        self.con.commit()
       except Exception as e:
        print(e)

    def edit_report(self, case_id: int, reason: str):
        self.con.execute("UPDATE reports SET reason = ? WHERE case_id = ?", (reason, case_id))
        self.con.commit()

    def delete_report(self, case_id: int):
        self.con.execute("DELETE FROM reports WHERE case_id = ?", (case_id,))
        self.con.commit()

    def get_report(self, case_id: int):
        return self.con.execute("SELECT * FROM reports WHERE case_id = ?", (case_id,)).fetchone()

    def get_reports(self, guild_id: int):
        return self.con.execute("SELECT * FROM reports WHERE guild_id = ?", (guild_id,)).fetchall()
    ###########################################

    def add_guild(self, guild_id: int, channel_id: int, reports_id: int, role_id: int, staff_role_id: int):
        self.con.execute("INSERT INTO server_config VALUES (?, ?, ?, ?, ?)", (guild_id, channel_id, reports_id, role_id, staff_role_id))
        self.con.commit()

    def delete_guild(self, guild_id: int):
        self.con.execute("DELETE FROM server_config WHERE guild_id = ?", (guild_id,))
        self.con.commit()
    
    def update_guild(self, guild_id: int, channel_id: int, role_id: int, staff_role_id: int):
        self.con.execute("UPDATE server_config SET channel_id = ?, role_id = ?, staff_role_id = ?, staff_role_id_2 = ? WHERE guild_id = ?", (channel_id, role_id, staff_role_id, guild_id))
        self.con.commit()

    def edit_staff_role(self, guild_id: int, role_id: int):
        self.con.execute("UPDATE server_config SET staff_role_id = ? WHERE guild_id = ?", (role_id, guild_id))
        self.con.commit()

    def edit_modlog_channel(self, guild_id: int, channel_id: int):
        self.con.execute("UPDATE server_config SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
        self.con.commit()

    def edit_reports_channel(self, guild_id: int, channel_id: int):
        self.con.execute("UPDATE server_config SET reports_channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
        self.con.commit()

    def edit_mute_role(self, guild_id: int, role_id: int):
        self.con.execute("UPDATE server_config SET role_id = ? WHERE guild_id = ?", (role_id, guild_id))
        self.con.commit()

    def get_guild(self, guild_id: int):
        return self.con.execute("SELECT * FROM server_config WHERE guild_id = ?", (guild_id,)).fetchone()
    ###########################################

    def add_level(self, guild_id: int, user_id: int, level: int, xp: int):
        self.con.execute("INSERT INTO levels VALUES (?, ?, ?, ?)", (guild_id, user_id, level, xp))
        self.con.commit()

    def get_level(self, guild_id: int, user_id: int):
        return self.con.execute("SELECT * FROM levels WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)).fetchone()

    def update_level(self, guild_id: int, user_id: int, level: int):
        self.con.execute("UPDATE levels SET level = ? WHERE guild_id = ? AND user_id = ?", (level, guild_id, user_id))
        self.con.commit()

    def show_all_levels(self, guild_id: int):
        return self.con.execute("SELECT * FROM levels WHERE guild_id = ?", (guild_id,)).fetchall()
    
    def show_xp(self, guild_id: int, user_id: int):
        return self.con.execute("SELECT * FROM levels WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)).fetchone()

    def update_xp(self, guild_id: int, user_id: int, level: int, xp: int):
        self.con.execute("UPDATE levels SET level = ?, xp = ? WHERE guild_id = ? AND user_id = ?", (level, xp, guild_id, user_id))
        self.con.commit()
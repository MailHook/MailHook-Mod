import discord
from discord.ext import commands
from utils.bot import ModBot
from utils.db import Database

class Events(commands.Cog):
    def __init__(self, bot: ModBot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener("on_guild_remove")
    async def data_remove(self, guild):
        # move all data from all tables to a new table
        try:
            self.db.remove_guild(guild.id)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Events(bot))
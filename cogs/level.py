import asyncio
import datetime
from msilib.schema import AppSearch
from click import command
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.db import Database

no_xp_list = []

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.is_weekend = False
        ############################
        self.weekend_xp = 5
        self.xp_per_message = 1
        ############################
        self.max_level = 100
        self.max_xp = 100

    # this is a task that runs everyone one day
    @tasks.loop(hours=12)
    async def check_weekend(self):
        now = datetime.datetime.now()
        if now.weekday() == 5 or now.weekday() == 6:
            self.is_weekend = True
            print("It is the weekend!")
        else:
            self.is_weekend = False
            print("It is not the weekend!")

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.content.startswith(self.bot.command_prefix):
            return

        guild_id = message.guild.id
        user_id = message.author.id
        xp = self.db.show_xp(guild_id, user_id)
        if xp is None:
            self.db.add_level(guild_id, user_id, 1, 1)
        else:
            level = xp[2]
            xp = xp[3]
            # if it is the weekend, then give 2x xp
            if self.is_weekend:
                xp += self.weekend_xp
            else:
                xp += self.xp_per_message

            if user_id in no_xp_list:
                return

            if level == self.max_level:
                return

            if xp >= self.max_xp:
                level += 1
                xp = 0
                if level == self.max_level:
                    await message.channel.send(f"Congrats {message.author.mention}, you have reached max level!")
                else:
                 await message.channel.send(f"{message.author.mention} has leveled up to level {level}!", delete_after=10)
                # use update level
            self.db.update_level(guild_id, user_id, level, xp)
            # add user to no_xp_list for 2 seconds so they don't get xp for spamming
            no_xp_list.append(user_id)
            await asyncio.sleep(2)
            no_xp_list.remove(user_id)

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.check_weekend.start()

    @app_commands.command(name="level", description="Shows your level")
    async def level(self, ctx: discord.Integration):
        guild_id = ctx.guild.id
        user_id = ctx.user.id
        xp = self.db.show_xp(guild_id, user_id)
        if xp is None:
            await ctx.response.send_message("You have not sent any messages yet!", ephemeral=True)
        else:
            level = xp[2]
            xp = xp[3]
            await ctx.response.send_message(f"You are level {level} with {xp}/{self.max_xp} xp", ephemeral=True)

    @app_commands.command(name="leaderboard", description="Shows the leaderboard")
    async def leaderboard(self, ctx: discord.Integration):
        guild_id = ctx.guild.id
        users_2 = self.db.show_all_levels(guild_id)
        # send an embed with the leaderboard and the users
        embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
        # highest level to lowest level in order
        users = sorted(users_2, key=lambda x: x[2], reverse=True)
        for user in users:
            user_id = user[1]
            level = user[2]
            xp = user[3]
            user = self.bot.get_user(user_id)
            embed.add_field(name=user.name, value=f"Level: {level} | XP: {xp}/{self.max_xp}", inline=False)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setxp", description="Sets the xp for a user")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setxp(self, ctx: discord.Integration, user: discord.User, xp: int):
        guild_id = ctx.guild.id
        user_id = user.id
        if xp > self.max_xp:
            await ctx.response.send_message("You can't set xp higher than the max xp!", ephemeral=True)
            return
        self.db.update_xp(guild_id, user_id, 1, xp)
        await ctx.response.send_message(f"{user} has been set to {xp} xp", ephemeral=True)

    @app_commands.command(name="setlevel", description="Sets the level for a user")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlevel(self, ctx: discord.Integration, user: discord.User, level: int):
        guild_id = ctx.guild.id
        user_id = user.id

        # check if is in the database
        data = self.db.show_xp(guild_id, user_id)
        if data is None:
            await ctx.response.send_message("That user is not in the database!", ephemeral=True)
            return
        if level > self.max_level:
            await ctx.response.send_message("You can't set level higher than the max level!", ephemeral=True)
            return
        self.db.update_level(guild_id, user_id, level)
        await ctx.response.send_message(f"{user} has been set to level {level}", ephemeral=True)

    @app_commands.command(name="reset", description="Resets a user's xp and level")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset(self, ctx: discord.Integration, user: discord.User):
        user_id = user.id
        # remove user from database
        self.db.remove_user(user_id)
        await ctx.response.send_message(f"{user} has been reset!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Level(bot))
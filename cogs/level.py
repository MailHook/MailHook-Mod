import asyncio
import datetime
from typing import List
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.db import Database
from utils.embed import custom_embed
from utils.level_core import Level_core

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
        self.level_core = Level_core(self.bot)

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
        await self.level_core.level_up(message, self.is_weekend)

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.check_weekend.start()
            
    @app_commands.command(name="profile", description="Shows your profile")
    async def profile(self, ctx: discord.Integration, user: discord.User = None):
        # show the user's level, xp, and rank on the leaderboard
        if user is None:
            user = ctx.user
        # check if user is a bot
        if user.bot:
            await ctx.response.send_message("Bots don't have levels!", ephemeral=True)
            return
        data = self.db.get_level(ctx.guild.id, user.id)
        if data is None:
            await ctx.response.send_message(f"{user.name} has not sent any messages yet!", ephemeral=True)
        else:
            level = data[2]
            xp = data[3]
            embed = discord.Embed(title=f"{user.name}'s Profile", color=discord.Color.blurple())
            embed.add_field(name="Level", value=level, inline=False)
            _bar = await self.level_core.xp_bar(xp)
            currtent_xp = f"{xp}/{self.max_xp}"
            embed.add_field(name="XP", value=f"{_bar} {currtent_xp}", inline=False)
            embed.set_footer(text=f"Requested by {user.name}", icon_url=user.avatar.url)
            await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="leaderboard", description="Shows the leaderboard")
    async def leaderboard(self, ctx: discord.Integration):
        await self.level_core.leaderboard(ctx)

    @app_commands.command(name="setlevel", description="Sets the level for a user")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlevel(self, ctx: discord.Integration, user: discord.User, level: int):
        guild_id = ctx.guild.id
        user_id = user.id

        # check if is in the database
        data = self.db.get_level(guild_id, user_id)
        if data is None:
            await ctx.response.send_message("That user is not in the database!", ephemeral=True)
            return
        if level > self.max_level:
            await ctx.response.send_message("You can't set level higher than the max level!", ephemeral=True)
            return
        self.db.update_level(guild_id, user_id, level, 0)
        await ctx.response.send_message(f"{user} has been set to level {level}", ephemeral=True)

    @app_commands.command(name="reset", description="Resets a user's xp and level")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset(self, ctx: discord.Integration, user: discord.User):
        user_id = user.id
        # remove user from database
        self.db.delete_level(ctx.guild.id, user_id)
        await ctx.response.send_message(f"{user} has been reset!", ephemeral=True)

    @app_commands.command(name="set-level-role", description="Sets the level role")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_level_role(self, ctx: discord.Integration, level: int, role: discord.Role):
        if level > self.max_level:
            await ctx.response.send_message("You can't set a role higher than the max level!", ephemeral=True)
            return
        self.db.add_role(ctx.guild.id, role.id, level)
        await ctx.response.send_message(f"Level {level} role has been set to {role.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Level(bot))
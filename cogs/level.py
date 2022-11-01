import asyncio
import datetime
from typing import List
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.db import Database
from utils.embed import custom_embed
from utils.core import Level_core

no_xp_list = []

class Level_System(commands.Cog):
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
    
    level = app_commands.Group(name="level", description="Level commands")

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

    @app_commands.command(name="set-level-role", description="Sets the level role")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_level_role(self, ctx: discord.Integration, level: int, role: discord.Role):
        if level > self.max_level:
            await ctx.response.send_message("You can't set a role higher than the max level!", ephemeral=True)
            return
        # check if role is already in the database
        data = self.db.get_role_by_level(ctx.guild.id, level)
        if data is not None:
            await ctx.response.send_message("That level already has a role!", ephemeral=True)
            return
        self.db.add_role(ctx.guild.id, role.id, level)
        await ctx.response.send_message(f"Level {level} role has been set to {role.mention}", ephemeral=True)

    @app_commands.command(name="get-level-roles", description="Gets the level roles")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def get_level_roles(self, ctx: discord.Integration):
        data = self.db.get_roles(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("There are no level roles!", ephemeral=True)
            return
        embed = discord.Embed(title="Level Roles", color=discord.Color.blurple())
        for role in data:
            embed.add_field(name=f"Level {role[2]}", value=f"<@&{role[1]}>", inline=False)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="remove-level-role", description="Removes a level role")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_level_role(self, ctx: discord.Integration, role: discord.Role=None, level: int=None):
        if role is None:
            self.db.delete_role(ctx.guild.id, None, level)
            await ctx.response.send_message(f"Level {level} role has been removed!", ephemeral=True)
        elif level is None:
            self.db.delete_role(ctx.guild.id, role.id, None)
            await ctx.response.send_message(f"{role.mention} role has been removed!", ephemeral=True)
        else:
            self.db.delete_role(ctx.guild.id, role.id, level)
            await ctx.response.send_message(f"{role.mention} has been removed!", ephemeral=True)

    @level.command(name="profile", description="Shows your profile")
    async def profile(self, ctx: discord.Integration, member: discord.Member=None):
        await self.level_core.profile(ctx, member)

    @level.command(name="leaderboard", description="Shows the leaderboard")
    async def leaderboard(self, ctx: discord.Integration):
        await self.level_core.leaderboard(ctx)

    @level.command(name="setlevel", description="Sets your level")
    async def setlevel(self, ctx: discord.Integration, level: int):
        if level > self.max_level:
            await ctx.response.send_message("You can't set level higher than the max level!", ephemeral=True)
            return
        self.db.update_level(ctx.guild.id, ctx.user.id, level, 0)
        await ctx.response.send_message(f"Your level has been set to {level}", ephemeral=True)

    @level.command(name="set-level", description="Sets the level for a user")
    @app_commands.describe(user="The user to set the level for", level="The level to set")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_level(self, ctx: discord.Integration, user: discord.User, level: int):
        guild_id = ctx.guild.id
        user_id = user.id

        data = self.db.get_level(guild_id, user_id)
        if data is None:
            await ctx.response.send_message("That user is not in the database!", ephemeral=True)
            return
        if level > self.max_level:
            await ctx.response.send_message("You can't set level higher than the max level!", ephemeral=True)
            return
        self.db.update_level(guild_id, user_id, level, 0)
        await ctx.response.send_message(f"{user} has been set to level {level}", ephemeral=True)

    @level.command(name="reset", description="Resets a user level")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(user="The user to reset")
    async def reset(self, ctx: discord.Integration, user: discord.User):
        user_id = user.id
        self.db.delete_level(ctx.guild.id, user_id)
        await ctx.response.send_message(f"{user} has been reset!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Level_System(bot))
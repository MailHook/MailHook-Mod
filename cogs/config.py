import discord
import pygit2
import itertools
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from discord.ext import commands
from utils.bot import ModBot
from discord import app_commands
from typing import Union
import requests
from utils.db import Database

class Config(commands.Cog):
    def __init__(self, bot: ModBot):
            self.bot = bot
            self.db = Database("logs.db")

    @app_commands.command(name="config", description="Configure the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(self, ctx):
        data = self.db.get_guild(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("This server is not configured yet. Please run `/setup` to configure the bot.")
            return  
        role = discord.utils.get(ctx.guild.roles, id=data[3])
        role2 = discord.utils.get(ctx.guild.roles, id=data[4])
        txt = f"""
        **Server Configuration**
Logging Channel: <#{data[1]}>
Report Channel: <#{data[2]}>
Mute Role: {role.mention}
Staff Role: {role2.mention}
To edit the configuration, run `/editconfig`
        """
        print(data)
        await ctx.response.send_message(txt)

    @app_commands.command(name="editconfig", description="Edit the bot configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def editconfig(self, ctx, log_channel: discord.TextChannel = None, report_channel: discord.TextChannel = None, role: discord.Role = None, staff_role: discord.Role = None):
        if log_channel is not None:
            self.db.edit_modlog_channel(ctx.guild.id, log_channel.id)
        if report_channel is not None:
            self.db.edit_reports_channel(ctx.guild.id, report_channel.id)
        if role is not None:
            self.db.edit_mute_role(ctx.guild.id, role.id)
        if staff_role is not None:
            self.db.edit_staff_role(ctx.guild.id, staff_role.id)
        await ctx.response.send_message("Successfully edited the configuration.")

    @app_commands.command(name="setup", description="Setup the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx, logging_channel: discord.TextChannel, report_channel: discord.TextChannel, mute_role: discord.Role, staff_role: discord.Role):
        data = self.db.get_guild(ctx.guild.id)
        if data is not None:
            await ctx.response.send_message("This server is already configured.")
            return
        try:
         self.db.add_guild(ctx.guild.id, logging_channel.id, report_channel.id, mute_role.id, staff_role.id)
         await ctx.response.send_message("Successfully configured the bot.")
        except Exception as e:
            print(e)
            await ctx.response.send_message("An error occurred while configuring the bot.")

async def setup(bot):
    await bot.add_cog(Config(bot))
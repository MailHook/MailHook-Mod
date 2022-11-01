import discord
from dotenv import load_dotenv
load_dotenv()

from discord.ext import commands
from utils.bot import ModBot
from discord import app_commands
from utils.db import Database

class Config(commands.Cog):
    def __init__(self, bot: ModBot):
            self.bot = bot
            self.db = Database()

    @app_commands.command(name="config", description="Configure the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(self, ctx):
        data = self.db.get_config(ctx.guild.id)
        if data is None:
         await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
         return
        embed = discord.Embed(title="Config", description=f"Configure for {ctx.guild.name}", color=0x00ff00)
        # log channel, mod role, mute role
        log_channel = self.bot.get_channel(data[1])
        report_channel = self.bot.get_channel(data[2])
        mute_role = ctx.guild.get_role(data[3])
        staff_role = ctx.guild.get_role(data[4])
        embed.add_field(name="Log Channel", value=log_channel.mention)
        embed.add_field(name="Report Channel", value=report_channel.mention)
        embed.add_field(name="Staff Role", value=staff_role.mention)
        embed.add_field(name="Mute Role", value=mute_role.mention)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="editconfig", description="Edit the config")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        log_channel="The log channel",
        report_channel="The report channel",
        staff_role="The mod role",
        mute_role="The mute role",
        ticket_category="The ticket category"
    )
    async def edit(self, ctx, log_channel: discord.TextChannel=None, report_channel: discord.TextChannel=None, staff_role: discord.Role=None, mute_role: discord.Role=None, ticket_category: discord.CategoryChannel=None):
        data = self.db.get_config(ctx.guild.id)
        if data is None:
         await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
         return
        if log_channel is not None:
            self.db.edit_log_channel(ctx.guild.id, log_channel.id)
        if report_channel is not None:
            self.db.edit_reports_channel(ctx.guild.id, report_channel.id)
        if staff_role is not None:
            self.db.edit_staff_role(ctx.guild.id, staff_role.id)
        if mute_role is not None:
            self.db.edit_role(ctx.guild.id, mute_role.id)
        if ticket_category is not None:
            self.db.edit_ticket_category(ctx.guild.id, ticket_category.id)
        await ctx.response.send_message("Config updated", ephemeral=True)

    @app_commands.command(name="setup", description="Setup the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx, log_channel: discord.TextChannel, report_channel: discord.TextChannel, mute_role: discord.Role, staff_role: discord.Role, ticket_category: discord.CategoryChannel):
        data = self.db.get_config(ctx.guild.id)
        if data is not None:
         await ctx.response.send_message("Your server is already setup", ephemeral=True)
         return
        self.db.add_config(ctx.guild.id, log_channel.id, report_channel.id, mute_role.id, staff_role.id, ticket_category.id)
        await ctx.response.send_message("Your server has been setup", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Config(bot))
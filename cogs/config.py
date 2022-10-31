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
        mod_role = ctx.guild.get_role(data[4])
        embed.add_field(name="Log Channel", value=log_channel.mention)
        embed.add_field(name="Report Channel", value=report_channel.mention)
        embed.add_field(name="Mod Role", value=mod_role.mention)
        embed.add_field(name="Mute Role", value=mute_role.mention)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setup", description="Setup the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx, log_channel: discord.TextChannel, report_channel: discord.TextChannel, mute_role: discord.Role, mod_role: discord.Role):
        data = self.db.get_config(ctx.guild.id)
        if data is not None:
         await ctx.response.send_message("Your server is already setup", ephemeral=True)
         return
        self.db.add_config(ctx.guild.id, log_channel.id, report_channel.id, mute_role.id, mod_role.id)
        await ctx.response.send_message("Your server has been setup", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Config(bot))
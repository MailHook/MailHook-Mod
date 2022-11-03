import discord
from discord.ext import commands
from discord import app_commands
import time

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Get the bot's latency")
    async def ping(self, ctx):
        await ctx.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=True)

    @app_commands.command(name="server-info", description="Get info about the server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title="Server Info", color=discord.Color.blurple())
        embed.add_field(name="Name", value=guild.name, inline=False)
        embed.add_field(name="Owner", value=guild.owner, inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=False)
        # we want the creation time to be in a readable format using discords timestamp function and the time module like this: <t:1627380000>
        crated_at = discord.utils.format_dt(guild.created_at, style="F")
        embed.add_field(name="Created At", value=crated_at, inline=False)
        #embed.add_field(name="Created At", value=f"<t:{int(time.mktime(guild.created_at.timetuple()))}>", inline=False)
        embed.set_thumbnail(url=guild.icon.url)
        await ctx.response.send_message(embeds=[embed], ephemeral=True)

    @app_commands.command(name="user-info", description="Get info about a user")
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.user
        embed = discord.Embed(title="User Info", color=discord.Color.blurple())
        embed.add_field(name="Name", value=member.name, inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        #embed.add_field(name="Created At", value=f"<t:{int(time.mktime(member.created_at.timetuple()))}>", inline=False)
        made_time = discord.utils.format_dt(member.created_at, style="F")
        embed.add_field(name="Created At", value=made_time, inline=False)
        joined_time = discord.utils.format_dt(member.joined_at, style="F")
        embed.add_field(name="Joined At", value=joined_time, inline=False)
        #embed.add_field(name="Joined At", value=f"<t:{int(time.mktime(member.joined_at.timetuple()))}>", inline=False)
        roles = [role.mention for role in member.roles]
        if roles == []:
            roles = "None"
        embed.add_field(name="Roles", value=" ".join(roles[::-1]), inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.response.send_message(embeds=[embed], ephemeral=True)
async def setup(bot):
    await bot.add_cog(Info(bot))
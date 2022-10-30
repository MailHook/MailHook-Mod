import asyncio
import discord
import datetime
import os
from dotenv import load_dotenv

from utils.embed import custom_embed
load_dotenv()

from discord.ext import commands
from utils.bot import ModBot
from discord import app_commands
from utils.db import Database
import random
import time

def time_converter(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2
    return val * time_dict[unit]

class Mod(commands.Cog):
    def __init__(self, bot: ModBot):
            self.bot = bot
            self.db = Database()
     
    @app_commands.command(name="warn", description="Warns a user.")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        # check if the user is staff with the highest role
        if member.top_role >= ctx.user.top_role:
            return await ctx.response.send_message("You cannot warn this user.", ephemeral=True)
        if member == ctx.user:
            return await ctx.response.send_message("You cannot warn yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {member.mention}!, You have been warned in {ctx.guild.name} for {reason}, 

Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await member.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Warn\n**Date:** {time_2}"
        embed = custom_embed(title="Warn", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, member.id, ctx.user.id, reason, "warn", time_1)
        await ctx.response.send_message("Warned user.", ephemeral=True)

    @app_commands.command(name="kick", description="Kicks a user.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if member.top_role >= ctx.user.top_role:
            return await ctx.response.send_message("You cannot kick this user.", ephemeral=True)
        if member == ctx.user:
            return await ctx.response.send_message("You cannot kick yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {member.mention}!, You have been kicked in {ctx.guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await member.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Kick\n**Date:** {time_2}"
        embed = custom_embed(title="Kick", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, member.id, ctx.user.id, reason, "kick", time_1)
        await member.kick(reason=reason)
        await ctx.response.send_message("Kicked user.", ephemeral=True)

    @app_commands.command(name="ban", description="Bans a user.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if member.top_role >= ctx.user.top_role:
            return await ctx.response.send_message("You cannot ban this user.", ephemeral=True)
        if member == ctx.user:
            return await ctx.response.send_message("You cannot ban yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {member.mention}!, You have been banned in {ctx.guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await member.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Ban\n**Date:** {time_2}"
        embed = custom_embed(title="Ban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, member.id, ctx.user.id, reason, "ban", time_1)
        await member.ban(reason=reason)
        await ctx.response.send_message("Banned user.", ephemeral=True)

    @app_commands.command(name="unban", description="Unbans a user.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member_id: str, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        member = await self.bot.fetch_user(member_id)
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Unban\n**Date:** {time_2}"
        embed = custom_embed(title="Unban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, member.id, ctx.user.id, reason, "unban", time_1)
        await ctx.guild.unban(member, reason=reason)
        await ctx.response.send_message("Unbanned user.", ephemeral=True)

    @app_commands.command(name="temp-ban", description="Temporarily bans a user.")
    @commands.has_permissions(ban_members=True)
    async def temp_ban(self, ctx, member: discord.Member, time_: str, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if member.top_role >= ctx.user.top_role:
            return await ctx.response.send_message("You cannot ban this user.", ephemeral=True)
        if member == ctx.user:
            return await ctx.response.send_message("You cannot ban yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {member.mention}!, You have been banned in {ctx.guild.name} for {reason} for {time_}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await member.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Temp Ban\n**Date:** {time_2}"
        embed = custom_embed(title="Temp Ban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, member.id, ctx.user.id, reason, "temp-ban", time_1)
        await member.ban(reason=reason)
        await ctx.response.send_message("Temporarily banned user.", ephemeral=True)
        await asyncio.sleep(time_converter(time_))
        await ctx.guild.unban(member, reason="Temp ban expired.")
        txt = f"**Case:** {case_number}\n**User:** {member.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** Temp ban expired.\n**Type:** Unban"
        embed = custom_embed(title="Unban", description=txt, color=discord.Color.green())
        await channel.send(embeds=[embed])

    # case command
    @app_commands.command(name="case", description="Get a case.")
    @commands.has_permissions(manage_messages=True)
    async def case(self, ctx, case_number: int):
        case = self.db.get_case(case_number)
        if case is None:
            return await ctx.response.send_message("No case found.", ephemeral=True)
        case_number = case[0]
        user_id = case[2]
        moderator_id = case[3]
        reason = case[4]
        case_type = case[5]
        user = self.bot.get_user(user_id)
        moderator = self.bot.get_user(moderator_id)
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**User Id**: {user.id}\n**Moderator:** {moderator.mention}\n**Reason:** {reason}\n**Type:** {case_type}"
        embed = custom_embed(title="Case", description=txt, color=discord.Color.green())
        embed.set_footer(text=f"Case {case_number}", icon_url=ctx.user.avatar.url)
        await ctx.response.send_message(embeds=[embed])

    # edit-case command
    @app_commands.command(name="edit-case", description="Edit a case.")
    @commands.has_permissions(manage_messages=True)
    async def edit_case(self, ctx, case_number: int, *, reason: str):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case = self.db.get_case(case_number)
        if case is None:
            return await ctx.response.send_message("No case found.", ephemeral=True)
        self.db.edit_case(case_number, ctx.guild.id, reason)
        # send the user a dm telling them their case has been edited
        user_id = case[2]
        user = self.bot.get_user(user_id)
        try:
            txt = f"""
Your case has been edited in {ctx.guild.name} for {reason}
            
If you have any questions, please contact a staff member.

Thanks, Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        # send embed to the mod-log channel
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Edit\n**Date:** {time_2}"
        embed = custom_embed(title="Edit Case", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        await ctx.response.send_message("Edited case.", ephemeral=True)

    # remove-case command
    @app_commands.command(name="remove-case", description="Remove a case.")
    @commands.has_permissions(manage_messages=True)
    async def remove_case(self, ctx, case_number: int):
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        case = self.db.get_case(case_number)
        if case is None:
            return await ctx.response.send_message("No case found.", ephemeral=True)
        self.db.remove_case(case_number)
        # send the user a dm telling them their case has been removed
        user_id = case[2]
        user = self.bot.get_user(user_id)
        # send embed to the mod-log channel
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** Case removed.\n**Type:** Remove\n**Date:** {time_2}"
        embed = custom_embed(title="Remove Case", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        await ctx.response.send_message("Removed case.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Mod(bot))
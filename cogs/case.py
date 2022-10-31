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

class Cases(commands.Cog):
    def __init__(self, bot: ModBot):
            self.bot = bot
            self.db = Database()
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
    await bot.add_cog(Cases(bot))
import asyncio
import datetime
import random
import time
import discord
from discord import app_commands
from discord.ext import commands
from utils.db import Database
from utils.core import Moderation_core

from utils.embed import custom_embed

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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.core = Moderation_core(bot)
    
    # command group for moderation commands (slash commands)
    moderation = app_commands.Group(
        name="moderation", 
        description="Moderation commands"
    )

    # kick command (slash command)
    @moderation.command(
        name="kick",
        description="Kick a member from the server.",
    )
    @app_commands.describe(
        user="The user to kick.",
        reason="The reason for kicking the user."
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user == ctx.user:
            return await ctx.followup.send("You can't kick yourself!", ephemeral=True)
        if user == self.bot.user:
            return await ctx.ctx.followup.send("You can't kick me!", ephemeral=True)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You can't kick someone with a higher role than you!", ephemeral=True)
        if user == ctx.guild.owner:
            return await ctx.followup.send("You can't kick the server owner!", ephemeral=True)
        await self.core.kick(ctx=discord.Integration, guild=ctx.guild, user=user, mod_user=ctx.user, reason=reason, case_number=case_number)
        await ctx.followup.send("Kicked user.", ephemeral=True)

    # ban command (slash command)
    @moderation.command(
        name="ban",
        description="Ban a member from the server.",
    )
    @app_commands.describe(
        user="The user to ban.",
        reason="The reason for banning the user."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.ctx.followup.send("You cannot ban this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot ban yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been banned in {ctx.guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Ban\n**Date:** {time_2}"
        embed = custom_embed(title="Ban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "ban", time_1)
        await user.ban(reason=reason)
        await ctx.followup.send("Banned user.", ephemeral=True)

    # unban command (slash command)
    @moderation.command(
        name="unban",
        description="Unban a member from the server.",
    )
    @app_commands.describe(
        user="The user to unban.",
        reason="The reason for unbanning the user."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Unban\n**Date:** {time_2}"
        embed = custom_embed(title="Unban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "unban", time_1)
        await ctx.guild.unban(user, reason=reason)
        await ctx.followup.send("Unbanned user.", ephemeral=True)

    # mute command (slash command)
    @moderation.command(
        name="temp-ban",
        description="Temporarily ban a member from the server.",
    )
    @app_commands.describe(
        user="The user to temporarily ban.",
        reason="The reason for temporarily banning the user.",
        timer="The time to temporarily ban the user for."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def temp_ban(self, ctx, user: discord.Member, timer: str, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot ban this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot ban yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been banned in {ctx.guild.name} for {reason} for {timer}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Temp Ban\n**Date:** {time_2}"
        embed = custom_embed(title="Temp Ban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "temp-ban", time_1)
        await user.ban(reason=reason)
        await ctx.followup.send("Temporarily banned user.", ephemeral=True)
        await asyncio.sleep(time_converter(timer))
        await ctx.guild.unban(user, reason="Temp ban expired.")
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** Temp ban expired.\n**Type:** Unban"
        embed = custom_embed(title="Unban", description=txt, color=discord.Color.green())
        await channel.send(embeds=[embed])

    @moderation.command(
        name="warn",
        description="Warn a member in the server.",
    )
    @app_commands.describe(
        user="The user to warn.",
        reason="The reason for warning the user."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        # check if the user is staff with the highest role
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot warn this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot warn yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been warned in {ctx.guild.name} for {reason}, 

Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Warn\n**Date:** {time_2}"
        embed = custom_embed(title="Warn", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "warn", time_1)
        await ctx.followup.send(f"Warned {user.name}.")

    @moderation.command(
        name="temp-warn",
        description="Temporarily warn a member in the server.",
    )
    @app_commands.describe(
        user="The user to temporarily warn.",
        reason="The reason for temporarily warning the user.",
        timer="The time to temporarily warn the user for."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temp_warn(self, ctx, user: discord.Member, timer: str, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot warn this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot wanr yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been warned in {ctx.guild.name} for {reason} for {timer}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Temp Warn\n**Date:** {time_2}"
        embed = custom_embed(title="Temp Warn", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "temp-warn", time_1)
        await ctx.followup.send(f"Temporarily warned {user.name}.")
        await asyncio.sleep(time_converter(timer))
        # delete the case and send a message in the mod log
        self.db.delete_case(case_number)
        txt = f"**Case:** **Delete**\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** Temp warn expired.\n**Type:** Unwarn"
        embed = custom_embed(title="Unwarn", description=txt, color=discord.Color.green())
        await channel.send(embeds=[embed])

    @moderation.command(
        name="clear",
        description="Clear messages in a channel.",
    )
    @app_commands.describe(
        amount="The amount of messages to clear."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
        if amount > 100:
            return await ctx.response.send_message("You can only clear 100 messages at a time.", ephemeral=True)
        await ctx.channel.purge(limit=amount)
        ctx.response.is_done()

    @moderation.command(
        name="mute",
        description="Mute a member in the server.",
    )
    @app_commands.describe(
        user="The user to mute.",
        reason="The reason for muting the user.",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot mute this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot mute yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been muted in {ctx.guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Mute\n**Date:** {time_2}"
        embed = custom_embed(title="Mute", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "mute", time_1)
        await ctx.followup.send("Muted user.", ephemeral=True)
        await user.add_roles(discord.Object(self.db.get_config(ctx.guild.id)[3]))

    @moderation.command(
        name="unmute",
        description="Unmute a member in the server.",
    )
    @app_commands.describe(
        user="The user to unmute.",
        reason="The reason for unmuting the user.",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, ctx, user: discord.Member, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot unmute this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot unmute yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been unmuted in {ctx.guild.name} for {reason}.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Unmute\n**Date:** {time_2}"
        embed = custom_embed(title="Unmute", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "unmute", time_1)
        await ctx.followup.send("Unmuted user.", ephemeral=True)
        await user.remove_roles(discord.Object(self.db.get_config(ctx.guild.id)[3]))

    @moderation.command(
        name="temp-mute",
        description="Temporarily mute a member in the server.",
    )
    @app_commands.describe(
        user="The user to mute.",
        time_muted="The time to mute the user for.",
        reason="The reason for muting the user.",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temp_mute(self, ctx, user: discord.Member, time_muted: str, *, reason: str = "No reason provided."):
        await ctx.response.defer()
        if self.db.get_config(ctx.guild.id) is None:
            return await ctx.followup.send("Your server is not setup please run `/setup`", ephemeral=True)
        case_number = random.randint(100000, 999999)
        if user.top_role >= ctx.user.top_role:
            return await ctx.followup.send("You cannot mute this user.", ephemeral=True)
        if user == ctx.user:
            return await ctx.followup.send("You cannot mute yourself.", ephemeral=True)
        try:
            txt = f"""
Hello, {user.mention}!, You have been muted in {ctx.guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
            await user.send(txt)
        except:
            pass
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {ctx.user.mention}\n**Reason:** {reason}\n**Type:** Temp Mute\n**Date:** {time_2}\n**Time:** {time_muted}"
        embed = custom_embed(title="Temp Mute", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(ctx.guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, ctx.guild.id, user.id, ctx.user.id, reason, "temp-mute", time_1)
        await ctx.followup.send("Temporarily muted user.", ephemeral=True)
        await user.add_roles(discord.Object(self.db.get_config(ctx.guild.id)[3]))
        await asyncio.sleep(time_converter(time_muted))
        await user.remove_roles(discord.Object(self.db.get_config(ctx.guild.id)[3]))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
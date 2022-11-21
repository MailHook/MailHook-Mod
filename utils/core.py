"""
 Copyright (c) 2022 DeveloperJosh

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """

import asyncio
import datetime
import time
import discord
from typing import List, Optional, Dict

from utils.embed import custom_embed
from .bot import ModBot
from .db import Database

no_xp_list = []
custom_level_up_messages = []
guild_level_up_messages = {}

class Level_core():
    def __init__(self, bot: ModBot):
        self.bot = bot
        self.db = Database()
        self.weekend_xp = 5
        self.xp_per_message = 1
        self.max_level = 100
        self.max_xp = 100

    async def level_up(self, message: discord.Message, is_weekend: bool = False):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.content.startswith(self.bot.command_prefix):
            return

        guild_id = message.guild.id
        user_id = message.author.id
        xp = self.db.get_level(guild_id, user_id)
        if xp is None:
            self.db.add_level(guild_id, user_id, 1, 1)
        else:
            level = xp[2]
            xp = xp[3]
            # if it is the weekend, then give 2x xp
            if is_weekend:
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
                 await self.level_role_reward(message, level=level)
                 #await message.channel.send(f"{message.author.mention} has leveled up to level {level}!", delete_after=10)
                 msg = await self.find_message(message, level=level)
                 await message.channel.send(msg, delete_after=10)

            self.db.update_level(guild_id, user_id, level, xp)
            # no_xp_list.append(user_id)
           # await asyncio.sleep(5)
            # no_xp_list.remove(user_id)

    async def set_message(self, ctx: discord.Integration, message: str):
        # if message has the words [level] or [xp] then replace it with the {level} or {xp}
        # now lets add the custom level up messages 
        if "[level]" in message:
            message = message.replace("[level]", "{level}")
        if "[xp]" in message:
            message = message.replace("[xp]", "{xp}")
        # add the message to the list and add `` at the start and end
        #custom_level_up_messages.append(f"f'{message}'")
        # add guild id and message to the database
        guild_level_up_messages[ctx.guild.id] = message
        await ctx.response.send_message(f"Custom level up message set to ``{message}``")

    async def find_message(self, ctx: discord.Message, level: int):
        if ctx.guild.id in guild_level_up_messages:
            message = guild_level_up_messages[ctx.guild.id]
            if message is not None:
                message = message.replace("{level}", str(level))
                message = message.replace("{xp}", str(self.max_xp))
                return message
        return f"{ctx.author.mention} has leveled up to level {level}!"

    async def level_role_reward(self, ctx: discord.Message, level: int):
        data = self.db.get_role_by_level(ctx.guild.id, level)
        if data is None:
            return
        for i in data:
            role = discord.utils.get(ctx.guild.roles, id=data[1])
            if role is None:
                print(f"Role with id {level} not found")
                continue
            if role in ctx.author.roles:
                print(f"{ctx.author} already has role {role}")
                continue
            await ctx.author.add_roles(role)

    async def xp_bar(self, xp: int):
        max_bar = 10
        bar = ""
        for i in range(max_bar):
            if xp >= self.max_xp / max_bar * (i + 1):
                bar += "█"
            else:
                bar += "░"
        return bar

    async def level_bar(self, level: int):
        max_bar = 10
        bar = ""
        for i in range(max_bar):
            if level >= self.max_level / max_bar * (i + 1):
                bar += "█"
            else:
                bar += "░"
        return bar

    async def leaderboard(self, ctx: discord.Integration):
        data = self.db.get_levels(ctx.guild.id)
        data = sorted(data, key=lambda x: x[2], reverse=True)
        embed = discord.Embed(
            title="Leaderboard",
            description="The top 10 people on the leaderboard",
            color=ctx.user.color
        )
        embed.set_footer(text=f"Requested by {ctx.user}", icon_url=ctx.user.avatar.url)
        embed.timestamp = datetime.datetime.now()
        for i in range(len(data)):
            if i == 10:
                break
            user = await self.bot.fetch_user(data[i][1])
            if user is None:
                continue
            if user.bot:
                continue
            embed.add_field(
                name=f"{i + 1}. {user}",
                value=f"Level: {data[i][2]}\nXP: {data[i][3]}",
                inline=False
            )
        await ctx.response.send_message(embed=embed)

    async def profile(self, ctx: discord.Integration, user: discord.User = None):
        if user is None:
            user = ctx.user
        data = self.db.get_level(ctx.guild.id, user.id)
        if data is None:
            await ctx.response.send_message("User has no xp")
            return
        embed = discord.Embed(
            title=f"{user}'s profile",
            description=f"Level: {data[2]}\nXP: {data[3]}\nXP Bar: {await self.xp_bar(data[3])}\nLevel Bar: {await self.level_bar(data[2])}",
            color=ctx.user.color
        )
        embed.set_footer(text=f"Requested by {ctx.user}", icon_url=ctx.user.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await ctx.response.send_message(embed=embed, ephemeral=True)

class Moderation_core():
    def __init__(self, bot: ModBot) -> None:
        self.db = Database()
        self.bot = bot

    async def kick(self, ctx: discord.Integration, guild: discord.Guild, user: discord.Member, mod_user: discord.Member, reason: str = "No reason provided", case_number: int=None):
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {mod_user.mention}\n**Reason:** {reason}\n**Type:** Kick\n**Date:** {time_2}"
        embed = custom_embed(title="Kick", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, guild.id, user.id, mod_user.id, reason, "kick", time_1)
        reason_for_kick = f"Kicked by {mod_user} for {reason}"
        txt = f"""
Hello, {user.mention}!, You have been kicked in {guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
        try:
           await user.send(txt)
        except:
            raise Exception("User has DMs disabled")
        await user.kick(reason=reason_for_kick)

    async def ban(self, ctx: discord.Integration, guild: discord.Guild, user: discord.Member, mod_user: discord.Member, reason: str = "No reason provided", case_number: int=None):
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user.mention}\n**Moderator:** {mod_user.mention}\n**Reason:** {reason}\n**Type:** Ban\n**Date:** {time_2}"
        embed = custom_embed(title="Ban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, guild.id, user.id, mod_user.id, reason, "ban", time_1)
        reason_for_ban = f"Banned by {mod_user} for {reason}"
        txt = f"""
Hello, {user.mention}!, You have been banned in {guild.name} for {reason}, Please read the rules and try to follow them next time.

Case Number: {case_number}
            """
        try:
           await user.send(txt)
        except:
            raise Exception("User has DMs disabled")
        await user.ban(reason=reason_for_ban)

    async def unban(self, ctx: discord.Integration, guild: discord.Guild, user_id: int, mod_user: discord.Member, reason: str = "No reason provided", case_number: int=None):
        time_1 = datetime.datetime.now()
        time_2 = f"<t:{int(time.mktime(time_1.timetuple()))}>"
        txt = f"**Case:** {case_number}\n**User:** {user_id}\n**Moderator:** {mod_user.mention}\n**Reason:** {reason}\n**Type:** Unban\n**Date:** {time_2}"
        embed = custom_embed(title="Unban", description=txt, color=discord.Color.green())
        channel = self.bot.get_channel(self.db.get_config(guild.id)[1])
        await channel.send(embeds=[embed])
        self.db.add_case(case_number, guild.id, user_id, mod_user.id, reason, "unban", time_1)
        reason_for_unban = f"Unbanned by {mod_user} for {reason}"
        await guild.unban(discord.Object(id=user_id), reason=reason_for_unban)
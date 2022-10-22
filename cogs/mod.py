import discord
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from discord.ext import commands
from utils.bot import ModBot
from discord import app_commands
from utils.db import Database
import random

class Mod(commands.Cog):
    def __init__(self, bot: ModBot):
            self.bot = bot
            self.db = Database("logs.db")
     
    @app_commands.command(name="add-staff", description="Adds the staff role to the user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def staff(self, ctx, user: discord.Member):
        try:
         server_data = self.db.get_guild(ctx.guild.id)
         if server_data is None:
            await ctx.response.send_message("This server is not configured yet. Please run `/setup` to configure the bot.")
            return
         staff_role = discord.utils.get(ctx.guild.roles, id=server_data[4])
         staff_traniee_role = discord.utils.get(ctx.guild.roles, id=1033324272434810890)
         await user.add_roles(staff_role)
         await user.add_roles(staff_traniee_role)
         channel = self.bot.get_channel(server_data[2])
         embed = discord.Embed(title="Staff Role Added", description=f"You have been added to the staff team, If you need any help please dm a Mod.", color=0x00ff00)
         await channel.send(content=f"{user.mention}", embed=embed)
         await ctx.response.send_message("Staff role added to user.", ephemeral=True)
        except Exception as e:
         await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="remove-staff", description="Removes the staff role from the user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_staff(self, ctx, user: discord.Member):
       try:
        server_data = self.db.get_guild(ctx.guild.id)
        if server_data is None:
            await ctx.response.send_message("This server is not configured yet. Please run `/setup` to configure the bot.")
            return
        staff_role = discord.utils.get(ctx.guild.roles, id=server_data[4])
        staff_traniee_role = discord.utils.get(ctx.guild.roles, id=1033324272434810890)
        await user.remove_roles(staff_role)
        await user.remove_roles(staff_traniee_role)
        embed = discord.Embed(title="You have been removed from the staff team!", description="You have been removed from the staff team of the {} discord server. If you have any questions, please ask a staff member.".format(ctx.guild.name), color=0x00ff00)
        new_dm = await user.create_dm()
        await new_dm.send(embed=embed)
        await ctx.response.send_message("Removed the staff role from the {}.".format(user.display_name))
       except Exception as e:
        await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="mute", description="Mutes the user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, *, reason: str):
        try:
            server_data = self.db.get_guild(ctx.guild.id)
            if server_data is None:
                await ctx.response.send_message("You need to set up the server first. Use `/setup` to set up the server.", ephemeral=True)
                return
            muted_role = discord.utils.get(ctx.guild.roles, id=server_data[3])
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "mute", timestamp)
            await user.add_roles(muted_role)
            try:
             embed = discord.Embed(title="You have been muted!", description="You have been muted in the {} discord server. If you have any questions, please dm MailHook".format(ctx.guild.name), color=0x00ff00)
             new_dm = await user.create_dm()
             await new_dm.send(embed=embed)
            except:
                pass
            # send the embed to the channel
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Mute
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Mute", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(server_data[2])
            await channel.send(embed=embed)

            await ctx.response.send_message("Muted {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="unmute", description="Unmutes the user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, ctx, user: discord.Member):
        try:
            server_data = self.db.get_guild(ctx.guild.id)
            if server_data is None:
                await ctx.response.send_message("You need to set up the server first. Use `/setup` to set up the server.", ephemeral=True)
                return
            muted_role = discord.utils.get(ctx.guild.roles, id=server_data[3])
            await user.remove_roles(muted_role)
            try:
             embed = discord.Embed(title="You have been unmuted!", description="You have been unmuted in the {} discord server. If you have any questions, please dm MailHook".format(ctx.guild.name), color=0x00ff00)
             new_dm = await user.create_dm()
             await new_dm.send(embed=embed)
            except:
                pass
            txt = f"""
            **Case ID:** None
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** None
            """
            embed = discord.Embed(title="Unmute", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(server_data[2])
            await channel.send(embed=embed)
            await ctx.response.send_message("Unmuted {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="ban", description="Bans the user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str):
        try:
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            server_data = self.db.get_guild(ctx.guild.id)
            if server_data is None:
                await ctx.response.send_message("You need to set up the server first. Use `/setup` to set up the server.", ephemeral=True)
                return
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "ban", timestamp)
            try:
             embed = discord.Embed(title="You have been banned!", description="You have been banned from the {} discord server.".format(ctx.guild.name), color=0x00ff00)
             new_dm = await user.create_dm()
             await new_dm.send(embed=embed)
            except:
                pass
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Ban
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Ban", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(server_data[2])
            await channel.send(embed=embed)
            await user.ban(reason=reason)
            await ctx.response.send_message("Banned {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="kick", description="Kicks the user.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str):
        try:
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            server_data = self.db.get_guild(ctx.guild.id)
            if server_data is None:
                await ctx.response.send_message("You need to set up the server first. Use `/setup` to set up the server.", ephemeral=True)
                return
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "kick", timestamp)
            try:
             embed = discord.Embed(title="You have been kicked!", description="You have been kicked from the {} discord server.".format(ctx.guild.name), color=0x00ff00)
             new_dm = await user.create_dm()
             await new_dm.send(embed=embed)
            except:
                pass
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Kick
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Kick", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(server_data[2])
            await channel.send(embed=embed)
            await user.kick(reason=reason)
            await ctx.response.send_message("Kicked {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="warn", description="Warns the user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        try:
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            server_data = self.db.get_guild(ctx.guild.id)
            if server_data is None:
                await ctx.response.send_message("You need to set up the server first. Use `/setup` to set up the server.", ephemeral=True)
                return
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "warn", timestamp)
            try:
             embed = discord.Embed(title="You have been warned!", description="You have been warned in the {} discord server.".format(ctx.guild.name), color=0x00ff00)
             new_dm = await user.create_dm()
             await new_dm.send(embed=embed)
            except:
                pass
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Warn
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Warn", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(server_data[2])
            await channel.send(embed=embed)
            await ctx.response.send_message("Warned {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="quarantine", description="Quarantines a staff member.")
    @app_commands.checks.has_permissions(administrator=True)
    async def quarantine(self, ctx, user: discord.Member, *, reason: str=None):
        try:
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "quarantine", timestamp)
            new_role = discord.utils.get(ctx.guild.roles, id=1028485135177359460)
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Quarantine
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Quarantine", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(1033438416987242529)
            # remove all other roles
            for role in user.roles:
                if role != ctx.guild.default_role:
                    await user.remove_roles(role)
            await user.add_roles(new_role)
            await channel.send(embed=embed)
            await ctx.response.send_message("Quarantined {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="unquarantine", description="Unquarantines a staff member.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unquarantine(self, ctx, user: discord.Member, *, reason: str=None):
        try:
            # make a random id for the case
            case_id = random.randint(100000, 999999)
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            print(timestamp)
            self.db.add_report(case_id, ctx.user.id, user.id, ctx.user.id, reason, "unquarantine", timestamp)
            new_role = discord.utils.get(ctx.guild.roles, id=1028485135177359460)
            txt = f"""
            **Case ID:** {case_id}
            **User:** {user.mention}
            **Moderator:** {ctx.user}
            **Reason:** {reason}
            **Type:** Unquarantine
            **Date:** {timestamp}
            To edit this case, use `/edit-report {case_id} <reason>`
            """
            embed = discord.Embed(title="Unquarantine", description=txt, color=0x00ff00)
            channel = self.bot.get_channel(1033438416987242529)
            await user.remove_roles(new_role)
            # add member and staff roles
            member_role = discord.utils.get(ctx.guild.roles, id=1025834769541505256)
            staff_role = discord.utils.get(ctx.guild.roles, id=1033325362421174284)
            await user.add_roles(member_role, staff_role)
            await channel.send(embed=embed)
            await ctx.response.send_message("Unquarantined {}.".format(user.display_name), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="clear", description="deletes a certain amount of messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        try:
            await ctx.channel.purge(limit=amount)
            await ctx.response.send_message("Deleted {} messages.".format(amount), ephemeral=True)
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="edit-report", description="Edits a case.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def edit_report(self, ctx, case_id: int, *, reason: str):
        try:
            report = self.db.get_report(case_id)
            if report is None:
                await ctx.response.send_message("Case {} does not exist.".format(case_id))
                return
            self.db.edit_report(case_id, reason)
            await ctx.response.send_message("Edited case {}.".format(case_id))
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="delete-report", description="Deletes a case.")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_report(self, ctx, case_id: int):
        try:
            report = self.db.get_report(case_id)
            if report is None:
                await ctx.response.send_message("Case {} does not exist.".format(case_id))
                return
            await ctx.response.send_message("Deleted case {}.".format(case_id))
        except Exception as e:
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="get-report", description="Gets a case.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def get_report(self, ctx, case_id: int):
        try:
            report = self.db.get_report(case_id)
            if report is None:
                await ctx.response.send_message("Case {} does not exist.".format(case_id))
                return
            txt = f"""
            **Case ID:** {report[0]}
            **User:** <@{report[2]}>
            **Moderator:** <@{report[1]}>
            **Reason:** {report[4]}
            **Type:** {report[5]}
            **Date:** {report[6]}
            To edit this case, use `/edit-report {report[0]} <reason>`
            """
            embed = discord.Embed(title="Case", description=txt, color=0x00ff00)
            await ctx.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="get-reports", description="Gets all cases.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def get_reports(self, ctx):
        try:
            reports = self.db.get_reports(ctx.guild.id)
            if reports is None:
                await ctx.response.send_message("No cases exist.")
                return
            txt = ""
            for report in reports:
                txt += f"""
                **Case ID:** {report[0]}
                **User:** <@{report[2]}>
                **Moderator:** <@{report[1]}>
                **Reason:** {report[4]}
                **Type:** {report[5]}
                **Date:** {report[6]}
                To edit this case, use `/edit-report {report[0]} <reason>`
                """
            embed = discord.Embed(title="Cases", description=txt, color=0x00ff00)
            await ctx.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            await ctx.response.send_message("An error occured: {}".format(e))

    @app_commands.command(name="help", description="Shows this message.")
    async def help(self, ctx):
        embed = discord.Embed(title="Help", description="Here are all the commands you can use.", color=0x00ff00)
        mod_commands = """
        `/ban <user> <reason>` - Bans a user.
        `/unban <user> <reason>` - Unbans a user.
        `/kick <user> <reason>` - Kicks a user.
        `/mute <user> <reason>` - Mutes a user.
        `/unmute <user> <reason>` - Unmutes a user.
        `/warn <user> <reason>` - Warns a user.
        `/quarantine <user> <reason>` - Quarantines a user.
        `/unquarantine <user> <reason>` - Unquarantines a user.
        `/clear <amount>` - Deletes a certain amount of messages.
        `/edit-report <case_id> <reason>` - Edits a case.
        `/delete-report <case_id>` - Deletes a case.
        `/get-report <case_id>` - Gets a case.
        `/get-reports` - Gets all cases.
        `/add-staff <user>` - Adds a user to the staff role.
        `/remove-staff <user>` - Removes a user from the staff role.
        """
        config_commands = """
        `/config` - Shows the current config.
        `/editconfig` - Edits the config.
        `/setup` - Sets up the bot.
        """
        embed.add_field(name="Mod", value=mod_commands, inline=False)
        embed.add_field(name="Config", value=config_commands, inline=False)
        await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Mod(bot))
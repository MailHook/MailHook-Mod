import discord
import datetime
from discord.ext import commands
from discord import app_commands
from utils.bot import ModBot
from utils.db import Database
from utils.embed import error_embed


# NOTE: dont know how to implement buttons. pls teach sensei.

class Ticket(commands.Cog):
    def __init__(self, bot: ModBot):
        self.bot = bot
        self.db = Database()
    support = app_commands.Group(name="support", description="Support commands")

    @support.command(name="create", description="Create a support ticket")
    async def create(self, ctx):
        """This is not ready for use"""
        data = self.db.get_config(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
            return
        category = discord.utils.get(ctx.guild.categories, id=data[5])
        if category is None:
            await ctx.response.send_message("The ticket category is not set please run `/editconfig ticket_category`", ephemeral=True)
            return
        role = discord.utils.get(ctx.guild.roles, id=data[4])
        if role is None:
            await ctx.response.send_message("The staff role is not set please run `/editconfig staff_role`", ephemeral=True)
            return
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.user: discord.PermissionOverwrite(read_messages=True),
            # add staff role
            role: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await ctx.guild.create_text_channel(f"ticket-{ctx.user.id}", category=category, overwrites=overwrites)
        self.db.create_ticket(guild_id=ctx.guild.id, channel_id=channel.id, user_id=ctx.user.id, staff_id=10)

        msg = f"{role.mention} a new ticket has been created by {ctx.user.mention}!"
        embed = discord.Embed(
            title="Ticket Created",
            description=f"Ticket ID: {ctx.user.id}",
            color=ctx.user.color
        )
        embed.set_footer(text=f"Ticket by: {ctx.user.name}", icon_url=ctx.user.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await channel.send(content = msg, embed=embed)

        await ctx.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

    # close the ticket
    @support.command(name="close", description="Close a ticket")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def close(self, ctx):
        data = self.db.get_config(ctx.guild.id)
        ticket_data = self.db.get_ticket(ctx.guild.id, ctx.channel.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
            return
        category = discord.utils.get(ctx.guild.categories, id=data[5])
        if category is None:
            await ctx.response.send_message("The ticket category is not set please run `/editconfig ticket_category`", ephemeral=True)
            return
        if ticket_data is None:
            await ctx.response.send_message("This is not a ticket channel", ephemeral=True)
            return
        self.db.close_ticket(guild_id=ctx.guild.id, channel_id=ctx.channel.id)
        await ctx.channel.delete()

    # assign a ticket to a staff member
    @support.command(name="assign", description="Assign a ticket to a staff member (only staff can use this)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def assign(self, ctx, staff: discord.Member):
        """This is not ready for use"""
        data = self.db.get_ticket(ctx.guild.id, ctx.channel.id)
        if data is None:
            await ctx.response.send_message("That is not a ticket!", ephemeral=True)
            return
        if data[3] == 10:
            self.db.assign_ticket(ctx.guild.id, ctx.channel.id, staff.id)
            await ctx.response.send_message(f"User has been assigened", ephemeral=True)
            channel = self.bot.get_channel(ctx.channel.id)
            await channel.send(f"Ticket assigned to {staff.mention}")
        else:
            # reassign the ticket
            self.db.assign_ticket(ctx.guild.id, ctx.channel.id, staff.id)
            await ctx.response.send_message(f"User has been assigened", ephemeral=True)
            channel = self.bot.get_channel(ctx.channel.id)
            await channel.send(f"Ticket reassigned to {staff.mention}")
# eror handling for support commands
    @assign.error
    async def support_error(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command")) # type: ignore
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time")) # type: ignore
        else:
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

    @create.error
    async def support_error_CREATE(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command"))
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

    @close.error
    async def support_error_CLOSE(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", error))
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

async def setup(bot):
    await bot.add_cog(Ticket(bot))
import discord
import datetime
from discord.ext import commands
from discord import app_commands
from utils.bot import ModBot
from utils.db import Database
from utils.embed import error_embed
from utils.buttons import TicketButton

# NOTE: dont know how to implement buttons. pls teach sensei.

class Ticket(commands.Cog):
    def __init__(self, bot: ModBot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        # add buttons
        self.bot.add_view(TicketButton())

    support = app_commands.Group(name="support", description="Support commands")

    @support.command(name="create", description="Create a support ticket")
    async def create(self, ctx):
        """This is not ready for use"""
        data = self.db.ticket_config(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/support setup`", ephemeral=True)
            return
        category = discord.utils.get(ctx.guild.categories, id=data[1])
        if category is None:
            await ctx.response.send_message("The ticket category is not set please run `/support editconfig category`", ephemeral=True)
            return
        role = discord.utils.get(ctx.guild.roles, id=data[2])
        if role is None:
            await ctx.response.send_message("The staff role is not set please run `/support editconfig staff_role`", ephemeral=True)
            return
        does_it = self.db.ticket_exists(ctx.guild.id, ctx.user.id)
        if does_it:
            channel = discord.utils.get(ctx.guild.channels, id=does_it[1])
            # check if the channel is deleted
            if channel is None:
                # if the channel is deleted then delete the ticket from the database
                self.db.close_ticket(ctx.guild.id, does_it[1])
                # make a new ticket
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
                  description=f"{data[3]}",
                  color=ctx.user.color
                )
                embed.set_footer(text=f"Ticket by: {ctx.user.name}", icon_url=ctx.user.avatar.url)
                embed.timestamp = datetime.datetime.now()
                await channel.send(content = msg, embed=embed, view=TicketButton())
                await ctx.response.send_message(f"Your ticket has been created {channel.mention}", ephemeral=True)
                return
            await ctx.response.send_message("You have a ticket open", ephemeral=True)
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
            description=f"{data[3]}",
            color=ctx.user.color
        )
        embed.set_footer(text=f"Ticket by: {ctx.user.name}", icon_url=ctx.user.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await channel.send(content = msg, embed=embed, view=TicketButton())

        await ctx.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

    # close the ticket
    @support.command(name="close", description="Close a ticket")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def close(self, ctx):
        data = self.db.ticket_config(ctx.guild.id)
        ticket_data = self.db.get_ticket(ctx.guild.id, ctx.channel.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
            return
        category = discord.utils.get(ctx.guild.categories, id=data[1])
        if category is None:
            await ctx.response.send_message("The ticket category is not set please run `/support editconfig category`", ephemeral=True)
            return
        if ticket_data is None:
            await ctx.response.send_message("This is not a ticket channel", ephemeral=True)
            return
        # before closing the ticket send a message to the user
        close_message = "It seems like your ticket has been closed. If you have any more questions please create a new ticket."
        user = discord.utils.get(ctx.guild.members, id=ticket_data[2])
        await user.send(content=close_message)
        try:
         self.db.close_ticket(guild_id=ctx.guild.id, channel_id=ctx.channel.id)
        except:
            await ctx.response.send_message("This is not a ticket channel", ephemeral=True)
            return
        await ctx.channel.delete()

    # assign a ticket to a staff member
    @support.command(name="assign", description="Assign a ticket to a staff member (This commmand is optional)")
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

    @support.command(name="config", description="View the ticket config")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(self, ctx):
        data = self.db.ticket_config(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/support setup`", ephemeral=True)
            return
        role = discord.utils.get(ctx.guild.roles, id=data[2])
        category = discord.utils.get(ctx.guild.categories, id=data[1])
        embed = discord.Embed(
            title="Ticket Config",
            description=f"Ticket category: {category.name}\nStaff role: {role.mention}\nTicket message: {data[3]}",
            color=ctx.user.color
        )
        embed.set_footer(text=f"Ticket config by: {ctx.user.name}", icon_url=ctx.user.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await ctx.response.send_message(embed=embed)

    @support.command(name="editconfig", description="Edit the ticket config")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(category="Tickets will be made in this category ", staff_role="The role to ping when a ticket is created", ticket_message="The message to send when a ticket is created")
    async def editconfig(self, ctx, category: discord.CategoryChannel = None, staff_role: discord.Role = None, ticket_message: str = None):
        if category is None and staff_role is None and ticket_message is None:
            await ctx.response.send_message("You need to provide a category, staff role or ticket message", ephemeral=True)
            return
        data = self.db.ticket_config(ctx.guild.id)
        if data is None:
            await ctx.response.send_message("Your server is not setup please run `/support setup`", ephemeral=True)
            return
        if category is not None:
            self.db.edit_ticket_config(ctx.guild.id, category.id, data[2], data[3])
        if staff_role is not None:
            self.db.edit_ticket_config(ctx.guild.id, data[1], staff_role.id, data[3])
        if ticket_message is not None:
            self.db.edit_ticket_config(ctx.guild.id, data[1], data[2], ticket_message)
        await ctx.response.send_message("Config updated", ephemeral=True)

    
    @support.command(name="setup", description="Setup the ticket system")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        # make sure the server is not setup and then setup the server
        data = self.db.get_config(ctx.guild.id)
        if data is None:
            # not setup
            await ctx.response.send_message("Your server is not setup please run `/setup`", ephemeral=True)
            return
        ticket_data = self.db.ticket_config(ctx.guild.id)
        if ticket_data is None:
            # make a category and a set the staff role from data
            category = await ctx.guild.create_category("Tickets")
            # setp perm for category
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.user: discord.PermissionOverwrite(read_messages=True),
                # add staff role
                ctx.guild.get_role(data[4]): discord.PermissionOverwrite(read_messages=True)
            }
            await category.edit(overwrites=overwrites)
            print(data[4])
            start_msg = "A staff member will be with you shortly, In the mean time please describe your issue as best as you can."
            self.db.create_ticket_config(guild_id=ctx.guild.id, category_id=category.id, role_id=data[4], start_message=start_msg)
            await ctx.response.send_message("Ticket system setup", ephemeral=True)
        else:
            await ctx.response.send_message("Ticket system is already setup", ephemeral=True)

    @assign.error
    async def support_error(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command")) # type: ignore
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time")) # type: ignore
        else:
            print(error)
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

    @create.error
    async def support_error_CREATE(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You do not have permission to use this command"))
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            print(error)
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

    @close.error
    async def support_error_CLOSE(self, ctx: discord.Integration, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await ctx.response.send_message(embed=error_embed("Error:x:", error))
        elif isinstance(error, discord.app_commands.errors.CommandLimitReached):
            await ctx.response.send_message(embed=error_embed("Error:x:", "You can only edit one setting at a time"))
        else:
            print(error)
            await ctx.response.send_message(embed=error_embed("Error:x:", "An error has occured"))

async def setup(bot):
    await bot.add_cog(Ticket(bot))
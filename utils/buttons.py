import discord
from .db import Database 

# NOTE: This is all buttons are. You can try to make the buttons for the ticket avi
# EXAMPLE: for a button to show up in the ticket message do this: await channel.send(embed=embed, view=Button)
class Button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Button 1", style=discord.ButtonStyle.blurple, row=1, emoji="👍", custom_id="button1")
    async def button_1(self, i: discord.Interaction, b: discord.ui.Button):
        i.response.send_message("This is a button", ephemeral=True)

    @discord.ui.button(label="Button 2", style=discord.ButtonStyle.danger, row=1, emoji="👎", custom_id="button2")
    async def button_2(self, i: discord.Interaction, b: discord.ui.Button):
        i.response.send_message("This is a button", ephemeral=True)

class ConfirmButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.yes = False

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, row=1, emoji="✅", custom_id="yes")
    async def yes(self, i: discord.Interaction, b: discord.ui.Button):
        self.yes = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, row=1, emoji="❌", custom_id="no")
    async def no(self, i: discord.Interaction, b: discord.ui.Button):
        self.yes = False
        await i.response.edit_message(content="Cancelled", view=None)
        self.stop()

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        #self.yes = False
        self.db = Database()

    # add callback so the ticket owner can only close the ticket
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, row=1, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, i: discord.Interaction, b: discord.ui.Button):
        txt = "Are you sure you want to close this ticket?"
        view = ConfirmButton()
        await i.response.send_message(txt, view=view, ephemeral=True)
        await view.wait()
        # if the user clicked yes then close the ticket if not send a message saying the ticket is not closed
        if view.yes is True:
            print("Closing ticket")
            self.db.close_ticket(guild_id=i.guild.id, channel_id=i.channel.id)
            await i.channel.delete()
        else:
            # edit the message to say cancelled
            return


    async def interaction_check(self, interaction: discord.Interaction):
        # check if the person who clicked the button is the ticket owner or a mod
        data = self.db.get_ticket(interaction.guild.id, interaction.channel.id)
        user_id = data[2]
        if interaction.user.id == user_id or interaction.user.guild_permissions.manage_channels:
            return True
        else:
            await interaction.response.send_message("You are not the ticket owner or a mod", ephemeral=True)
            return False
import discord

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
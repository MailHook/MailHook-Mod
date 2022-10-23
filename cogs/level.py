import asyncio
import datetime
from click import command
import discord
from discord.ext import commands, tasks
from utils.db import Database

no_xp_list = []
level_masters = [733536002563637298, 280464234972839936]

def is_level_master():
 async def predicate(ctx: commands.Context):
    if ctx.author.id in level_masters:
        return True
    elif ctx.author.guild_permissions.administrator:
        return True
    else:
        return False
 return commands.check(predicate)


class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("levels.db")
        self.is_weekend = False
        ############################
        self.weekend_xp = 5
        self.xp_per_message = 1
        ############################
        self.max_level = 100
        self.max_xp = 100

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.content.startswith(self.bot.command_prefix):
            return

        guild_id = message.guild.id
        user_id = message.author.id
        xp = self.db.show_xp(guild_id, user_id)
        if xp is None:
            self.db.add_level(guild_id, user_id, 1, 1)
        else:
            level = xp[2]
            xp = xp[3]
            # if it is the weekend, then give 2x xp
            if self.is_weekend:
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
                 await message.channel.send(f"{message.author.mention} has leveled up to level {level}!", delete_after=10)
            self.db.update_xp(guild_id, user_id, level, xp)
            # add user to no_xp_list for 2 seconds so they don't get xp for spamming
            no_xp_list.append(user_id)
            await asyncio.sleep(2)
            no_xp_list.remove(user_id)

    # this is a task that runs everyone one day
    @tasks.loop(hours=12)
    async def check_weekend(self):
        now = datetime.datetime.now()
        if now.weekday() == 5 or now.weekday() == 6:
            self.is_weekend = True
            print("It is the weekend!")
        else:
            self.is_weekend = False
            print("It is not the weekend!")

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.check_weekend.start()

    @commands.hybrid_command()
    async def level(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        xp = self.db.show_xp(ctx.guild.id, member.id)
        if xp is None:
            await ctx.send("This user has no xp")
        else:
            level = xp[2]
            xp = xp[3]
            await ctx.send(f"{member.name} is level {level} with {xp} xp")

    @commands.hybrid_command()
    async def leaderboard(self, ctx):
        levels = self.db.show_all_levels(ctx.guild.id)
        if levels is None:
            await ctx.send("There are no levels in this server")
        else:
            levels = sorted(levels, key=lambda x: x[2], reverse=True)
            embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
            for i in range(len(levels)):
                #embed.add_field(name=f"{i+1}. {self.bot.get_user(levels[i][1])}", value=f"Level: {levels[i][2]} XP: {levels[i][3]}", inline=False)
                # show the highest level in the server and the lowest level in the server
                if i == 0:
                    highest_level = levels[i][2]
                if i == len(levels) - 1:
                    lowest_level = levels[i][2]
                embed.add_field(name=f"{i+1}. {self.bot.get_user(levels[i][1])}", value=f"Level: {levels[i][2]}", inline=False)
            embed.set_footer(text=f"Highest level: {highest_level} Lowest level: {lowest_level}")
            await ctx.send(embed=embed)


    @commands.hybrid_command()
    @commands.has_role(1033556803872624671)
    async def set_level(self, ctx, member: discord.Member, level: int):
        if level > self.max_level:
            await ctx.send("This level is too high")
        else:
            self.db.update_level(ctx.guild.id, member.id, level)
            await ctx.send(f"{member.name} is now level {level}")

    @commands.hybrid_command()
    @commands.has_role(1033556803872624671)
    async def resetxp(self, ctx, member: discord.Member):
        self.db.update_xp(ctx.guild.id, member.id, 1, 0)
        await ctx.send("Done!")

    @commands.hybrid_command(name="startdoublexp")
    #@commands.has_role(1033556803872624671)
    @is_level_master()
    async def startdoublexp(self, ctx):
        self.is_weekend = True
        await ctx.send("Done!")
    
async def setup(bot):
    await bot.add_cog(Level(bot))
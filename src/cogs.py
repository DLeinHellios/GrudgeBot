# Command cogs for GrudgeBot

import discord, random
from discord.ext import commands
from src import data, embedder

class Information(commands.Cog):
    '''Commands for display information'''
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def games(self, ctx):
        '''Displays all supported games and their abbreviations'''
        msg = embedder.format_game_args(data.query_game_args())
        await ctx.send(embed=msg)


    @commands.command()
    async def info(self, ctx, game):
        '''Displays game info and links, requires a game abbreviation'''
        gameData = data.query_games(game.lower())
        if gameData != None:
            msg = embedder.format_games(data.query_games(game.lower()))
            await ctx.send(embed=msg)
        else:
            await ctx.send('Sorry, I don\'t know that game. Please check available games with the "!games" command.')



class Taunt(commands.Cog):
    '''Commands to talk shit'''
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def taunt(self, ctx):
        '''Sends a random taunt'''
        await ctx.send(data.random_taunt())


    @commands.command(name="add-taunt", pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def add_new_taunt(self, ctx, *, taunt):
        '''(Mod/Admin) Adds a new taunt'''
        if data.add_taunt(str(ctx.message.author), taunt):
            await ctx.send('I\'ve added the taunt "{}" - it had better be funny.'.format(taunt))
        else:
            await ctx.send('That one\'s in there already, stupid.')


    @commands.command(name="no-taunts", pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def remove_all_taunts(self, ctx):
        '''(Mod/Admin) Clears taunt list'''
        data.clear_taunts()
        await ctx.send("I've gone ahead and taken out the trash")



class Randomizer(commands.Cog):
    '''Commands for randomization utilities'''
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def flip(self, ctx):
        '''Flips a coin, heads or tails'''
        await ctx.send("{} flips **{}**".format(ctx.author.mention, random.choice(["heads","tails"])))


    @commands.command()
    async def roll(self, ctx, max):
        '''Rolls a random number, 1-max'''
        try:
            max = int(max)
            roll = random.randint(1, max)
            await ctx.send("{} rolls **{}**".format(ctx.author.mention, roll))

        except:
            await ctx.send("I need a maximum number for that")

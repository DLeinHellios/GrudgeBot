# Command cogs for GrudgeBot

import discord, random
from discord.ext import commands, tasks
from src import data, embedder, twitch

class Information(commands.Cog):
    '''Commands for display information'''
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def games(self, ctx):
        '''Displays all supported games and their abbreviations'''
        gameList = data.query_game_list()

        if gameList != []:
            msg = embedder.format_game_list(gameList)
            await ctx.send(embed=msg)
        else:
            await ctx.send("Sorry, I don't seem to know any games at the moment")


    @commands.command()
    async def info(self, ctx, game):
        '''Displays game info and links, requires a game abbreviation'''
        gameData = data.query_game(game.lower())

        if gameData != None:
            msg = embedder.format_game_info(gameData)
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


    @commands.command(name="random-select")
    async def random_seles(self, ctx, game):
        '''Random character select'''
        characterData = data.query_characters(game.lower())

        if characterData != None:
            await ctx.send("{} plays **{}**".format(ctx.author.mention, random.choice(characterData)))
        else:
            await ctx.send('Sorry, I don\'t know that game. Please check available games with the "!games" command.')



class Stream(commands.Cog):
    '''Commands for managing stream notifications'''
    def __init__(self, bot):
        self.bot = bot


    @tasks.loop(seconds=300)
    async def notifications(self, channel):
        '''Gives notifications for live streams, only supports Twitch'''
        watchlist = data.query_twitch_logins() # List of Twitch login names

        if watchlist != []: # Streams are being watched, check for notifications
            notify = twitch.check_streams(watchlist)

            if notify != []: # Notifications are pending, get user details
                users = [x['user_login'] for x in notify] # Get detailed channel info
                users = twitch.get_user_data(users)

                for user in users: # Send notifications for each live stream
                    msg = embedder.format_stream_notification(user)
                    await channel.send(embed=msg)


    @commands.command(name="add-twitch", pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def add_twitch_streamer(self, ctx, id):
        '''(Mod/Admin) Adds a Twitch streamer to watchlist'''
        msg = data.add_stream(id, "Twitch")
        await ctx.send(msg)


    @commands.command(name="clear-twitch", pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def remove_twitch_streamer(self, ctx):
        '''(Mod/Admin) Clears Twitch watchlist'''
        data.clear_streams("Twitch")
        twitch.live = []
        await ctx.send("Stream watchlist for Twitch has been cleared")


    @commands.command(name="streams")
    async def get_streams(self, ctx):
        '''Displays currently followed streams'''
        logins = data.query_twitch_logins()

        if logins != []:
            twitchData = sorted(twitch.get_user_data(logins), key=lambda item: item['display_name'].lower())
            msg = embedder.format_streams(twitchData)
            await ctx.send(embed=msg)

        else:
            await ctx.send("No streams are on my radar. That's kinda boring.")

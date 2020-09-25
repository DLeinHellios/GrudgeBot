#!/usr/bin/env python3

# Copyright 2020 DLeinHellios
# Logo by ZN
# Provided under the Apache License 2.0

import discord, os, sys, sqlite3, random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Data:
    def __init__(self):
        try:
            self.db = sqlite3.connect('data.db')
            self.c = self.db.cursor()
        except:
            print("Cannot open database! Exiting...")
            sys.exit()


    def query_game_args(self):
        '''Returns all game names and their corresponding commands'''
        self.c.execute('SELECT name, arg FROM games ORDER BY name')

        return self.c.fetchall()


    def query_games(self, game):
        '''Returns all data about a specified game'''
        self.c.execute('SELECT * FROM games WHERE arg=?', (game,))
        gameData = self.c.fetchall()

        if gameData != []:
            return gameData[0]


    def random_taunt(self):
        '''Returns a random taunt from database'''
        self.c.execute('SELECT body FROM taunts')
        taunts = self.c.fetchall()

        if len(taunts) == 0:
            return "I got nothin..."

        return random.choice(taunts)[0]


    def add_taunt(self, author, taunt):
        '''Saves a new taunt to to the database, returns True is taunt is added'''
        # Check existing
        self.c.execute('SELECT body from taunts')
        taunts = self.c.fetchall()

        for t in taunts:
            if taunt == t[0]:
                return False

        # Add taunt
        self.c.execute('INSERT INTO taunts ("author", "body") VALUES (?, ?)', (author, taunt))
        self.db.commit()

        return True


    def clear_taunts(self):
        '''Deletes all taunts'''
        self.c.execute('DELETE FROM taunts')
        self.db.commit()



class Embedder:
    def format_game_args(self, commands):
        '''Accepts a list of tuples containg game names and commands, returns formatted embed'''
        embed = discord.Embed(title="**Supported Games**", colour=discord.Colour(0xef4535))

        for command in commands:
            embed.add_field(name=command[0], value="`" + command[1] + "`", inline=True)

        return embed


    def format_games(self, gameData):
        '''Returns formatted embed for game data'''
        if gameData != None:

            # Main field
            title = gameData[1]
            description = ''

            for i in [gameData[3], gameData[4], gameData[5]]:
                if i != None:
                    description += i + " | "

            if description != '':
                description = description[:-3]
                embed = discord.Embed(title=title, colour=discord.Colour(0xf7b722), description=description)

            else:
                embed = discord.Embed(title=title, colour=discord.Colour(0xf7b722))

            # Links field
            links = ''
            if gameData[7] != None:
                links += '[Character Data](' + gameData[7] + ') | '
            if gameData[6] != None:
                links += '[Move List](' + gameData[6] + ') | '

            if links != '':
                links = links[:-3]
                embed.add_field(name="Links", value=links, inline=False)

            # Return formatted embed object
            return embed


#=======================================================

bot = commands.Bot(command_prefix="!", description="GrudgeBot - I know some fighting game stuff")
embedder = Embedder()
data = Data()


@bot.event
async def on_ready():
    '''Login message'''
    print('Successfully logged in as:')
    print("User: " + bot.user.name)
    print("ID: " + str(bot.user.id))
    print('==========================')


@bot.command()
async def games(ctx):
    '''Displays all supported games and their abbreviations'''
    msg = embedder.format_game_args(data.query_game_args())
    await ctx.send(embed=msg)


@bot.command()
async def info(ctx, game):
    '''Displays game info and links, requires a game abbreviation (i.e., !game <abbr>)'''
    gameData = data.query_games(game)
    if gameData != None:
        msg = embedder.format_games(data.query_games(game))
        await ctx.send(embed=msg)
    else:
        await ctx.send('Sorry, I don\'t know that game. Please check available games with the "!games" command.')


@bot.command()
async def taunt(ctx):
    '''Sends a random taunt'''
    await ctx.send(data.random_taunt())


@bot.command(name="addtaunt", pass_context=True)
@commands.has_permissions(ban_members=True)
async def add_new_taunt(ctx, *, taunt):
    '''Adds a new taunt, usable by moderators and administrators only'''
    if data.add_taunt(str(ctx.message.author), taunt):
        await ctx.send('I\'ve added the taunt "{}" - it had better be funny.'.format(taunt))
    else:
        await ctx.send('That one\'s in there already, stupid.')


@bot.command(name="notaunts", pass_context=True)
@commands.has_permissions(ban_members=True)
async def remove_all_taunts(ctx):
    '''Removes all taunts in one big go. Only usable by mods and admins'''
    data.clear_taunts()
    await ctx.send("I've gone ahead and taken out the trash")


@bot.event
async def on_command_error(ctx, error):
    '''Handles command errors'''
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I dont know that command.")

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You are not permitted to use that command.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide argument(s) for that command.")

    else:
        raise error


if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])

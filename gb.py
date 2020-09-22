#!/usr/bin/env python3

# Copyright 2020 DLeinHellios
# Logo by ZN
# Provided under the Apache License 2.0

import discord, os, sys, sqlite3
from dotenv import load_dotenv

load_dotenv()


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



class Embedder:
    def format_game_args(self, commands):
        '''Accepts a list of tuples containg game names and commands, returns formatted embed'''
        embed = discord.Embed(title="**Supported Games**", colour=discord.Colour(0xef4535))

        for command in commands:
            embed.add_field(name=command[0], value="`" + command[1] + "`", inline=False)

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
            if gameData[6] != None:
                links += gameData[6] + " | "

            if links != '':
                links = links[:-3]
                embed.add_field(name="Links", value="[Movelist](" + gameData[6] + ")", inline=False)

            # Return formatted embed object
            return embed



class Client(discord.Client):
    async def on_ready(self):
        print('Successfully logged in as {0.user}'.format(client))

    async def on_message(self, message):
        # Ignore self messages
        if message.author == client.user:
            return

        # Send embed of available game args
        if message.content.startswith('!games'):
            msg = embedder.format_game_args(data.query_game_args())
            await message.channel.send(embed=msg)

        # Send embed of game information
        if message.content.startswith('!info'):
            # Read args
            game = message.content.split(" ", 1)
            if len(game) > 1:
                game = game[1]
            else:
                # No game specified
                return

            # Send message
            gameData = data.query_games(game)
            if gameData != None:
                msg = embedder.format_games(data.query_games(game))
                await message.channel.send(embed=msg)
            else:
                await message.channel.send('Sorry, I don\'t know that game. Please check available games with the "!games" command.')



embedder = Embedder()
data = Data()

if __name__ == "__main__":
    client = Client()
    client.run(os.environ['DISCORD_TOKEN'])

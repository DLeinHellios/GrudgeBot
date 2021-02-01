# Utility classes for GrudgeBot

import discord, sys, sqlite3, random

class Data:
    '''Handles sqlite transactions'''
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
    '''Formats Discord embed objects'''
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

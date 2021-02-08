# Utility classes for GrudgeBot

import discord, os, sys, sqlite3, random, requests


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


    def add_stream(self, id, service):
        '''Adds a streamer to database'''
        twitchStreams = self.query_twitch_logins()

        if service == "Twitch":
            # Twitch channels
            if id not in twitchStreams:
                self.c.execute('INSERT INTO streams ("stream_id", "service") VALUES (?,?)', (id, service))
                self.db.commit()
                msg = "Twitch streamer **{}** has been added".format(id)

            elif id in twitchStreams:
                msg = "Twitch steamer **{}** is already followed".format(id)

            return msg


    def clear_streams(self, service):
        '''Removes all streamers of a particular service from watchlist'''
        self.c.execute('DELETE FROM streams WHERE (service=?)', ("Twitch",))
        self.db.commit()

        return "Stream watchlist for {} has been cleared".format(service)


    def query_twitch_logins(self):
        '''Returns a list of all Twitch login names on from database'''
        self.c.execute('SELECT stream_id FROM streams WHERE service="Twitch" ORDER BY stream_id')
        twitchLogins = self.c.fetchall()

        # Remove from tuple
        twitchLogins = [x[0] for x in twitchLogins]

        return twitchLogins


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
        embed = discord.Embed(title="Supported Games", colour=discord.Colour(0xef4535))
        embed.set_thumbnail(url="https://dleinhellios.com/gm/logo_thumb.png")

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


    def format_streams(self, streamData):
        '''Returns formatted embed for cuttently followed streams, only Twitch for now'''
        embed = discord.Embed(title="Followed Streams", colour=discord.Colour(14378506))
        embed.set_thumbnail(url="https://dleinhellios.com/gm/logo_thumb.png")

        for stream in streamData:
            name = stream["display_name"] + " -  https://twitch.tv/" + stream["login"]

            if stream["description"] != "":
                value = stream["description"]
            else:
                value = "Streams on Twitch"

            embed.add_field(name=name, value=value, inline=False)

        return embed


    def format_stream_notification(self, userData):
        '''Creates embed for Twitch notification'''
        title = "{} is live!".format(userData["display_name"])
        url = "https://twitch.tv/" + userData["login"]
        description = userData["description"] + "\nWatch now at " + url
        embed = discord.Embed(title=title, description=description, url=url, colour=discord.Colour(14378506))
        embed.set_thumbnail(url=userData["profile_image_url"])

        return embed


class Twitch:
    '''Handles calls to Twitch API'''
    def __init__(self, clientID, secret):
        self.client = clientID
        self.secret = secret
        self.active = True # Kills Twitch integration on auth issues

        self.token = self.get_token() # Get initial token
        #print(self.token) # Get a token to re-use for debugging
        self.live = [] # List of already-live streams


    def get_token(self):
        '''Returns valid OAuth token for API calls'''
        url = 'https://id.twitch.tv/oauth2/token'

        params = {
            'client_id': self.client,
            'client_secret': self.secret,
            'grant_type': 'client_credentials'
        }

        response = requests.post(url=url, params=params)

        if response.status_code != 200:
            # Unable to get token, fail gracefully
            self.active = False
            return None, None

        else:
            response = response.json()
            return response['access_token']


    def get_stream_data(self, logins):
        '''Accepts list of Twitch login names, returns live stream information'''
        url = 'https://api.twitch.tv/helix/streams'
        headers = {
            'client-id': self.client,
            'Authorization': "Bearer " + self.token
        }

        params = {
            'user_login': logins
        }

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 401:
            # Token rejected, get new one
            print('Token Rejected - Trying to get a new one')
            self.token = self.get_token()

            if self.active:
                # New token was successful
                response = requests.get(url=url, headers=headers, params=params)

            else:
                print("Token Error - Unable to check streams")
                return []

        response = response.json()
        return response['data']


    def check_streams(self, logins):
        '''Checks all running streams and returns notification data'''
        notify = []

        if self.active:
            liveStreams = self.get_stream_data(logins)

            keepLive = []
            for stream in liveStreams:
                if stream['user_login'] not in self.live:
                    # Add to notification list
                    notify.append(stream)
                    self.live.append(stream['user_login'])

                keepLive.append(stream['user_login'])

            # Clean up recently-ended streams
            checkLive = list(self.live)
            for streamer in checkLive:
                if streamer not in keepLive:
                    self.live.remove(streamer)

        return notify


    def get_user_data(self, logins):
        '''Returns Twitch user data for provided list of login names'''
        url = 'https://api.twitch.tv/helix/users'
        headers = {
            'client-id': self.client,
            'Authorization': "Bearer " + self.token
        }

        params = {
            'login': logins
        }

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 401:
            # Token rejected, get new one
            print('Token Rejected - Trying to get a new one')
            self.token = self.get_token()

            if self.active:
                # New token was successful
                response = requests.get(url=url, headers=headers, params=params)

            else:
                print("Token Error - Unable to get user data")
                return []

        response = response.json()
        return response['data']

# Utility classes for GrudgeBot

import discord, os, sys, sqlite3, datetime, random, requests


class Data:
    '''Handles sqlite transactions'''
    def __init__(self):
        try:
            self.db = sqlite3.connect('data.db')
            self.c = self.db.cursor()

            self.gamedataURL = "https://dleinhellios.com/gm/game_data.json"

        except:
            print("Cannot open database! Have you ran db_util.py? Exiting...")
            sys.exit()


    def query_game_list(self):
        '''Returns all game names and their corresponding command arguments'''
        self.c.execute('SELECT name, argument FROM games ORDER BY name')

        return self.c.fetchall()


    def query_game(self, game):
        '''Returns all data about a specified game argument'''
        self.c.execute('SELECT * FROM games WHERE argument=?', (game,))
        gameData = self.c.fetchall()

        if gameData != []:
            return gameData[0]


    def query_characters(self, game):
        '''Returns character names as a list for the specified game argument'''
        self.c.execute('SELECT characters FROM games WHERE argument=?', (game,))
        characters = self.c.fetchall()
        # Convert from list of tuples containing character list string
        characters = characters[0][0].split(", ")

        if characters != []:
            return characters


    def add_stream(self, id, service):
        '''Adds a streamer to database'''
        if service == "Twitch":
            twitchStreams = self.query_twitch_logins()

            if id in twitchStreams:
                msg = "Twitch steamer **{}** is already followed".format(id)

            else:
                self.c.execute('INSERT INTO streams ("stream_id", "service") VALUES (?,?)', (id, service))
                self.db.commit()
                msg = "Twitch streamer **{}** has been added".format(id)

            return msg


    def remove_stream(self, id, service):
        '''Removes a stream from database'''
        if service == "Twitch":
            twitchStreams = self.query_twitch_logins()

            if id in twitchStreams:
                self.c.execute('DELETE FROM streams WHERE stream_id=?', (id,))
                self.db.commit()
                msg = "Twitch streamer **{}** has been removed".format(id)

            else:
                msg = "Twitch streamer **{}** not found. Names are case sensitive!".format(id)

            return msg


    def clear_streams(self, service):
        '''Removes all streamers of a particular service from watchlist'''
        self.c.execute('DELETE FROM streams WHERE (service=?)', (service,))
        self.db.commit()


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


    def query_champ(self, game):
        '''Returns champ info for specified game, returns None if no game or champ exists'''
        # Get prerequisite info
        info = self.query_game(game)

        # Check for champ
        if info == None:
            champ = None

        else:
            # Fetch champ entry
            self.c.execute('SELECT * FROM champs WHERE game=? AND current=1', (info[3],))
            champ = self.c.fetchall()

            # Format return
            if champ != []:
                champ = (info[1], champ[0][2], champ[0][3])

            else:
                champ = None

        return champ


    def set_champ(self, game, champ):
        '''Sets current champion of specified game, accepts game argument abbreviation'''
        # Get prerequisite info
        info = self.query_game(game)
        today = datetime.date.today()

        if info == None: # Game not found
            return None

        # Mark others as non-current
        self.c.execute('UPDATE champs SET current=0 WHERE game=?', (info[3],))

        # Create new champ entry
        self.c.execute('INSERT INTO champs ("game", "player", "crown_date", "current") VALUES (?,?,?,1)', (info[3], champ, today))
        self.db.commit()

        return info[1]


    def update_games(self):
        '''Downloads game data json from web and updates games table in database'''
        try:
            # Download data json
            headers = {"User-Agent":'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
            response = requests.get(url=self.gamedataURL, headers=headers).json()

            # Clean up old game data first
            self.c.execute("DELETE FROM games")

            # Import data into database
            for name, field in response.items():
                links = []

                for link, url in field['links'].items():
                    links.append("{}|{}".format(link,url))

                links = ",".join(links)

                values = (
                    name,
                    field["full_name"],
                    field["argument"],
                    field["platform"],
                    field["developer"],
                    field["release_year"],
                    field["thumbnail"],
                    links,
                    ", ".join(field["characters"]),
                )

                self.c.execute('''
                    INSERT INTO games (
                        "name",
                        "full_name",
                        "argument",
                        "platform",
                        "developer",
                        "release_year",
                        "thumbnail",
                        "links",
                        "characters"
                    )

                    VALUES (?,?,?,?,?,?,?,?,?)''', (values))

            self.db.commit()
            # Return true for success
            return True

        except:
            # Failed to update game data
            return False



class Embedder:
    '''Formats Discord embed objects'''
    def game_list(self, commands):
        '''Accepts a list of tuples containg game names and commands, returns formatted embed'''
        embed = discord.Embed(title="Supported Games", colour=discord.Colour(0xef4535))
        embed.set_thumbnail(url="https://dleinhellios.com/gm/logo_thumb.png")

        for command in commands:
            embed.add_field(name=command[0], value="`" + command[1] + "`", inline=True)

        return embed


    def game_links(self, links):
        '''Returns formatting link string from database field'''
        linkList = links.split(",")

        linkString = ''

        for link in linkList:
            splitLink = link.split("|")

            linkString += " [{}]({}) -".format(*splitLink)

        linkString = linkString[:-2] # Remove last "-"

        return linkString


    def game_info(self, gameData):
        '''Returns formatted embed for game data'''
        # Main field
        title = gameData[2] # full_name
        description = ''

        # Description
        for i in [gameData[4], gameData[5], str(gameData[6])]:
            if i != None:
                description += i + " | "

        if description != '': # Description needs to be non-blank string!
            description = description[:-3]
        else:
            description = "No description given"

        embed = discord.Embed(title=title, colour=discord.Colour(0xf7b722), description=description)
        embed.set_thumbnail(url=gameData[7])

        # Characters field
        if gameData[9] != None:
            embed.add_field(name="Characters", value=gameData[9], inline=False)

        # Links Field
        if gameData[8] != None:
            linkText = self.game_links(gameData[8])
            embed.add_field(name="Links", value=linkText, inline=False)

        return embed


    def streamers(self, streamData):
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


    def stream_notification(self, userData):
        '''Creates embed for Twitch notification'''
        title = "{} is live!".format(userData["display_name"])
        url = "https://twitch.tv/" + userData["login"]
        description = userData["description"] + "\nWatch now at " + url
        embed = discord.Embed(title=title, description=description, url=url, colour=discord.Colour(14378506))
        embed.set_thumbnail(url=userData["profile_image_url"])

        return embed


    def about(self):
        '''Creates embed about Dial'''
        description = "GrudgeBot is developed by [Dial](https://dleinhellios.com) to be a useful and fun addition to this server. We like fighting games around here, so most functionality pertains to that. GrudgeBot is free, open-source software. Wanna see the code? [Check out GrudgeBot on GitHub!](https://github.com/DLeinHellios/GrudgeBot)"
        embed=discord.Embed(title="About the Developer", description=description, color=0x22c1dd)
        embed.set_thumbnail(url="https://dleinhellios.com/img/dial.png")

        links = "[DLeinHellios.com](https://dleinhellios.com) | [Dial's GitHub](https://github.com/DLeinHellios) | [Dial's Twitter](https://twitter.com/DLeinHellios)"
        embed.add_field(name="More Links", value=links)

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

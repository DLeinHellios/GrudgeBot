# GrudgeBot

A bot for the GrudgeMatch Discord server, does fighting game stuff

## Usage

| Command          | Args                           | Permissions                    | Description                                     |
| ---------------- | ------------------------------ | ------------------------------ | ----------------------------------------------- |
| !games           | None                           | Anyone                         | Lists supports games for command arguments      |
| !info            | Game (see !games)              | Anyone                         | Displays game info and links for specified game |
| !taunt           | None                           | Anyone                         | Sends a random taunt                            |
| !add-taunt       | Taunt text                     | Can Ban                        | Add a new taunt to the pool                     |
| !no-taunts       | None                           | Can Ban                        | Removes all taunts                              |
| !streams         | None                           | Anyone                         | Displays streamer watchlist                     |
| !add-twitch      | Twitch name                    | Can Ban                        | Adds a Twitch streamer to notification list     |
| !clear-twitch    | None                           | Can Ban                        | Clears Twitch streamer watchlist                |


## Requirements
[Discord Token](https://discordapp.com/developers/applications/)

[Twitch Client ID and Secret](https://dev.twitch.tv/)

See .env.example

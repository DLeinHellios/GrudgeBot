# GrudgeBot

A bot for the GrudgeMatch Discord server. Does some fun fighting game stuff.

## Commands

| Command          | Module                         | Arguments                      | Permissions                    | Description                                     |
| ---------------- | ------------------------------ | ------------------------------ | -------------------------------|------------------------------------------------ |
| !games           | Information                    | None                           | Anyone                         | Lists known games and their abbreviations       |
| !info            | Information                    | Game (see !games)              | Anyone                         | Displays game info and links for specified game |
| !glossary        | Information                    | Search Term                    | Anyone                         | Searches Infil's fighting game glossary         |
| !about           | Information                    | None                           | Anyone                         | Displays developer information                  |
| !random-select   | Randomizer                     | Game (see !games)              | Anyone                         | Acts a random character select for games        |
| !roll            | Randomizer                     | Max Roll                       | Anyone                         | Rolls a random number 1-max (inclusive)         |
| !flip            | Randomizer                     | None                           | Anyone                         | Flips a 2-sided coin heads/tails                |
| !taunt           | Taunt                          | None                           | Anyone                         | Sends a random taunt                            |
| !add-taunt       | Taunt                          | Taunt text                     | Can Ban                        | Add a new taunt to the pool                     |
| !no-taunts       | Taunt                          | None                           | Can Ban                        | Removes all taunts                              |
| !champ           | Champion                       | Game (see !games)              | Anyone                         | Displays the current champ of specified game    |
| !set-champ       | Champion                       | Game, Member @mention          | Can Ban                        | Sets game champ, accepts player name or mention |
| !streams         | Stream                         | None                           | Anyone                         | Displays streamer watchlist                     |
| !add-twitch      | Stream                         | Twitch login name              | Can Ban                        | Adds a Twitch streamer to notification list     |
| !clear-twitch    | Stream                         | None                           | Can Ban                        | Clears Twitch streamer watchlist                |


## Requirements
[Discord Token](https://discordapp.com/developers/applications/)

[Twitch Client ID and Secret](https://dev.twitch.tv/)

See .env.example

<p align="center">
    <img src=img/logo.png?raw=true >
</p>

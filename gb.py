#!/usr/bin/env python3

# GrudgeBot - Discord bot for GrudgeMatch server
# Copyright 2020 DLeinHellios
# Logo by ZN
# Provided under the Apache License 2.0

import discord, os
from src import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))
bot = commands.Bot(command_prefix="!", description="GrudgeBot - I know some fighting game stuff")

bot.add_cog(Information(bot))
bot.add_cog(Taunt(bot))
bot.add_cog(Randomizer(bot))
bot.add_cog(Stream(bot))
bot.add_cog(Champion(bot))


@bot.event
async def on_ready():
    '''Handles bot login'''
    print('Successfully logged in as:')
    print("User: " + bot.user.name)
    print("ID: " + str(bot.user.id))
    print('==========================')

    # Start Tasks
    Stream.notifications.start(Stream, bot.get_channel(int(os.environ['STREAM_CHANNEL'])))
    print("Starting stream notifications...")


@bot.event
async def on_command_error(ctx, error):
    '''Handles command errors'''
    if isinstance(error, commands.CommandNotFound):
        #await ctx.send("Sorry, I dont know that command.") # Enable unknown command message
        pass

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You are not permitted to use that command.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide argument(s) for that command.")

    else:
        raise error


if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])

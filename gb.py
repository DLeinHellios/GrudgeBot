#!/usr/bin/env python3

# Copyright 2020 DLeinHellios
# Logo by ZN
# Provided under the Apache License 2.0

import discord, os
from dotenv import load_dotenv
from src import *

load_dotenv()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
bot = commands.Bot(command_prefix="!", description="GrudgeBot - I know some fighting game stuff")


@bot.event
async def on_ready():
    '''Prints bot info on login'''
    print('Successfully logged in as:')
    print("User: " + bot.user.name)
    print("ID: " + str(bot.user.id))
    print('==========================')


@bot.event
async def on_command_error(ctx, error):
    '''Handles command errors'''
    if isinstance(error, commands.CommandNotFound):
        # await ctx.send("Sorry, I dont know that command.") # Enable unknown command message
        pass

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You are not permitted to use that command.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide argument(s) for that command.")

    else:
        raise error
        

bot.add_cog(Information(bot))
bot.add_cog(Taunt(bot))
bot.add_cog(Randomizer(bot))


if __name__ == "__main__":
    # Run bot
    bot.run(os.environ['DISCORD_TOKEN'])

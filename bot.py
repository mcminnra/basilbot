#!/usr/bin/env python3

import os

import discord
from discord.ext import commands
import giphy_client
from google.cloud import secretmanager
import numpy as np

# Get API Keys from GCP Secrets
PROJECT_ID = os.environ['PROJECT_ID']
secrets = secretmanager.SecretManagerServiceClient()
DISCORD_BOT_TOKEN = secrets.access_secret_version(f"projects/{PROJECT_ID}/secrets/DISCORD_BOT_TOKEN/versions/1").payload.data.decode("utf-8")
GIPHY_KEY = secrets.access_secret_version(f"projects/{PROJECT_ID}/secrets/GIPHY_KEY/versions/1").payload.data.decode("utf-8")

# Init Bot
bot = commands.Bot(command_prefix='!')
giphy = giphy_client.DefaultApi()

# === Events ===
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    
# === Commands ===
@bot.command(
    brief='Shows a random gif',
    usage='<Search Query>\n!random fat mac',
    description='Shows a random gif loosely based on the search query.')
async def random(ctx, *args):
    print('[Command] !random')
    q = ' '.join([str(x) for x in args])
    response = giphy.gifs_search_get(GIPHY_KEY, q, limit=1, lang='en')
    image_url = response.data[0].url
    await ctx.send(f'{image_url}')

    
@random.error
async def random_error(ctx, error):
    cmd = '!random'
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Error: {cmd} command is missing an argument - See \'!help {cmd}\' for details.')


@bot.command(
    brief='Plays "Odds Are" against Basil',
    usage='<Odds (Number from 1 to 100)> <Your Guess (Number from 1 to Odds)>\n!odds 10 4',
    description='Plays "Odds Are" against Basil')
async def odds(ctx, odds, guess):
    print('[Command] !odds')

    odds, guess = int(odds), int(guess)
    msg = f'Odds: 1 to {odds}, Your Guess: {guess}\n'
    
    if odds > 100 or odds < 1:
        msg += 'Error: Your odds have to be betwen 1 and 100!'
    elif guess > odds or guess < 1:
        msg += f'Error: Your guess has to be between 1 and the odds ({odds})!'
    else:
        basil_guess = np.random.randint(low=1, high=odds, size=1)[0]
        msg += f'Basil\'s guess is.... **{basil_guess}**!\n\n'

        if guess == basil_guess:
            msg += 'They match! Now you gotta do it.'
        else:
            msg += 'They don\'t match! You don\'t have to do it.'
    
    await ctx.send(msg)


@odds.error
async def odds_error(ctx, error):
    cmd = '!odds'
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Error: {cmd} command is missing an argument - See \'!help {cmd}\' for details.')


# Start Bot
bot.run(DISCORD_BOT_TOKEN)

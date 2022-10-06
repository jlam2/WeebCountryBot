import os
from discord.ext import commands

botID = os.getenv('DISCORD_BOT_ID2')

client = commands.Bot(command_prefix='!')

@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("I'm not ready yet!(command on cooldown)")
        await ctx.send("https://tenor.com/view/astolfo-angry-mad-anime-astolfo-is-angry-gif-17672544") 
    elif isinstance(error, commands.errors.ExpectedClosingQuoteError):
        await ctx.send("Bitch, don't forget your closing quotes.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Missing inputs")
    elif isinstance(error, commands.errors.MemberNotFound):
        await ctx.send("Server member not found")
    else:
        await ctx.send("Something went wrong senpai")
        raise error

for file in os.listdir("cogs folder"):
    if file.endswith('.py'):
        client.load_extension(f'cogs folder.{file[:-3]}')

client.run(botID)
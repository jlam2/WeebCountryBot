import random
from discord.ext import commands
import discord

class Miscellaneous(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(brief = 'The very best.')
    @commands.cooldown(10, 30,commands.cooldowns.BucketType.user)
    async def ping(self,ctx):
        await ctx.send("pong")
    
    @commands.command(brief = 'The second best.', usage = '| optional*<roll_ceiling>')
    async def roll(self,ctx,input = '6'):
        try:
            value = abs(int(input))
            number = random.randint(1,  value if value > 0 else 1 )
        except ValueError:
            value = sum([ord(c) for c in input])
            number = random.randint(1, value if value > 0 else 1)
        await ctx.send(number)

    @commands.command(brief = 'When your having a bad day.', usage = '| <@user_mention>')
    @commands.cooldown(5, 30,commands.cooldowns.BucketType.user)
    async def insult(self,ctx,person:discord.Member):
        repertoire=["{0}, You're a god damn whore.", 
                    "{0}, You fuckin cumquat.", 
                    "Nah dude, fuck you {0}.", 
                    "{0}.......Cuck.", 
                    "Hey {0}, [racial slur]", 
                    "I'll choke you {0}.",
                    "God regrets you {0}.",
                    "Nobody loves you {0}."]     
                     
        msg = random.choice(repertoire).format(person.mention)
        await ctx.send(msg)

    @commands.command(brief = "When there's beef.")
    async def cointoss(self,ctx):
        coinoptions = ["Heads, bitch", "Tails, bitch"]
        await ctx.send(random.choice(coinoptions))

    @commands.command(brief = "I dunno man...")
    async def orderweed(self,ctx):
        await ctx.send("Weed machine's broke")
    
    @commands.command(brief = 'CONVENIENT!!! *CHECKS LAST 100 MSGS*', usage = '| <#ofMsgs> optional*<bot_mention>')
    @commands.cooldown(3, 300,commands.cooldowns.BucketType.user)
    async def clear(self,ctx,amount = 1, member:discord.Member = None):
        author = member if member == self.client.user else ctx.author 
                
        msgs = []
        async for m in ctx.channel.history(limit = 100):
            if len(msgs) == amount + 1: 
                break
            if m.author == author: 
                msgs.append(m)
        await ctx.message.delete()
        await ctx.channel.delete_messages(msgs)
        
    @clear.error
    async def clear_handler(self, ctx, error):
        if isinstance(error,commands.errors.BadArgument):
            await ctx.send("I take numbers holmes.")
            
def setup(client):
    client.add_cog(Miscellaneous(client))
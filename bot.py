

def start():
    import json
    from discord.ext import commands
    from settings import BOT_ID, ADMIN_ID, COMMAND_PREFIX
    import utility

    bot = commands.Bot(command_prefix=COMMAND_PREFIX, self_bot=True)
    bot.load_extension("cog")


    async def reload(ctx):
        bot.unload_extension("cog")
        bot.load_extension("cog")
        await ctx.send("RELOADED")


    @bot.event
    async def on_message(message):
        if message.content == ">reload" and message.author.id == ADMIN_ID:
            await reload(message.channel)


    # Start bot
    with open("token.json") as file:
        try: 
            bot.run(json.load(file)["token"]) 
        except:
            print("TODO: Renew token automatically")

    return bot

import json, datetime
from discord.ext import commands
from settings import BOT_ID, COMMAND_PREFIX, CONTAINER_CHAR
import utility

bot = commands.Bot(command_prefix=COMMAND_PREFIX, self_bot=True)
bot.load_extension("cog")

_func = None
_args = None


async def reload(ctx):
    bot.unload_extension("cog")
    bot.load_extension("cog")
    await ctx.send("RELOADED")


@bot.event
async def on_message(message):
    if message.content == f"{COMMAND_PREFIX} reload" and utility.is_admin(message.author.id):
        await reload(message.channel)


@bot.event
async def on_ready():
    print(CONTAINER_CHAR * 30)
    print("LOGGED IN TO ACCOUNT: ")
    print(f"user: {bot.user.name}#{bot.user.discriminator}")
    print(f"id:   {bot.user.id}")
    print(CONTAINER_CHAR * 30)
    await _func(*_args)


def start(func, *args):
    global _func
    global _args
    _func = func
    _args = args
    # Start bot
    with open("token.json") as file:
        try: 
            bot.run(json.load(file)["token"]) 
        except:
            print("TODO: Renew token automatically")


async def stop():
    if not bot.is_closed():
        await bot.close()


def is_ready():
    return bot.is_ready()


async def getHistory(channel_id, limit=20000, output_to_file=False):
    channel = bot.get_channel(int(channel_id))

    messages = [message async for message in channel.history(limit=limit, oldest_first=False)]
    messages.reverse()

    parsed_messages = [
        {
            "id" : message.id, 
            "date" : message.created_at, 
            "author" : f"{message.author.name}#{message.author.discriminator}", 
            "content" : message.content
        } for message in messages
    ]

    # print("MESSAGES LOADED")
    # print("Saving messages...")
    
    if output_to_file:
        with open("outputs/user_history.json", 'w', encoding='utf-8') as file:
            json.dump(parsed_messages, file, ensure_ascii=False, default=str) # datetime.datetime.strptime("2019-11-22 18:32:20.461000", '%Y-%m-%d %H:%M:%S.%f')

    return parsed_messages


async def getHistoryAround(channel_id, date, limit=15, output_to_file=False):
    channel = bot.get_channel(int(channel_id))

    if type(date) != datetime.datetime:
        if len(date) == 19: date += ".000000"
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')

    messages = [message async for message in channel.history(limit=limit, around=date, oldest_first=True)]

    index = 0
    for i in range(len(messages)):
        if messages[i].created_at == date: 
            index = i
            break

    left  = index
    right = len(messages) - 1 - index
    diff  = left - right

    if left > right: messages = messages[ diff:]
    else           : messages = messages[:-diff]

    parsed_messages = [
        {
            "id" : message.id, 
            "date" : message.created_at, 
            "author" : f"{message.author.name}#{message.author.discriminator}", 
            "content" : message.content
        }
        for message in messages
    ]

    if output_to_file:
        with open("outputs/user_history.json", 'w', encoding='utf-8') as file:
            json.dump(parsed_messages, file, ensure_ascii=False, default=str) # datetime.datetime.strptime("2019-11-22 18:32:20.461000", '%Y-%m-%d %H:%M:%S.%f')


    return parsed_messages

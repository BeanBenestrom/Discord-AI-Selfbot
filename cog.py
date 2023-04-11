import discord, json, datetime
from discord.ext import commands
from settings import BOT_ID, COMMAND_PREFIX
import utility, debug, ai, vectorDatabase

w  = debug.Fore.WHITE
lb = debug.Fore.LIGHTBLACK_EX
lg = debug.Fore.LIGHTGREEN_EX
ly = debug.Fore.LIGHTYELLOW_EX
lr = debug.Fore.LIGHTRED_EX


class MainCog(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.extra_info = False
        self.locks  = {}
        self.chache = {}

    async def ping(self, ctx, message):
        print(f"PING - ARGS: {message}")
        await ctx.send('pong!')


    async def users(self, ctx):   
        users_info = "" 
        for user in self.bot.users:
            if user.id == BOT_ID : continue
            if not user.dm_channel: continue
            users_info += f"{user.name}, {user.id}\n"

        print(users_info)


    async def printDMChannels(self, ctx):
        
        # user = discord.Object(int(id))
        # dm = self.bot.create_dm(user)
        # print(f"DM Channel ID: {dm.id}")
        # print(self.bot.private_channels)

        private_channels = self.bot.private_channels

        for channel in private_channels:
            if type(channel) == discord.DMChannel:
                print(f"DM Channel {channel.id} - {channel.recipient.name}")
        print()
        

    async def printAllPrivateChannels(self, ctx):
        private_channels = self.bot.private_channels

        for channel in private_channels:
            if type(channel) == discord.DMChannel:
                print(f"DM Channel    {channel.id} - {channel.recipient.name}")
            elif type(channel) == discord.GroupChannel:
                print(f"Group Channel {channel.id} - {channel.name}")
            else:
                print(f"UNDEFINED     {channel}")

    
    async def send_message(self, message):
        channel_id = message.channel.id

        # notes
        # ( stm must store token size )

        # if (fisrt message since turn on) and (not new channel)
            # GET RECENT CHANNEL HISTORY
            # if (stm doesn't match history)
                # UPDATE STM
            # if ()

        # ADD MESSAGE into CHANNEL QUEUE
        # LOCK CHANNEL

        # if new channel
            # GET CHANNEL HISTORY UP TO 50000 - MINUS CURRENT MESSAGE
            # BUILD STM
            # GET LTM EMBEDDINGS
            # BUILD LTM
            # SAVE FAILED EMBEDDINGS INTO FILE

        # ADD MESSAGES FROM QUEUE INTO STM
        # SEND OVERFLOWING STM INTO LTM

        # GENERATE RESPONSE

        # RESPOND
        # UNLOCK CHANNEL


        # if (fisrt message since turn on) and (not new channel)
            # GET RECENT CHANNEL HISTORY
            # if (stm doesn't match history)
                # UPDATE STM

        # ADD MESSAGE TO BUFFER

        # LOCK
        # DYNAMIC DELAY

        # if new channel
            # GET CHANNEL HISTORY
            # BUILD STM
            # GET LTM EMBEDDINGS
            # BUILD LTM

        # ADD MESSAGE FROM BUFFER INTO STM
        # ADD OVERFLOWING STM INTO LTM

        # SEND MESSAGE
        # UNLOCK


        # if vectorDatabase.create_channel_memory_if_new(channel_id):
        #     pass
        #     # GET CHANNEL HISTORY
        #     # BUILD STM
        #     # GET LTM EMBEDDINGS
        #     # BUILD LTM

        # else:
        #     pass
            
            

            # if not vectorDatabase.add_messages(message.author.id, memory, debug_info=True): return
            # if not vectorDatabase.create_index(): return

            # debug.logt(g, "Index created")     

        # UNLOCK


    @commands.Cog.listener()
    async def on_message(self, message):
        # utility.print_message_info(message)
        utility.print_message_info_inline(message, 30, 20, 20, 50)

        if message.content is None or len(message.content) == 0: return
        

        if message.content[0:len(COMMAND_PREFIX)].lower() == COMMAND_PREFIX.lower() and utility.is_admin(message.author.id):
            try:
                command, args = utility.get_command_info(message)
                utility.print_command_info(message, command, args)
                # print(args)
                args = [*args, *([None] * (10 - len(args)))]  
                ctx = message.channel
                if   command == "ping"                      : await self.ping                   (ctx, str(args[0:])             )
                elif command == "users"                     : await self.users                  (ctx                            )
              # elif command == "TESTgethistory"            : await self.TESTgethistory         (ctx, args[0]                   )
                elif command == "printDMChannels"           : await self.printDMChannels        (ctx                            )
                elif command == "printAllPrivateChannels"   : await self.printAllPrivateChannels(ctx                            )
              # elif command == "getHistoryAround"          : await self.getHistoryAround       (ctx, args[0], args[1], args[2] )
            except Exception as e:
                print( "[*] BOT - Invalid command")
                print(f"          exception: {e}")
            return
        
        if message.author.id == BOT_ID: 
            if self.extra_info: debug.log(lb, "[-] BOT - Skipped message. Sent by bot")
            return
        if message.guild != None: 
            if self.extra_info: debug.log(lb, "[-] BOT - Skipped message. Sent inside guild")
            return
        
        if not utility.is_admin(message.author.id): return

        # INITIATE SENDING MESSAGE
        # await self.send_message(message)


def setup(_bot):
    global bot
    bot = _bot
    _bot.add_cog(MainCog(_bot))
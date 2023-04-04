import discord
from discord.ext import commands
from settings import BOT_ID, ADMIN_ID, COMMAND_PREFIX, CONTAINER_CHAR
import utility


class MainCog(commands.Cog):


    def __init__(self, bot):
        self.bot = bot

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


    async def TESTgethistory(self, ctx, user):
        user = self.bot.get_user(int(user))
        messages = [message async for message in user.history(limit=50000, oldest_first=True)]
        
        parsed_messages = [[message.id, f"{message.author.name}#{message.author.discriminator}", message.content] for message in messages]
        
        print("MESSAGES LOADED")
        string_parsed_messages = str(parsed_messages)
        print("Saving messages...")
        
        with open("outputs/test_user_messages.json", 'w', encoding="utf-8") as file:
            file.write(string_parsed_messages) 
        print("TEST MESSAGES SAVED")


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


    @commands.Cog.listener()
    async def on_ready(self):
        print(CONTAINER_CHAR * 30)
        print("LOGGED IN TO ACCOUNT: ")
        print(f"user: {self.bot.user.name}#{self.bot.user.discriminator}")
        print(f"id:   {self.bot.user.id}")
        print(CONTAINER_CHAR * 30)


    @commands.Cog.listener()
    async def on_message(self, message):
        utility.print_message_info(message)
        # utility.print_message_info_inline(message)

        if message.content is None or len(message.content) == 0: return
        
        if message.author.id  == BOT_ID:        return
        if message.content[0] == COMMAND_PREFIX and message.author.id == ADMIN_ID:
            try:
                command, args = utility.get_command_info(message)
                utility.print_command_info(message, command, args)
                # print(args)
                args = [*args, *([None] * (10 - len(args)))]
                if   command == "ping":            await self.ping(message.channel, str(args[0]))
                elif command == "users":           await self.users(message.channel)
                elif command == "TESTgethistory":  await self.TESTgethistory(message.channel, args[0])
                elif command == "printDMChannels": await self.printDMChannels(message.channel)
                elif command == "printAllPrivateChannels": await self.printAllPrivateChannels(message.channel)
            except Exception as e:
                print( "[*] BOT - Invalid command")
                print(f"          exception: {e}")
            return


def setup(bot):
    bot.add_cog(MainCog(bot))
import datetime
import debug
from settings import BOT_ID, ADMINS_ID, COMMAND_PREFIX, CONTAINER_CHAR

w  = debug.Fore.WHITE
lb = debug.Fore.LIGHTBLACK_EX
lg = debug.Fore.LIGHTGREEN_EX
ly = debug.Fore.LIGHTYELLOW_EX
lr = debug.Fore.LIGHTRED_EX


def is_owner(id):
    '''
    check if message sender is the owner.
    '''
    # return ctx.message.author.id == ADMIN_ID


def is_admin(id):
    '''
    check if message sender is the admin.
    '''
    for admin in ADMINS_ID:
        if id == admin: return True
    return False



def print_message_info(messageClass):
    '''
    Print message information into the terminal.
    '''
    debug.log(lb, CONTAINER_CHAR * 30)
    try:    debug.log(w, f"ACTIVITY: {messageClass.activity}")
    except: debug.log(w, f"ACTIVITY: FAILED")                 
    try:    debug.log(w, f"AUTHOR  : {messageClass.author.name}")
    except: debug.log(w, f"AUTHOR  : FAILED")
    try:    debug.log(w, f"GUILD   :   origin: {messageClass.guild}")
    except: debug.log(w, f"GUILD   :   origin: FAILED")
    try:    debug.log(w, f"              name: {messageClass.guild.name}")
    except: debug.log(w, f"              name: FAILED")
    try:    debug.log(w, f"CHANNEL :   origin: {messageClass.channel}")
    except: debug.log(w, f"CHANNEL :   origin: FAILED")
    try:    debug.log(w, f"CHANNEL :       id: {messageClass.channel.id}")
    except: debug.log(w, f"CHANNEL :       id: FAILED")
    try:    debug.log(w, f"              type: {messageClass.channel.type}")
    except: debug.log(w, f"              type: FAILED")
    try:    debug.log(w, f"             guild: {messageClass.channel.guild}")
    except: debug.log(w, f"             guild: FAILED")
    try:    debug.log(w, f"          category: {messageClass.channel.category}")
    except: debug.log(w, f"          category: FAILED")
    try:    debug.log(w, f"MESSAGE : {messageClass.content}")
    except: debug.log(w, f"MESSAGE : FAILED")
    try:    debug.log(w, f"MENTIONS:   normal: {messageClass.mentions}")
    except: debug.log(w, f"MENTIONS:   normal: FAILED")
    try:    debug.log(w, f"               raw: {messageClass.raw_mentions}")
    except: debug.log(w, f"               raw: FAILED")
    debug.log(lb, CONTAINER_CHAR * 30)


def print_command_info(messageClass, command:str, args:list=[]):
    '''
    Print command information into the terminal.
    
    ### MESSAGE PRINTED INTO TERMINAL:

     ---------------------------------------

    COMMAND: {command}

    ARGS   : {args}

    SENDER : {messageClass.author.name} - {messageClass.author.id}


    '''  
    string_args = ""
    for arg in args: string_args += f"{arg} "

    debug.log(lb, CONTAINER_CHAR * 30)
    debug.log(w, f"COMMAND: {command}")
    debug.log(w, f"ARGS   : {string_args}")
    debug.log(w, f"SENDER : {messageClass.author.name} - {messageClass.author.id}")
    debug.log(lb, CONTAINER_CHAR * 30)


def print_message_info_inline(messageClass, max_guild_length, max_channel_length, max_author_length, max_message_length):
    '''
    Print message information inline into the terminal.
    '''

    def padding(string, max):
        length = len(string)
        if length > max: length = max
        return string + " " * ( max - length )

    guildText = ""
    if messageClass.guild: guildText = f"{padding(messageClass.guild.name, max_guild_length)} - "

    channelText = padding(str(messageClass.channel), max_channel_length)
    authorText  = padding( messageClass.author.name, max_author_length )

    l  = messageClass.content.split('\n')
    inline = f"{guildText}{channelText} - {authorText} - {l[0][:max_message_length] + ' ...' if len(l) != 1 else l[0][:max_message_length]}"
    debug.log(lb, inline)



def get_command_info(messageClass):
    '''
    Takes in the discord message object and retrieves the command name and the passed arguments.
    
    ##### RETURN: ( command : `str`, args : `list` )
    
    ### PREREGUISITES:
    - make sure that the function is in the format.

        `[COMMAND_PREFIX][COMMAND] [ARGS]...`

        example: `@BOT> add_numbers 24 15 9 10`
    '''
    parts = messageClass.content.split(' ')
    command = parts[1]
    args = parts[2:]
    return (command, args)


# def serialize_datetime(obj):
#     if isinstance(obj, datetime.datetime):
#         return obj.isoformat()
#     raise TypeError("Type not serializable")
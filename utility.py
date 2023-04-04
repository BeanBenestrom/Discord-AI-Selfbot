from settings import BOT_ID, ADMIN_ID, COMMAND_PREFIX, CONTAINER_CHAR


def is_owner(ctx):
    '''
    check if message sender is the admin.
    '''

    return ctx.message.author.id == ADMIN_ID



def print_message_info(messageClass):
    '''
    Print message information into the terminal.
    '''
    print(CONTAINER_CHAR * 30)
    try:    print(f"ACTIVITY: {messageClass.activity}")
    except: print(f"ACTIVITY: FAILED")                 
    try:    print(f"AUTHOR  : {messageClass.author.name}")
    except: print(f"AUTHOR  : FAILED")
    try:    print(f"GUILD   :   origin: {messageClass.guild}")
    except: print(f"GUILD   :   origin: FAILED")
    try:    print(f"              name: {messageClass.guild.name}")
    except: print(f"              name: FAILED")
    try:    print(f"CHANNEL :   origin: {messageClass.channel}")
    except: print(f"CHANNEL :   origin: FAILED")
    try:    print(f"CHANNEL :       id: {messageClass.channel.id}")
    except: print(f"CHANNEL :       id: FAILED")
    try:    print(f"              type: {messageClass.channel.type}")
    except: print(f"              type: FAILED")
    try:    print(f"             guild: {messageClass.channel.guild}")
    except: print(f"             guild: FAILED")
    try:    print(f"          category: {messageClass.channel.category}")
    except: print(f"          category: FAILED")
    try:    print(f"MESSAGE : {messageClass.content}")
    except: print(f"MESSAGE : FAILED")
    try:    print(f"MENTIONS:   normal: {messageClass.mentions}")
    except: print(f"MENTIONS:   normal: FAILED")
    try:    print(f"               raw: {messageClass.raw_mentions}")
    except: print(f"               raw: FAILED")
    print(CONTAINER_CHAR * 30)


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

    print(CONTAINER_CHAR * 30)
    print(f"COMMAND: {command}")
    print(f"ARGS   : {string_args}")
    print(f"SENDER : {messageClass.author.name} - {messageClass.author.id}")
    print(CONTAINER_CHAR * 30)


def print_message_info_inline(messageClass):
    '''
    Print message information inline into the terminal.
    '''
    print(f"{messageClass.author.name} - {messageClass.channel} - {messageClass.content}")



def get_command_info(messageClass):
    '''
    Takes in the discord message object and retrieves the command name and the passed arguments.
    
    ##### RETURN: ( command : `str`, args : `list` )
    
    ### PREREGUISITES:
    - make sure that the function is in the format.

        `[COMMAND_PREFIX][COMMAND] [ARGS]...`

        example: `>add_numbers 24 15 9 10`

    - COMMAND_PREFIX must be 1 charather
    '''
    parts = messageClass.content.split(' ')
    command = parts[0][1:]
    args = parts[1:]
    return (command, args)
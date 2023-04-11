'''
PROMPT
======

All the stuff related to the AI prompt.
Creation, calculating tokens, etc.

FUNCTIONS
---------
tokens_from_string

tokens_from_message

tokens_from_messages

message_to_string

memory_string_crafter 

prompt_crafter 

PROMPT FUNCTIONS
----------------
DEFAULT
'''

import datetime, tiktoken
import debug

w  = debug.Fore.WHITE
lb = debug.Fore.LIGHTBLACK_EX
lg = debug.Fore.LIGHTGREEN_EX
ly = debug.Fore.LIGHTYELLOW_EX
lr = debug.Fore.LIGHTRED_EX


# def get_token_amount(message):
enc = tiktoken.get_encoding("cl100k_base")

# the added * 2 is there to get a more accurate answer for this kind of usage, as Discord messages aren't like typical paragraphs
def tokens_from_string(string):
    '''
    Get a perdiction for tokens with tiktoken.

    PARAMETERS
    ----------
    `string` : `str`

    RETURN
    ------
    Returns an `int` of how many tokens the string would be.
    '''
    return len(enc.encode(string)) + 1


def tokens_from_message(prev_message, message):
    '''
    Returns the perdicted amount of tokens from a message.

    PARAMETERS
    ----------
    `prev_message` : `None || dict`
        The previous message.
        Read the assumptions section on the proper message format.

    `current_message` : `dict`
        Current message.
        Read the assumptions section on the proper message format.

    ASSUMPTIONS
    -----------
    `messages` must follow the message format given by the `message_to_string` function.
    Check its assumptions list for the format.

    RETURN
    ------
    Returns an `int` of how many tokens the message is
    '''
    return tokens_from_string(message_to_string(prev_message, message))


def tokens_from_messages(messages):
    '''
    Calculate the amount of tokens inside a message or list of messages.

    PARAMETERS
    ----------
    `messages` : `dict || dict[]`
        Message or messages from for which tokens will be counted.
        Read the assumptions section on the proper message format. 

    ASSUMPTIONS
    -----------
    `messages` must follow the message format given by the `message_to_string` function.
    Check its assumptions list for the format.

    `messages` is assumed to go from oldest to newest

    RETURN
    ------
    Returns a dictionary containing the fields `total`, and `each`:

    `total` : `int`
        The total amount of tokens
    `each` : `int[]`
        How many tokens each message was
    '''
    if type(messages) != list: messages = [messages]

    info = {
        "total" : 0,
        "each"  : []
    }

    prev_message = None
    for message in messages:   

        next_tokens = tokens_from_message(prev_message, message)

        info["total"] += next_tokens
        info["each"].append(next_tokens) 
        prev_message   = message

    return info


def message_to_string(prev_message, current_message):
    '''
    Get the string representation of a message.

    PARAMETERS
    ----------
    `prev_message` : `None || dict`
        The previous message.
        Read the assumptions section on the proper message format.

    `current_message` : `dict`
        Current message.
        Read the assumptions section on the proper message format.

    ASSUMPTIONS
    -----------
    `prev_message` and `current_message` must contain atleast the following fields for this function not to fail:

    `date`      : str, of format `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M:%S.%f`
    `author`    : str
    `content`   : str

    RETURN
    ------
    Depends on the time difference between `prev_message` and `current_date`.
    Check what happens inside the function to find out. :)
    '''
    if prev_message is None: return f"\n({current_message['date'].split('.')[0]}) {current_message['author']}:\n{current_message['content']}\n"

    if current_message['content'] == "": current_message['content'] = "[attachment]"

    if len(prev_message['date'])    == 19:    prev_message['date'] += ".000000"
    if len(current_message['date']) == 19: current_message['date'] += ".000000"

    prev_date    = datetime.datetime.strptime(   prev_message['date'], '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.datetime.strptime(current_message['date'], '%Y-%m-%d %H:%M:%S.%f')  
    if current_message['author'] == prev_message['author'] and abs( current_date - prev_date ).total_seconds() < 3 * 60:    
        return current_message['content'] + '\n'
    else:                                           
        return f"\n({current_message['date'].split('.')[0]}) {current_message['author']}:\n{current_message['content']}\n"


def memory_string_crafter(memory, max_tokens, mode=1):
    '''
    Crafts a string representation of a chain of messages which complies with being inside the a token threshold.
    Returned string could then be placed onto a prompt.

    This is achieved by creating an empty string and then adding messages onto the string in the right format until the token threshold is reached.

    `memory` can be an empty list.

    PARAMETERS
    ----------
    `memory` : `dict[]`
        A list of messages to be converted.
        Read the assumptions section on the proper memory format.

    `max_tokens` : `int`
        The maximun amount of tokens the string is allowed to be

    `mode` : `int`, [0, 1, 2]
        There are three ways that this function can go about adding messages into the string.

        `0` Start from the first message, iteratively add next message, until all messages are in string or token threshold is reached.
        This means that the newest messages would be skipped if threshold was reached before end of array.

        `1` Start from the last message, iteratively add previous message, until all messages are in string or token threshold is reached.
        This means that the oldest messages would be skipped if threshold was reached before end of array.

        `2` Start the adding from the middle of the array and expands outwards until all messages are in string or token threshold is reached.

    ASSUMPTIONS
    -----------
    Each message inside of `memory` must follow the message format given by the `message_to_string` function.
    Check its assumptions list for the format.

    `memory` is assumed to go from oldest to newest

    `max_tokens` > 0, obviously. duuuuhhh

    RETURN
    ------
    Returns a dictionary containing the fields `string`, `tokens`:

    `string` : `str`
        The actual wanted string

    `tokens` : `int`
        How many tokens the string is
    '''
    A = {
        "string" : "",
        "tokens" : 0
    }

    if len(memory) == 0: return A
    
    if mode == 0:
        prev_message = None

        for message in memory:
            next        = message_to_string(prev_message, message)
            next_tokens = tokens_from_string(next)
            if A["tokens"] + next_tokens > max_tokens: break
            A["tokens"] += next_tokens
            A["string"] += next
            prev_message = message

    elif mode == 1:
        prev_A = None

        for i in range(len(memory) - 1, -1, -1):
            next_tokens = tokens_from_string(message_to_string(None, memory[i]))

            if A["tokens"] + next_tokens > max_tokens:
                if not i == len(memory) - 1: 
                    next        = message_to_string(None, memory[i+1])
                    next_tokens = tokens_from_string(next)
                    A = prev_A
                    A["tokens"] += next_tokens
                    A["string"]  = next + A["string"]
                break

            prev_A = A.copy()

            prev_message = None
            if i - 1 >= 0: prev_message = memory[i - 1] 
            next        = message_to_string(memory[i - 1], memory[i])
            next_tokens = tokens_from_string(next)
            A["tokens"] += next_tokens
            A["string"] = next + A["string"]

    elif mode == 2:
        result = tokens_from_messages(memory)

        switch = True
        section = [0, len(memory) - 1]
        while result["total"] > max_tokens:
            if switch:
                result["total"] -= result["each"][section[0]]
                section[0]      += 1
                switch           = False
            else:
                result["total"] -= result["each"][section[1]]
                section[1]      -= 1
                switch           = True

        result["total"] -= result["each"][section[0]]
        tokens = tokens_from_message(None, memory[section[0]])
        result["total"] += tokens

        if result["total"] > max_tokens: section[0] += 1

        prev_message = None
        for message in memory[section[0]:section[1]]:
            next        = message_to_string(prev_message, message)
            next_tokens = tokens_from_string(next)
            A["tokens"] += next_tokens
            A["string"] += next
            prev_message = message

    return A


def prompt_crafter(long_term_memory, short_term_memory, max_ltm_tokens, max_stm_tokens, output_result_to_file=False):
    '''
    Craft a prompt containing long-term memory and short-term memory.

    PARAMETERS
    ----------
    `long_term_memory` : `dict || dict[] || dict[][]`
        Memories each containing messages from long-term memory that will be added into prompt.
        Read the assumptions section on the proper memory format.

    `short_term_memory` : `dict || dict[]`
        Messages from short-term memory that will be added into prompt.
        Read the assumptions section on the proper memory format.

    `max_ltm_tokens` : `int`
        Max amount of tokens for long-term memory

    `max_stm_tokens` : `int`
        Max amount of tokens for short-term memory

    `output_result_to_file` : `bool`
        Also write output into file `outputs/ai_generated_prompt.txt`
    
    ASSUMPTIONS
    -----------
    Each message inside of `memory` must follow the message format given by the `memory_string_crafter` function.
    Check its assumptions list for the format.
    
    `max_ltm_tokens` and `max_stm_tokens` > 0

    All messages inside the memories are assumed to go from oldest to newest
    
    RETURN
    ------
    Returns a dictionary containing the fields `string`, `ltm_tokens`, `stm_tokens`:

    `string` : `str`
        The actual wanted prompt string which can then be given to ChatGPT or any other AI model.

    `base_tokens` : `int`
        How many tokens the base/template of the prompt is

    `ltm_tokens` : `int`
        How many tokens the long-term memory string inside the prompt is

    `stm_tokens` : `int`
        How many tokens the shortstring inside the promp-term memory string inside the prompt is
    '''

    # message = [ id, date, author, message ]

    ltm = ""
    stm = ""
    ltm_tokens_per_memory = max_ltm_tokens / len(long_term_memory)
    ltm_tokens = 0
    stm_tokens = 0

    i = 1
    for memory in long_term_memory:
        ltm_snippet  = memory_string_crafter(memory, ltm_tokens_per_memory, 2)["string"]
        ltm         += f"MEMORY {i}{ltm_snippet}\n"
        i           += 1

    stm = memory_string_crafter(short_term_memory, max_stm_tokens)["string"]

    ltm_tokens = tokens_from_string(ltm)
    stm_tokens = tokens_from_string(stm)

    prompt = DEFAULT(ltm.strip(), stm.strip())

    if output_result_to_file:
        with open("outputs/generated_prompt.txt", 'w', encoding='utf-8') as file:
            file.write(prompt)

    # total_tokens = RESPONSE_SPINE_TOKENS + ltm_tokens + stm_tokens
    # debug.log(lg, f"[#] AI - Prompt crafted. Perdiction ( Spine, LTM, STM, Total, Cost ): {RESPONSE_SPINE_TOKENS} {ltm_tokens} {stm_tokens} {total_tokens} {0.002/1000*total_tokens*0.92}")

    return {
        "string" : prompt,
        "ltm_tokens" : ltm_tokens,
        "stm_tokens" : stm_tokens
    }



def DEFAULT(long_term_memory_string, short_term_memory_string):
    '''
    Default prompt for AI.

    PARAMETERS
    ----------
    `long_term_memory_string` : `str`
        Long-term memory in prompt string form

    `short_term_memory_string` : `str`
        Short-term memory in prompt string form

    RETURN
    ------
    Returns the full prompt containing the given long-term memory and short-term memory.
    '''
    with open("prompts/default.txt") as file:
        return file.read().format(long_term_memory_string = long_term_memory_string, short_term_memory_string = short_term_memory_string)
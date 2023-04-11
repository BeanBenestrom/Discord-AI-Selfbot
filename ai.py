'''
ARTIFICIAL INTELLIGENCE
=======================

Module for interacting with the AI and AI functionality.

For this module to work, the an openai api key is required.
This is by default required to be saved as an enviroment variable named `API_KEY_OPENAI`,
but this can of course be changed on the first few lines of this module.

NOTES
-----
This module needs access to the currently active bot.
The bot can be given to the module by calling `link_bot`.
If the bot is changed, `link_bot` needs to be called again.

FUNCTIONS
---------
link_bot

embed_strings

create_channel_memory_if_new

remove_channel_memory_if_exist

add_messages_into_memory

respond
'''

import openai, os, json, datetime, asyncio
import debug, prompt, vectorDatabase, cog
openai.api_key = os.environ["API_KEY_OPENAI"]

w  = debug.Fore.WHITE
lb = debug.Fore.LIGHTBLACK_EX
lg = debug.Fore.LIGHTGREEN_EX
ly = debug.Fore.LIGHTYELLOW_EX
lr = debug.Fore.LIGHTRED_EX


EMBEDDING_TRUE_MAX_TOKEN_SIZE = 8191

EMBEDDING_MAX_BATCH_SIZE = 1000
# EMBEDDING_MAX_TOKEN_SIZE = 7800         # 100 tokens ~= 75 words, hence  tokens = 1.33333333333333333333333 * words
EMBEDDING_RPM = 20 
EMBEDDING_TPM = 150000

# RESPONSE_SPINE_TOKENS   = 634
RESPONSE_MAX_LTM_TOKENS = 1500
RESPONSE_MAX_STM_TOKENS = 1500

TESTING_WRITE_TO_FILE = True
bot = None


def link_bot(_bot):
    '''
    Gives this module access to the current discord bot.

    This module needs access to the current bot so that it can call discord related functions.
    '''
    global bot
    bot = _bot


def embed_strings(strings, debug_info=False, output_to_file=False):
    '''
    Embed string or a list of strings.

    Embedding uses `text-embedding-ada-002`.
    Currently when writing, this is priced at `$0.0004 / 1000 tokens`.
    Check OpenAI's official website for more up-to-date pricings.

    PARAMETERS
    ----------
    `strings` : `str || str[]`
        String(s) to be embedded

    `debug_info` : `bool`
        Print extra information

    `output_to_file` : `bool`
        Writes result into file `outputs/embedding_responses.json`.

    ASSUMPTIONS
    -----------
    The length of all strings must not be too large.
    How large? Idk, `openai.Embedding.create` just doesn't work if string inside of `input` are "too large". 
    Just test bro. lol

    FAILURE
    -------
    `[*]` : An item inside of `strings` was not actually of type str 

    `[*]` : Failed to embed batch. One reason this could happen is because a string inside the batch was too long.

    RETURN
    ------
    `None` if failure

    If `strings` was of type `str`, returns the embedding of that string directly.

    Else if `stings` was of type `str[]`, returns a list of embeddings.

    Check OpenAI's documentation for more information on embeddings.
    '''
    was_string = False
    
    if type(strings) == str: 
        was_string = True
        strings = [strings]
    for string in strings:
        if type(string) != str:
            debug.log(ly, f"[*] AI - Failed to embed string{ '' if len(strings) == 1 else 's' } because { 'the' if len(strings) == 1 else 'a' } string was not actually of type string")
            debug.log(ly, f"         invalid string: {string}"      )
            debug.log(ly, f"                   type: {type(string)}")
            return
    
    try:
        result = []
        total_amount_of_batches = 0     # The amount of batches sent to openAI
        string_amount = len(strings)
        tokens = 0

        if output_to_file: open('outputs/embedding_responses.json', 'w', encoding='utf-8').close()

        while True:
            if EMBEDDING_MAX_BATCH_SIZE*total_amount_of_batches >= len(strings): break
            batch = strings[EMBEDDING_MAX_BATCH_SIZE*total_amount_of_batches:(total_amount_of_batches+1)*EMBEDDING_MAX_BATCH_SIZE]
                 
            response = openai.Embedding.create(model="text-embedding-ada-002", input = batch)
            total_amount_of_batches += 1
            tokens                  += response.usage.total_tokens

            for embeddingObject in response.data:
                result.append(embeddingObject.embedding)     

            if output_to_file:
                with open("outputs/embedding_responses.json", 'a', encoding='utf-8') as file:
                    json.dump(response, file, ensure_ascii=False)

            if debug_info: debug.logt(lb, f"[-] AI - Batch embedded ( number, tokens ): {total_amount_of_batches} {response.usage.total_tokens}")

        debug.log(lg, f"[#] AI - Embedding {string_amount} string{ '' if string_amount == 1 else 's' } completed with {total_amount_of_batches} batch{'' if total_amount_of_batches == 1 else 'es'} costing {tokens} tokens")
        if was_string:  return result[0]
        else:           return result
        
    except Exception as e:
        debug.log(ly,                         f"[*] AI - Failed to embed string{ '' if string_amount == 1 else 's' }"  )
        if len(str(e)) > 1000:  debug.log(ly, f"         exception: {str(e)[:50]}...{str(e)[-100:]}"                    )
        else:                   debug.log(ly, f"         exception: {e}"                                                )
        return


async def create_channel_memory_if_new(channel_id):
    '''
    Create new memory for channel if this channel doesn't already have memory.

    This function does not usually need to be called manually, 
    as `add_messages_into_memory` automatically calls this fuction before inserting messages.

    PARAMETERS
    ----------
    `channel_id` : unique `int `
        Channel identifier for which new memory will be created

    RETURN
    ------
    `True` : channel memory was created.

    `False` : channel memory already existed.
    '''
    if not os.path.isfile(f"short-term-memory/{str(channel_id)}"):
        with open(f"short-term-memory/{str(channel_id)}", 'w', encoding='uft-8') as file:
            json.dump({
                "total_tokens": 0,
                "messages": [],
                "failedSaves": []
            }, file, ensure_ascii=False)
        vectorDatabase.remove_channel_memory_if_exist(channel_id)

        messages = await cog.getHistory(channel_id, limit=15)
        if not add_messages_into_memory(channel_id, messages, debug_mode=True): return

        vectorDatabase.create_index()

        debug.log(lg, f"[#] AI - New channel added into memory: {str(channel_id)}")
        return True
    return False


async def remove_channel_memory_if_exist(channel_id):
    '''
    Remove a channel's memory if this channel has memory.

    PARAMETERS
    ----------
    `channel_id` : unique `int`
        Channel identifier from which all memory will be removed

    RETURN
    ------
    `True` : channel memory was dropped.
    
    `False` : there was no memory to drop.
    '''
    if os.path.isfile(f"short-term-memory/{str(channel_id)}"):
        os.remove(f"short-term-memory/{str(channel_id)}")
        vectorDatabase.remove_channel_memory_if_exist(channel_id)
        debug.log(lg, f"[#] AI - Channel removed from memory: {str(channel_id)}")
        return True
    return False


def add_messages_into_memory(channel_id, messages, debug_info=False, debug_mode=False):
    '''
    Add a message or a list of messages into AI's memory

    `channel_id` : unique `int`
        The channel identifier for which message will be added into memory

    `messages`   : `dict || dict[]`
        Message or messages to be added into memory.
        Read the assumptions section on the proper message format before adding any messages

    `debug_info` : `bool`
        Print extra information

    `debug_file` : `None || str`
        If not None, writes the output of the operation into the given file istead of the channels short-term memory.
        Also writes information about done operations into file `outputs/add_messages_into_memory_debug.json`.
        This also doesn't change the 
        This really is only for testing purposed.
        [ FIX THIS ]

    ASSUMPTIONS
    -----------
    Memory for channel is assummed to be initialized.

    `messages` are assumed to go from oldest to newest

    `messages` must contain atleast the following fields for this function not to fail:

    `id`        : unique int
    `date`      : str, of format `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M:%S.%f`
    `author`    : str, not longer than vectordatabase._MAX_AUTHOR_LENGTH
    `content`   : str, not longer than vectordatabase._MAX_MESSAGE_LENGTH

    FAILURE
    -------
    [ADD FAILURES. TOO LAZY RIGHT NOW...]
    `[!]` : 

    RETURN
    ------
    Return `True` if function succeeded
    '''
    if type(messages) != list: messages = [messages]
    memory = None

    with open(f"short-term-memory/{channel_id}.json", encoding='utf-8') as file:
        memory = json.load(file)

    tokensOriginaly = memory["total_tokens"]
    tokensAdded = 0
    tokensRemoved = 0

    # ADD MESSAGES INTO SHORT-TERM MEMORY
    prev_message = None if len(memory["messages"]) == 0 else memory["messages"][-1]
    
    for message in messages:
        tokens = prompt.tokens_from_message(prev_message, message)

        memory["messages"].append({ 
            "id"        : message["id"], 
            "date"      : message["date"], 
            "author"    : message["author"], 
            "content"   : message["content"],
            "tokens"    : tokens
        })
        memory["total_tokens"] += tokens
        prev_message = memory["messages"][-1]
    tokensAdded = memory["total_tokens"] - tokensOriginaly

    # TRIM SHORT-TERM MEMORY AND ADD TRIMMED MESSAGES INTO LONG-TERM MEMORY SO THAT SHORT-TERM MEMORY IS INSIDE OF TOKEN THRESHOLD
    trim_count = 0

    while memory["total_tokens"] > RESPONSE_MAX_STM_TOKENS:
        memory["total_tokens"] -= memory["messages"][trim_count]["tokens"]
        trim_count += 1
    tokensRemoved = tokensAdded - memory["total_tokens"]

    if debug_mode:
        with open("outputs/add_messages_into_memory_debug.json", 'w', encoding='utf-8') as file:
            json.dump({
                "added"                   : memory["messages"][-len(messages):],
                "removed"                 : memory["messages"][:trim_count],
                "tokensBefore"            : tokensOriginaly,
                "tokensAfterAdd"          : memory["total_tokens"] + tokensRemoved,
                "tokensAfterTrim"         : memory["total_tokens"],
                "RESPONSE_MAX_STM_TOKENS" : RESPONSE_MAX_STM_TOKENS
            }, file, ensure_ascii=False)
        return True

    trimmed_messages = memory["messages"][:trim_count]

    embeddings = embed_strings(trimmed_messages["content"])
    if not embeddings is None: 
        for i in range(trimmed_messages): trimmed_messages[i]["embedding"] = embeddings[i]

        response = vectorDatabase.add_messages(channel_id, trimmed_messages)

        if not response["fullSuccess"]:
            for failed_slice in response["failedSlices"]:
                for message in trimmed_messages[failed_slice[0]:failed_slice[1]]: 
                    memory["failedSaves"].append(message)

    memory["messages"] = memory["messages"][trim_count:]

    with open(f"short-term-memory/{channel_id}.json", 'w', encoding='utf-8') as file:
        json.dump(memory, file, ensure_ascii=False)

    if not embeddings is None: debug.log(lg, f"[#] AI - Adding messages success.")
    else                     : debug.log(lr, f"[!] AI - Adding messages failed while trimming. Loss occured for oldest short-term memories.")

    return True


def respond(channel_id, output_to_file=False):
    '''
    Create a response to current context.
    
    Context for the response is build with the current long-term and short-term memory of the given channel.
    Any new messages that should be taken into consideration by the AI should be added in with the `add_messages_into_memory` function.

    Responding uses `gpt-3.5-turbo`.
    Currently when writing, this is priced at `$0.002 / 1000 tokens`.
    Check OpenAI's official website for more up-to-date pricings.

    PARAMETERS
    ----------
    `channel_id` : unique `int`
        Channel identifier for which a response will be created

    RETURN
    ------

    
    Check OpenAI's documentation for more information on AI completions.
    '''

    # AI STEPS

    # LOAD LONG-TERM MEMORY FROM MILVUS
    # GET RESPONSE WITH: TEMPLATE + LTM + STM + MESSAGE
    # CHECK MODERATION AND PRINT
    # RETURN ANSWER

    short_term_memory = None

    with open(f"short-term-memory/{channel_id}.json", encoding='utf-8') as file:
        short_term_memory = json.load(file)

    if len(short_term_memory["messages"]) == 0:
        debug.log(ly, "[*] AI - Failed to create response because short-term memory has no messages")
        return

    vector = embed_strings(short_term_memory["messages"][-1]["content"])
    if not vector: return
    long_term_memory_search_result = vectorDatabase.search(channel_id, vector)[0]

    for hit in long_term_memory_search_result:
        print(w, f"date: {hit.entity.get('date')}, author: {hit.entity.get('author')}, " + f"message: {hit.entity.get('message')}")

    chat_response = openai.ChatCompletion.create(
        model       =   "gpt-3.5-turbo",
        messages    =   [{"role": "user", "content": message}],
        temperature =   0.5)
    
    # moderation_response = openai.Moderation.create(input=[message])
    
    # if output_to_file:
        # with open("outputs/response.json", "w", encoding='utf-8') as file:
            # file.write(str(chat_response) + "\n\n" + str(moderation_response))


    return chat_response


if __name__ == "__main__":
    pass
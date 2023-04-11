'''
VECTOR DATABASE
===============

Module for handling all long-term memory of the AI.

LTM is handled with the use of a milvus vector database.

All memory is saved inside the collection called `discord_selfbot_memory`

NOTES
-----
The database must be started and stopped:
    >>> start()
    >>> DO STUFF ...
    >>> stop()

FUNCTIONS
---------
start

stop

is_running

create_channel_memory_if_new

remove_channel_memory_if_exist

add_messages

drop_messages

create_index

search

DROP_ALL_MEMORY
'''

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    Partition
)
import debug

w  = debug.Fore.WHITE
lb = debug.Fore.LIGHTBLACK_EX
lg = debug.Fore.LIGHTGREEN_EX
ly = debug.Fore.LIGHTYELLOW_EX
lr = debug.Fore.LIGHTRED_EX


_HOST = 'localhost'
_PORT = '19530'
_DIM = 1536
_COLLECTION_NAME = "discord_selfbot_memory"

_SCHEMA_SIZE        = 5
_MAX_AUTHOR_LENGTH  = 40
_MAX_MESSAGE_LENGTH = 2500

INSERT_BATCH_SIZE = 1000

running = False
memory_collection = None    # The entire collection object for the bot's memory


def start(collection_name=_COLLECTION_NAME):
    '''
    Start the vector database.

    PARAMETERS
    ----------
    `collection_name` : `str`
        The collection to load. 
        By default is `discord_selfbot_memory`, but can be changed to a different collection.
        This could be done for testing purposes.

    ASSUMPTIONS
    -----------
    Milvus is running

    FAILURE
    -------
    `[%]` : Database is already running

    `[!]` : connecting to Milvus fails

    `[!]` : Could not get collection
    '''
    debug.init()
    global memory_collection, _COLLECTION_NAME, running

    if running: 
        debug.log(w, "[%] VECTOR DATABASE - Could not start database, as it is already running")
        return    

    if collection_name != _COLLECTION_NAME:
        debug.log(w, f"[%] VECTOR DATABASE - Non-default database chosen: {collection_name}")

    _COLLECTION_NAME = collection_name

    try: connections.connect("default", host=_HOST, port=_PORT)
    except Exception as e:
        debug.log(lr, f"[!] VECTOR DATABASE - Could not connect to database")
        debug.log(lb, f"                      exception: {e}",              )
        raise

    try:
        if not utility.has_collection(_COLLECTION_NAME):
            fields = [
                # REMEBER TO UPDATE SCHEMA SIZE AND THE STUFF THAT DEPENDS ON IT!
                FieldSchema(name="id",        dtype=DataType.INT64,         is_primary=True,                description="Primary Message ID"),
                FieldSchema(name="date",      dtype=DataType.VARCHAR,       max_length=26,                  description="Date"),
                FieldSchema(name="author",    dtype=DataType.VARCHAR,       max_length=_MAX_AUTHOR_LENGTH,  description="Author"),
                FieldSchema(name="content",   dtype=DataType.VARCHAR,       max_length=_MAX_MESSAGE_LENGTH, description="Actual Message"),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,  dim=_DIM,                       description="Vector")
            ]
            schema = CollectionSchema(fields, "My Discord selfbot's entire long-term memory.", auto_id=False)
            memory_collection = Collection(_COLLECTION_NAME, schema)
            debug.log(lg, "[#] VECTOR DATABASE - New collection created")
            running = True
            return True
        else:
            memory_collection = Collection(_COLLECTION_NAME)
            debug.log(lg, "[#] VECTOR DATABASE - Collection loaded")
            running = True
            return True
    except Exception as e:
        debug.log(lr,  "[!] VECTOR DATABASE - Could not get collection while startup")
        debug.log(lb, f"                      exception: {e}",                       )
        raise


def stop():
    '''
    Stop the vector database.

    FAILURE
    -------
    `[%]` : Database is not running
    '''
    global running
    if not running: 
        debug.log(w, "[%] VECTOR DATABASE - Could not stop database, as it isn't running in the first place")
        return
    connections.disconnect("default")
    debug.log(lg, "[#] VECTOR DATABASE - Collection disconnected")
    running = False


def is_running():
    '''
    Returns `True` if the database is on.

    Returns `False` if database is off.
    '''
    global running
    return running



def create_channel_memory_if_new(channel_id):
    '''
    Create new memory for channel if this channel isn't already in memory.

    This function does not usually need to be called manually, 
    as `add_messages` automatically calls this fuction before inserting messages.

    PARAMETERS
    ----------
    `channel_id` : unique `int `
        Channel identifier for which new memory will be created

    RETURN
    ------
    `True` : channel memory was created.

    `False` : channel memory already existed.
    '''
    global memory_collection

    if not memory_collection.has_partition(str(channel_id)):
        memory_collection.create_partition(str(channel_id))
        debug.log(lg, f"[#] VECTOR DATABASE - New memory created for channel {str(channel_id)}")
        return True
    return False


def remove_channel_memory_if_exist(channel_id):
    '''
    Remove a channel's memory if this channel is in memory.

    PARAMETERS
    ----------
    `channel_id` : unique `int`
        Channel identifier from which all memory will be removed

    RETURN
    ------
    `True` : channel memory was dropped.
    
    `False` : there was no memory to drop.
    '''
    global memory_collection

    if memory_collection.has_partition(str(channel_id)):
        memory_collection.drop_partition(str(channel_id))
        debug.log(lg, f"[#] VECTOR DATABASE - Memory removed for channel {str(channel_id)}")
        return True
    return False


def add_messages(channel_id, messages, debug_info=False):
    '''
    Add a message or a list of messages into a channel's long-term memory.

    PARAMETERS
    ----------
    `channel_id` : unique `int`
        Channel identifier for which new messages will be added

    `messages` : `dict || dict[]`
        The message or list of messages that will be added into the channel's memory.
        Read the assumptions section on the proper message format before adding any messages

    `debug_info` : `bool`
        If extra infomation will be printed

    ASSUMPTIONS
    -----------
    `messages` must contain atleast the following fields for this function not to fail:

    `id`        : unique int
    `date`      : str, of format `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M:%S.%f`
    `author`    : str, not longer than _MAX_AUTHOR_LENGTH
    `content`   : str, not longer than _MAX_MESSAGE_LENGTH
    `embedding` : float[_DIM]

    FAILURE
    -------
    `[*]` : Developer forgor to update `schema_size_assumption` after changing the schema size.

    `[*]` : Inserting a batch of messages into long-term memory failed

    RETURN
    ------
    Returns a dictionary containing the fields `fullSuccess`, `failedAmount`, and `failedSlices`:

    `fullSuccess` : `bool`
        Whether all messages were added correctly, or a batch insert failed
    `failedAmount` : `int`
        The total amount of messages that failed
    `failedSlices` : `int[][2]`
        Contains information about all the messages that failed.
        For each entry,
        first index contains the beggining of the slice,
        the second index contains the end of the slice
    '''
    global memory_collection

    if type(messages) != list: messages = [messages]

    create_channel_memory_if_new(channel_id)

    # Check that I have indeed remembered to update this function after changing the schema entry fields
    schema_size_assumption = 5
    if _SCHEMA_SIZE != schema_size_assumption:
        debug.log(ly, "[*] VECTOR DATABASE - Could not safely add messages, as schema size has changed without proper refactoring")
        return

    # Turn message entries into proper format
    entries = [[] for _ in range(_SCHEMA_SIZE)]
    for message in messages:
        entries[0].append(message["id"]       )
        entries[1].append(message["date"]     )
        entries[2].append(message["author"]   )
        entries[3].append(message["content"]  )
        entries[4].append(message["embedding"])

    if debug_info: debug.log(lb, "[-] Memory arranged")

    # Check that all the messages are the correct size
    # too_large_messages = []
    # for enum in enumerate(entries[3]):
    #     if len(enum[1]) > _MAX_MESSAGE_LENGTH:
    #         too_large_messages.append(enum)
    # if len(too_large_messages) > 0:
    #     debug.log (ly, f"[*] VECTOR DATABASE - Could not add messages, as {len(too_large_messages)} too large message{ ' was' if len(too_large_messages) == 1 else 's were'} found" )
    #     [debug.log(lb, f"                      index: {pair[0]}    message: {pair[1][:100]}") for pair in too_large_messages[:10]]
        

    batches_inserted = 0
    info = {
        "fullSuccess"  : True,
        "failedAmount" : 0,
        "failedSlices" : []
    }

    while True:
        if INSERT_BATCH_SIZE*batches_inserted >= len(messages): break
        batch = [
            entries[i][INSERT_BATCH_SIZE*batches_inserted:(batches_inserted+1)*INSERT_BATCH_SIZE] 
            for i in range(_SCHEMA_SIZE)
        ]
        
        try:
            memory_collection.insert(batch, partition_name=str(channel_id))
            if debug_info: debug.logt(lb, f"[-] VECTOR DATABASE - Batches Inserted: {batches_inserted + 1}")
            
        except Exception as e:
            debug.log(ly,  "[*] VECTOR DATABASE - Inserting message batch failed")
            debug.log(lb, f"                      exception  : {e}",             )
            info["fullSuccess"]   = False
            info["failedAmount"] += len(batch[0])
            info["failedSlices"].append((INSERT_BATCH_SIZE*batches_inserted, (batches_inserted+1)*INSERT_BATCH_SIZE))

        batches_inserted += 1

    memory_collection.flush()
    if info["fullSuccess"]: debug.log(lg, f"[#] VECTOR DATABASE - Memory flushed. Insert complete")
    else: 
        debug.log(ly, f"[*] VECTOR DATABASE - Memory flushed. Insert completed with {info['failedAmount']} failed inserts")
        debug.log(lb, f"                      percentage: {info['failedAmount']/len(messages)*100} %",                    )
    return info
    

def drop_messages(channel_id, message_ids):
    '''
    Remove messages from channel's memory.

    Does not fail even if a message is not inside the channel's memory.

    PARAMETERS
    ----------
    `channel_id` : unique `int`
        Channel identifier from messages will be removed

    `message_ids` : `int || int[]`, unique ids
        A message's id or a list of messages' ids, which will be used to remove them from the channel's memory

    FAILURE
    -------
    `[*]` : Removing messages failed

    RETURN
    ------
    `True` : Messages were able to be removed from channel's memory

    `False` : Failed to remove messages
    '''
    global memory_collection

    if type(message_ids) != list: message_ids = [message_ids]

    expr = "id in " + str(message_ids)

    if memory_collection.has_partition(str(channel_id)):
        try:    
            memory_collection.delete(expr, partition_name=str(channel_id))
            debug.log(lg, f"[#] VECTOR DATABASE - Removed {len(message_ids[0])} messages")
            return True
        except Exception as e:
            debug.log(ly,  "[*] VECTOR DATABASE - Removing messages failed")
            debug.log(lb, f"                      exception  : {e}",       )
            return False


def create_index():
    '''
    Generate a new index for AI's memory.

    FAILURE
    -------
    `[*]` Failed to create new index

    RETURN
    ------
    `True` : Index created

    `False` : Failed to create index
    '''

    global memory_collection

    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }
    try:
        memory_collection.create_index("embedding", index)
        debug.log(lg, f"[#] VECTOR DATABASE - New index created")
        return True
    except Exception as e:
        debug.log(ly,  "[*] VECTOR DATABASE - Failed to create a new index")
        debug.log(lb, f"                      exception  : {e}",           )
        return False


def search(channel_id, vectors=None, expr=None):
    '''
    Search for messages inside channel.

    PARAMETERS
    ----------

    `channel_id` : unique `int`
        Channel identifier from which messages will searched from

    `vectors` : `float[_DIM] || float[][_DIM] || None`
        A vector or a list of vectors that will be compared to all the messages' embeddings inside long-term memory of the channel

    `expr` : `str || None`
        A boolean expression used in search 

    ASSUMTIONS
    ----------
    Either `vectors` or `expr` must be valid.
    They cannot both be None

    FAILURE
    -------
    `[*]` : Search failed

    RETURN
    ------
    If fails, returns `None`

    If search succeeds, returns the result of the search, which is in the format given by Milvus.

    Check Milvus' documentation for more information on the search function.
    '''
    global memory_collection

    if vectors is None and expr is None:
        debug.log(ly, "[*] VECTOR DATABASE - Failed to search database, as both vectors and expresion were invalid")
        return
    
    if type(vectors) != list: vectors = [vectors]
    
    search_param = {
        "data"              :   vectors,
        "anns_field"        :   "embedding",
        "param"             :   {"metric_type": "L2", "params": {"nprobe": 10}},
        "limit"             :   10,
        "expr"              :   expr,
        "partition_names"   :   [str(channel_id)],
        "output_fields"     :   ["date", "author", "content"]
    }

    try:
        memory_collection.load([str(channel_id)])
        res = memory_collection.search(**search_param)
        memory_collection.release()
        debug.log(lg, f"[#] VECTOR DATABASE - Search completed")
        return res
    except Exception as e:
        debug.log(ly,  "[*] VECTOR DATABASE - Failed search" )
        debug.log(lb, f"                      exception: {e}")

        
def DROP_ALL_MEMORY():
    '''
    Drops all of the AI's long-term memory if it exists.
    
    SHOULD ONLY BE USED WITH ABSOLUTE CONFIDENCE!
    '''
    global memory_collection
    if utility.has_collection(_COLLECTION_NAME):
        utility.drop_collection(_COLLECTION_NAME)
        debug.log(lg, f"[#] VECTOR DATABASE - COLLECTION DROPPED")


# def COPY_MEMORY_FROM_TO(from_collection, from_channel_id, to_collection, to_channel_id):
#     global memory_collection

#     if utility.has_collection(from_collection):
#         utility.drop_collection(_COLLECTION_NAME)
#         debug.log(lg, f"[#] VECTOR DATABASE - COLLECTION DROPPED")
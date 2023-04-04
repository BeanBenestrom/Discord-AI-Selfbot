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

_SCHEMA_SIZE        = 4
_MAX_AUTHOR_LENGTH  = 40
_MAX_MESSAGE_LENGTH = 2500

INSERT_MAX_BATCH_SIZE = 2000

running = False
memory_collection = None    # The entire collection object for the bot's memory


def start(collection_name=_COLLECTION_NAME):
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
        return

    try:
        if not utility.has_collection(_COLLECTION_NAME):
            fields = [
                FieldSchema(name="id",        dtype=DataType.INT64,         is_primary=True,  description="Primary Message ID"),
                FieldSchema(name="author",    dtype=DataType.VARCHAR,       max_length=_MAX_AUTHOR_LENGTH,    description="Author"),
                FieldSchema(name="message",   dtype=DataType.VARCHAR,       max_length=_MAX_MESSAGE_LENGTH,  description="Message"),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,  dim=_DIM,         description="Vector")
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
        return


def stop():
    global running
    if not running: 
        debug.log(w, "[%] VECTOR DATABASE - Could not stop database, as it isn't running in the first place")
        return
    connections.disconnect("default")
    debug.log(lg, "[#] VECTOR DATABASE - Collection disconnected")
    running = False


def create_channel_memory_if_new(channel_id):
    global memory_collection

    if not memory_collection.has_partition(str(channel_id)):
        memory_collection.create_partition(str(channel_id))
        debug.log(lg, f"[#] VECTOR DATABASE - New memory created for channel {str(channel_id)}")


def remove_channel_memory_if_exist(channel_id):
    global memory_collection

    if memory_collection.has_partition(str(channel_id)):
        memory_collection.drop_partition(str(channel_id))
        debug.log(lg, f"[#] VECTOR DATABASE - Memory removed for channel {str(channel_id)}")


def add_messages(channel_id, entries, show_debug=False):
    '''
    ENTRIES [ message id, author, message text, embedding ]
    '''

    global memory_collection

    create_channel_memory_if_new(channel_id)
    if show_debug: debug.log(lb, "[-] Created new memory")

    # Check that I have indeed remembered to update this function after changing entry fields
    schema_size_assumption = 4
    if _SCHEMA_SIZE != schema_size_assumption:
        debug.log(ly, "[*] VECTOR DATABASE - Could not safely add messages, as schema size has changed without proper refactoring")
        return

    # Turn list into proper format
    new_order_entries = [[] for _ in range(_SCHEMA_SIZE)]
    for entry in entries:
        if len(entry) != _SCHEMA_SIZE:
            debug.log(ly,  "[*] VECTOR DATABASE - Could not add messages, as entry is invalid length")
            debug.log(lb, f"                      valid length: {_SCHEMA_SIZE}",                     )
            debug.log(lb, f"                      given length: {len(entry)}",                       )
            return
        for i in range(_SCHEMA_SIZE):
            new_order_entries[i].append(entry[i])

    if show_debug: debug.log(lb, "[-] Memory arranged")

    # Check that all the messages are the correct size
    too_large_messages = []
    for enum in enumerate(new_order_entries[2]):
        if len(enum[1]) > _MAX_MESSAGE_LENGTH:
            too_large_messages.append(enum)
    if len(too_large_messages) > 0:
        debug.log (ly, f"[*] VECTOR DATABASE - Could not add messages, as {len(too_large_messages)} too large message{ ' was' if len(too_large_messages) == 1 else 's were'} found" )
        [debug.log(lb, f"                      index: {pair[0]}    message: {pair[1][:100]}") for pair in too_large_messages[:10]]
        

    try:
        for i in range(len(new_order_entries))
        memory_collection.insert(new_order_entries, partition_name=str(channel_id))
        memory_collection.flush()
        if show_debug: debug.log(lg, f"[-] VECTOR DATABASE -Embedding ( backet, message ): {total_amount_of_batches} {i}")
        return True
    except Exception as e:
        debug.log(ly,  "[*] VECTOR DATABASE - Inserting messages failed")
      # debug.log(lb, f"                      first entry: {new_order_entries[][0]}")
        debug.log(lb, f"                      exception  : {e}",        )
        return
    


def drop_messages(channel_id, entry_ids):
    global memory_collection

    expr = "id in " + str(entry_ids)

    if memory_collection.has_partition(str(channel_id)):
        try:    
            memory_collection.delete(expr, partition_name=str(channel_id))
            debug.log(lg, f"[#] VECTOR DATABASE - Removed {len(entry_ids[0])} messages")
            return True
        except Exception as e:
            debug.log(ly,  "[*] VECTOR DATABASE - Removing messages failed")
            debug.log(lb, f"                      exception  : {e}",       )

        


def DROP_ALL_MEMORY():
    global memory_collection
    if utility.has_collection(_COLLECTION_NAME):
        utility.drop_collection(_COLLECTION_NAME)
        debug.log(lg, f"[#] VECTOR DATABASE - COLLECTION DROPPED")


def create_index():
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


def search(channel_id, vectors=None, expr=None):
    global memory_collection

    if vectors is None and expr is None:
        debug.log(ly, "[*] VECTOR DATABASE - Failed to search database, as both vectors and expresion were invalid")
        return
    
    search_param = {
        "data"              :   vectors,
        "anns_field"        :   "embedding",
        "param"             :   {"metric_type": "L2", "params": {"nprobe": 10}},
        "limit"             :   10,
        "expr"              :   expr,
        "partition_names"   :   [str(channel_id)],
        "output_fields"     :   ["author", "message"]
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
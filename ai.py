import openai, os, time # , tiktoken
import debug
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

TESTING_WRITE_TO_FILE = True


# def get_token_amount(message):
    

# the added * 2 is there to get a more accurate answer for this kind of usage, as Discord messages aren't like typical paragraphs
def perdict_token_amount_from_string(string, bias=2): 
    return round(1.33333333333333333333333 * len(string.split(" ") * bias))


def embed_messages(messages, debug_info=False, output_result_to_file=False):

    was_string = False

    if type(messages) == str: 
        was_string = True
        messages = [messages]
    for message in messages:
        if type(message) != str:
            debug.log(ly, f"[*] AI - Failed to embed message{ '' if len(messages) == 1 else 's' } because { 'the' if len(messages) == 1 else 'a' } message was not of type string")
            debug.log(ly, f"         invalid message: {message}")
            return

    try:
        result = []    
        saved_time = time.time()
         # rpm = 0                      # Amount of requests inside the current minute
        total_amount_of_batches = 0     # The amount of batches sent to openAI
        message_amount = len(messages)

        while True:
            if EMBEDDING_MAX_BATCH_SIZE*total_amount_of_batches >= len(messages): break
            batch = messages[EMBEDDING_MAX_BATCH_SIZE*total_amount_of_batches:(total_amount_of_batches+1)*EMBEDDING_MAX_BATCH_SIZE]
                 
            response = openai.Embedding.create(model="text-embedding-ada-002", input = batch)
            total_amount_of_batches += 1
            # rpm                   += 1

            for embeddingObject in response.data:
                result.append(embeddingObject.embedding)     

            if output_result_to_file:
                with open("outputs/embedding_responses.json", 'a') as file:
                    file.write(str(response.usage))

            # if debug_info: 
                # color = lb
                # if   response.usage.total_tokens > EMBEDDING_TRUE_MAX_TOKEN_SIZE:   color = lr
                # elif response.usage.total_tokens > EMBEDDING_MAX_TOKEN_SIZE:        color = ly
                # elif response.usage.total_tokens > batch_token_amount:              color = w
                # debug.log(lb, f"[-] AI - Embedding ( perdicted tokens, actual tokens, backet, message ): {batch_token_amount} {color}{response.usage.total_tokens}{lb} {total_amount_of_batches} {i}")
                # debug.log(lb, f"[-] AI - Embedding ( backet, message ): {total_amount_of_batches} {i}")

            # if rpm >= EMBEDDING_RPM: 
            #     delta_time = time.time() - saved_time
            #     if delta_time < 60:
            #         if debug_info: debug.log(w, f"[%] AI - RPM limit reached ({i}, {delta_time})")
            #         time.sleep(61 - delta_time)
            #     saved_time = time.time()
            #     rpm = 0
        debug.log(lg, f"[#] AI - Embedding {message_amount} message{ '' if message_amount == 1 else 's' } completed with {total_amount_of_batches} batch{'' if total_amount_of_batches == 1 else 'es'}")
        if was_string:  return result[0]
        else:           return result
        
    except Exception as e:
        debug.log(ly,                         f"[*] AI - Failed to embed message{ '' if message_amount == 1 else 's' }"  )
        if len(str(e)) > 1000:  debug.log(ly, f"         exception: {str(e)[:50]}...{str(e)[-100:]}"                    )
        else:                   debug.log(ly, f"         exception: {e}"                                                )
        return


def respond(message):

    # message = JAILBREAK_PROMPT + message

    # AI STEPS

    # LOAD LONG-TERM MEMORY FROM MILVUS
    # GET RESPONSE WITH: TEMPLATE + LTM + STM + MESSAGE
    # CHECK MODERATION AND PRINT
    # RETURN ANSWER

    moderation_response = openai.Moderation.create(input=[message])

    chat_response = openai.ChatCompletion.create(
        model       =   "gpt-3.5-turbo",
        messages    =   [{"role": "user", "content": message}],
        temperature =   0.5)
    
    if TESTING_WRITE_TO_FILE:
        with open("res.json", "w") as file:
            file.write(str(chat_response) + "\n\n" + str(moderation_response))


    return chat_response


if __name__ == "__main__":
    pass

    messages = [ "A " * 300 for _ in range(2010) ]
    response3 = openai.Embedding.create(model="text-embedding-ada-002", input = messages)
    print(response3.usage)

    # messages = ["Hello, World!", "My name is BEAN"]
    # print(perdict_token_amount_from_string(messages[0]),
    #       perdict_token_amount_from_string(messages[1]))
    # response1 = openai.Embedding.create(model="text-embedding-ada-002", input = messages[0])
    # response2 = openai.Embedding.create(model="text-embedding-ada-002", input = messages[1])
    # response3 = openai.Embedding.create(model="text-embedding-ada-002", input = messages)

    # print(response1.usage, response2.usage, response3.usage)

    # message = "Describe to me the evolution of penguins and their history."       # 16
    
    # enc = tiktoken.get_encoding("cl100k_base")
    # sus = enc.encode(message)
    # sas = enc.decode(sus)
    # print(len(sus))
    # print(sus)
    # print(sas)


    # chat_response = openai.ChatCompletion.create(
    #     model       =   "gpt-3.5-turbo",
    #     messages    =   [{"role": "user", "content": message}],
    #     temperature =   0.5)
    
    # print(chat_response.usage)

    # response = respond("Write a essay about penguins and their evolutionary history.")

    # chat_response = response["choices"][0]

    # print()
    # print(chat_response["finish_reason"])
    # print(f'ROLE ({chat_response["message"]["role"]}) : {chat_response["message"]["content"]}')
    # print(f'{chat_response["message"]["role"]} : {chat_response["message"]["content"]}')
    # print()
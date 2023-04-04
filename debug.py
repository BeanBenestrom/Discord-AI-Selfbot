import sys, time, colorama
from colorama import Fore


w  = Fore.WHITE
lb = Fore.LIGHTBLACK_EX
lg = Fore.LIGHTGREEN_EX
ly = Fore.LIGHTYELLOW_EX
lr = Fore.LIGHTRED_EX


saved_time  = None
initialized = False


# def print_c(color, *args):
#     text = 
#     for 

# def print_white  (*args):   print(w , args)
# def print_gray   (*args):   print(lb, args)
# def print_green  (*args):   print(lg, args)
# def print_yellow (*args):   print(ly, args)
# def print_red    (*args):   print(lr, args)

def print_line(string, color=lb, line_length=50):
    length = line_length - len(string)
    if length < 0: length = 0
    print(color, string + "-" * length)


# time show, aka. return proper spacing, with time
def ts(): 
    def get_time_string(secs):
        seconds, decimals = str(secs).split('.')

        temp_decimal = ""
        for i in range(2):
            if len(decimals) > i: temp_decimal += decimals[0]
            else:                 temp_decimal += "0"
        
        decimals = temp_decimal
        seconds  = " " * (3 - len(seconds) ) + seconds

        return f"{seconds}.{decimals}"

    secs = get_measured_time()
    if secs < 1: return f"{get_time_string(secs * 1000)}ms"
    else:        return f"{get_time_string(secs)}s "

    # 000.00ms
    # 000.00s
    
    # 000.000000s

    # return f"{secs}"


# time null, aka. return proper spacing, but no time
def tn():
    return " " * 8


def reset_time():
    global saved_time
    saved_time = time.time()


def get_measured_time():
    global saved_time
    new_time = time.time()
    deltatime = new_time - saved_time
    saved_time = new_time
    return deltatime


def container(func):
    def wrapper(*args):
        print_line(f"{func.__name__} ")
        start_time_container = time.time()
        reset_time()
        func(*args)
        end_time_container = time.time()
        print_line(f"{end_time_container - start_time_container}s ")
        print()

    return wrapper


def logt(color, string):
    print(w, '-', color, f"{ts()} {color}{string}", w)


def log(color, string):
    print(w, '-', color, f"{tn()} {color}{string}", w)
    # if show_time:   print('-', color, f"{ts()} {color}{string}")
    # else:           print('-', color, f"{tn()} {color}{string}")    # M4HXXX


def init():
    global saved_time, initialized
    if not initialized:
        initialized = True
        saved_time = time.time()
        colorama.init()


def deinit():
    global initialized
    initialized = False
    colorama.deinit()
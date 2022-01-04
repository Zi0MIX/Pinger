import os
import sys
import getpass
import re
from time import sleep
from time import ctime
from pythonping import ping

address_list = []
custom_address_list = []
user = getpass.getuser()

definitions = {
    "y/n": ["y", "n"],
    "ping_freq": range(1, 301),
    "ping_threshold": range(1, 2000) # Exclude 2000 as that's the timeout code
}

defaults = {
    "virgin_list": [],
    "address_list": ["8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"], # DNS providers, in order Google, Cloudflare, Cisco and Quad9
    "win_logfile_path": rf"C:\Users\{user}\Documents\Pinger",
    "sleep": 2,
    "ping_threshold": 50.00,
}

errors = {
    "y/n input": "Wrong answer! Please input Y for Yes or N for No",
    "max_addresses": "You reached a max amount of custom addresses.",
    "critical_addresses": "A critical error occured, no addresses to ping. Press ENTER to close the program.",
    "ping": "Something went wrong, not all pings were sent.",
    "analytics": "An error occured while analyzing the result.",
    "argument": "Provided argument is wrong, try again!",
}

questions = {
    "def_address": "Would you like to use default addresses? (Y/N) ",
    "def_sleep": "Would you like to use default time between pings? (Y/N) ",
    "def_logfile": "Would you like to use default logfile location? (Y/N) ",
    "def_threshold": "Would you like to use default limit, above which pings get logged? (Y/N) ",
    "confirm_config": "Would you like to proceed or would you like to configure again? (Y to continue, N to config) ",
}

##### GENERAL FUNCTIONS #####

def validation(user_input, error, definition_key):
    if user_input not in definitions[definition_key]:
        return error
    else:
        return


def choice(user_input, option1="y", option2="n", option3=None, t_output=None):
    if user_input == option1:
        return True
    elif user_input == option2:
        return False
    elif user_input == option3:
        return t_output


def a_question(question, error, definition_key, option1="y", option2="n", option3=None, t_output=None):
    while True:
        t_question = input(question).lower()
        val = validation(t_question, error, definition_key)
        if val != None:
            print(val)
            continue
        return choice(t_question, option1, option2, option3, t_output)


def open_log_file(default_path):
    try:
        t_log_file = open(rf"{default_path}\event log.txt", "a")
    except FileNotFoundError:
        os.mkdir(default_path)
        t_log_file = open(rf"{default_path}\event log.txt", "x")
        print(f"Log file created in {default_path}")
    return t_log_file


def analyze_response(response, ip_in):
    if re.search("Request timed out", response):
        timeout = True
    elif re.search("Reply from", response):
        timeout = False
    if timeout:
        ip, time = ip_in, 2000.00
    elif not timeout: 
        ip = cleanup(response, "ip", 1)
        time = cleanup(response, "time", 1)
        if str(ip) != str(ip_in):
            print(f"""{errors["analytics"]} code ip_not_equal, ip = {ip}, ip_in = {ip_in}""")
            return
    else:
        print(f"""{errors["analytics"]} code unknown_result""")
        return
    
    return [str(ip), float(time)]


def cleanup(t_input, case, argument=None):
    if argument == 1:
        t_reg = re.split(" ", t_input)
        if case == "ip":
            t_ip = t_reg[2]
            t_ip = t_ip.replace(",", "")
            return t_ip
        elif case == "time":
            t_time = t_reg[6]
            t_time = t_time.replace("ms", "")
            t_time = t_time.replace("Round", "")
            return t_time


##### CONFIGURATION #####

while True:
    use_default_address = a_question(questions["def_address"], errors["y/n input"], "y/n")

    first_address = True
    if use_default_address: 
        max_list_len = 6
    else: 
        max_list_len = 10
    while True:
        while True:
            if not use_default_address and first_address:
                skip_question = True
            else:
                skip_question = False

            if first_address and not use_default_address:
                output = "Would you like to add your own, custom address? (Y/N) "
            else:
                output = "Would you like to add another address? (Y/N) "

            if first_address and skip_question:
                append_custom_address = True
                break
            else:
                append_custom_address = a_question(output, errors["y/n input"], "y/n")
                break

        if not append_custom_address:
            break
        else:
            first_address = False
            address = input("Type address of the host you want to ping ")
            custom_address_list.append(address)
            if len(custom_address_list) >= max_list_len:
                print(errors["max_addresses"])
                break

    use_default_sleep = a_question(questions["def_sleep"], errors["y/n input"], "y/n")
    if not use_default_sleep:
        while True:
            print("Provide time between pings in seconds (range 1 to 300)")
            ping_freq = int(input("> "))
            if ping_freq in definitions["ping_freq"]:
                break
            else:
                print(errors["argument"])
    else:
        ping_freq = defaults["sleep"]

    use_default_logfile = True #a_question(questions["def_logfile"], errors["y/n input"], "y/n")
    if not use_default_logfile:
        pass # Maybe one day
    else:
        logfile_path = defaults["win_logfile_path"]
    
    use_default_threshold = a_question(questions["def_threshold"], errors["y/n input"], "y/n")
    if not use_default_threshold:
        while True:
            print("Type in new ping limit (between 1 and 1999).")
            ping_threshold = int(input("> "))
            if ping_threshold in definitions["ping_threshold"]:
                break
            else:
                print(errors["argument"])
    else:
        ping_threshold = defaults["ping_threshold"]
            
    if use_default_address:
        for x in defaults["address_list"]:
            address_list.append(x)

    if custom_address_list != []:
        for x in custom_address_list:
            address_list.append(x)

    if address_list == []:
        input(errors["critical_addresses"])
        sys.exit()

    print("The program will ping these addresses:")
    for x in address_list:
        print(x)

    is_configuration_successful = a_question(questions["confirm_config"], errors["y/n input"], "y/n")
    if is_configuration_successful:
        break
    else:
        address_list = []
        custom_address_list = []

##### PROCESSOR #####
while True:
    ip_id = 0
    for x in address_list:
        a_ping = ping(x, verbose=False, count = 1)
        analyzed = analyze_response(str(a_ping), address_list[ip_id])
        ip_id += 1
        if analyzed[1] >= ping_threshold:
            print(f"Ping higher than {ping_threshold} to {analyzed[0]} at {ctime()} is {analyzed[1]}ms.")
            logfile = open_log_file(logfile_path)
            if analyzed[1] == 2000.00:
                logfile.write(f"""{ctime()} Ping to {analyzed[0]} timed out.
""")
            else:
                logfile.write(f"""{ctime()} Ping to {analyzed[0]} is {analyzed[1]}.
""")

    sleep(ping_freq) 
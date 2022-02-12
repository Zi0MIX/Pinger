import os, sys, getpass, re, subprocess
from time import ctime, time, sleep, localtime, mktime
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
    "win_logfile_path": f"C:\\Users\\{user}\\Documents\\Pinger",
    "sleep": 2,
    "ping_threshold": 80.00,
}

errors = {
    "y/n input": "Wrong answer! Please input Y for Yes or N for No",
    "max_addresses": "You reached a max amount of custom addresses.",
    "critical_addresses": "A critical error occured, no addresses to ping. Press ENTER to close the program.",
    "ping": "Something went wrong, not all pings were sent.",
    "analytics": "An error occured while analyzing the result.",
    "argument": "Provided argument is wrong, try again!",
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


def analyze_response(response, ip_in, firewall):
    reg_timeout = re.compile("Request timed out")
    reg_reply = re.compile("Reply from")

    arg = 2
    if firewall:
        arg = 1
        
    if re.search(reg_timeout, response):
        timeout = True
    elif re.search(reg_reply, response):
        timeout = False

    if timeout:
        ip, time = ip_in, 2000.00
    elif not timeout: 
        ip = cleanup(response, "ip", arg)
        time = cleanup(response, "time", arg)
        if str(ip) != str(ip_in):
            print(f"""{errors["analytics"]} code ip_not_equal, ip = {ip}, ip_in = {ip_in}""")
            return 0
    else:
        print(f"""{errors["analytics"]} code unknown_result""")
        return 0
    
    return [str(ip), float(time)]


def cleanup(t_input, case, argument=2):
    t_reg = re.split(" ", t_input)
    if case == "ip":
        t_ip = t_reg[argument]
        if argument == 2:
            t_ip = t_ip.replace(",", "")
        return t_ip
    elif case == "time":
        # print(t_reg)
        pos = 6
        if argument == 1:
            pos = 10
        t_time = t_reg[pos]
        t_time = t_time.replace("ms", "")
        if argument == 1:
            t_time = t_time.replace("time=", "")
        elif argument == 2:
            t_time = t_time.replace("Round", "")
        return t_time


def add_one(t_number, last_time_timeout):
    if last_time_timeout:
        t_number += 1
        return t_number
    else:
        return 0


def checkup(t_time):
    if t_time == 0.0:
        t_time = time()

    if time() >= t_time + 1800:
        print(f"{ctime()} the app is stable.")
        return time()
    else:
        return t_time


# def calc_time(t_arg): 
#     t_now = localtime()
#     t_secs = mktime(t_now)
#     t_desire = ctime(t_secs + t_arg)
#     return


##### CONFIGURATION #####

while True:
    use_default_address = a_question("Would you like to use default addresses? (Y/N) ", errors["y/n input"], "y/n")

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

    use_default_sleep = a_question("Would you like to use default time between pings? (Y/N) ", errors["y/n input"], "y/n")
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

    use_default_logfile = True #a_question("Would you like to use default logfile location? (Y/N) ", errors["y/n input"], "y/n")
    if not use_default_logfile:
        pass # Maybe one day
    else:
        logfile_path = defaults["win_logfile_path"]
    
    use_default_threshold = a_question("Would you like to use default limit, above which pings get logged? (Y/N) ", errors["y/n input"], "y/n")
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

    is_configuration_successful = a_question("Would you like to proceed or would you like to configure again? (Y to continue, N to config) ", errors["y/n input"], "y/n")
    if is_configuration_successful:
        break
    else:
        address_list = []
        custom_address_list = []

##### PROCESSOR #####
time_outs = 0
timed_out = False
timestamp = 0.0

test_timeouts = []
bruh = False
print("Testing ...")
while True:
    firewall_ping = subprocess.Popen("ping 8.8.8.8", stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
    firewall_pull = firewall_ping.communicate()
    for x in firewall_pull:
        if re.search(r"(100% loss)", x):
            if not bruh:
                bruh = True
                sleep(2)
                continue
            test_success = False
            break
    else:
        test_success = True
        break

ip_id = 0
for x in address_list:
    a_ping = ping(x, verbose=False, count=1, payload="32")
    analyzed = analyze_response(str(a_ping), address_list[ip_id], False)
    ip_id += 1

    if analyzed[1] > 999:
        timed_out = True
    else:
        timed_out = False
    test_timeouts.append(timed_out)
    
falses = 0
for x in test_timeouts:
    if x:
        falses += 1

if falses < 4:
    firewall_active = False
else:
    if test_success:
        print("The program is most likely blocked by either local or network firewall.")
        firewall_choice = input("Would you like to continue using alternative method? (Y/N) ").upper()
        print("Do note, alternative method may become unstable over long period of time, please monitor the program.")
        if firewall_choice == "N":
            sys.exit()
        else:
            firewall_active = True

logfile = open_log_file(logfile_path)
print("""Pinging ...""")
print(f"""Results will be saved in a log in {defaults["win_logfile_path"]}\\event log.txt""")
while True:
    ip_id = 0
    for x in address_list:
        if not firewall_active:
            try:
                a_ping = ping(x, verbose=False, count=1, payload="32")
            except OSError:
                print("Network change detected.")
                sleep(10)
                continue
        else:
            ping_temp = subprocess.Popen(f"ping -n 1 {x}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
            a_ping = ping_temp.communicate()

        analyzed = analyze_response(str(a_ping), address_list[ip_id], firewall_active)
        ip_id += 1

        if analyzed == 0:
            input("Press ENTER to close the program")
            sys.exit()
        
        if analyzed[1] >= ping_threshold:
            if analyzed[1] < 2000:
                print(f"Ping higher than {ping_threshold} to {analyzed[0]} at {ctime()} is {analyzed[1]}ms.")
                logfile.write(f"""{ctime()} Ping to {analyzed[0]} is {analyzed[1]}ms. """)
                if analyzed[1] >= 1000:
                    timed_out = True
                else:
                    timed_out = False
            else:
                print(f"Ping to {analyzed[0]} at {ctime()} timed out.")
                logfile.write(f"""{ctime()} Ping to {analyzed[0]} timed out. """)
                timed_out = True

            time_outs = add_one(time_outs, timed_out)

    if time_outs == len(address_list):
        print(f"CRITICAL!!!! ALL SERVERS TIMED OUT AT {ctime()}")
        logfile.write(f"""{ctime()} CRITICAL!!!! ALL SERVERS TIMED OUT """)
    elif time_outs >= len(address_list) / 2:
        print(f"Attention!! At least half of the servers ({time_outs} servers) timed out at {ctime()}")
        logfile.write(f"""{ctime()} Attention!! At least half of the servers ({time_outs} servers) timed out """)  

    time_outs = 0
    timed_out = False

    timestamp = checkup(timestamp)
    sleep(ping_freq)

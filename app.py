import os, sys, getpass, re, subprocess
from time import ctime, time, sleep, localtime, mktime
from pythonping import ping

address_list = []
custom_address_list = []
user = getpass.getuser()
reg_timeout = re.compile("Request timed out")
reg_reply = re.compile("Reply from")

definitions = {
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
    "input": "Wrong answer! Please double check if your answer is right.",
    "int": "Wrong answer!. Please only use digits.",
    "index": "Length of the list with definitions is not right.",
    "max_addresses": "You reached a max amount of custom addresses.",
    "critical_addresses": "A critical error occured, no addresses to ping. Press ENTER to close the program.",
    "ping": "Something went wrong, not all pings were sent.",
    "analytics": "An error occured while analyzing the result.",
    "argument": "Provided argument is wrong, try again!",
}

##### GENERAL FUNCTIONS #####

def ask(t_question, t_error, t_lower_it=True, t_definition=["y", "n", None], t_output=None):
    """Function will ask user for the input(str), then validate it against provided list of definitions and return True/False/Output depending the selection."""
    while True:
        t_answer = str(input(t_question))
        if t_lower_it:
            t_answer = t_answer.lower()
        
        if t_answer not in t_definition:
            print(t_error)
            continue
        break

    while True:
        try:
            if t_answer == t_definition[0]:
                return True
            elif t_answer == t_definition[1]:
                return False
            elif t_answer == t_definition[2]:
                return t_output
        except IndexError:
            print(errors['index'])
            sys.exit()


def open_log_file(default_path):
    """Function will open a log file from provided system path."""
    try:
        t_log_file = open(rf"{default_path}\event log.txt", "a")
    except FileNotFoundError:
        os.mkdir(default_path)
        t_log_file = open(rf"{default_path}\event log.txt", "x")
        print(f"Log file created in {default_path}")
    return t_log_file


def analyze_response(response, ip_in, firewall, reg_args):
    """Function will analyze pings and return latency with an ip address."""
    arg = 2
    if firewall:
        arg = 1
        
    if re.search(reg_args[1], response):
        timeout = True
    elif re.search(reg_args[0], response):
        timeout = False

    if timeout:
        ip, time = ip_in, 2000.00
    elif not timeout: 
        ip = cleanup(response, "ip", arg)
        time = cleanup(response, "time", arg)
        if str(ip) != str(ip_in):
            print(f"{errors['analytics']} code ip_not_equal, ip = {ip}, ip_in = {ip_in}")
            return 0
    else:
        print(f"{errors['analytics']} code unknown_result")
        return 0
    
    return [str(ip), float(time)]


def cleanup(t_input, case, argument=2):
    """Function will use regex to modify provided strings so they can be processed further."""
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
    """Function will add a number if provided condition is set to True."""
    if last_time_timeout:
        t_number += 1
        return t_number
    else:
        return 0


def checkup(t_time):
    """Function will make a print if nothing's been printed for last 10 minutes. It'll return True and a timestamp of the print. If print wasn't executed, function will return None."""
    if time() >= t_time + 600:
        print(f"{ctime()} the app is stable.")
        return [True, time()]
    else:
        return [False, None]


##### CONFIGURATION #####

while True:
    while True:
        use_default_address = ask("Would you like to use default addresses? (Y/N/LIST) ", errors['input'], t_definition=["y", "n", "list"],t_output="8.8.8.8 | 1.1.1.1 | 208.67.222.222 | 9.9.9.9")
        if use_default_address not in [True, False]:
            print(use_default_address)
            continue
        break

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
                append_custom_address = ask(output, errors['y/n input'])
                break

        if not append_custom_address:
            break
        else:
            first_address = False
            address = input("Type address of the host you want to ping ")
            custom_address_list.append(address)
            if len(custom_address_list) >= max_list_len:
                print(errors['max_addresses'])
                break

    use_default_sleep = ask(f"Would you like to use default time between pings? Default is {defaults['sleep']} (Y/N) ", errors['y/n input'])
    if not use_default_sleep:
        while True:
            print("Provide time between pings in seconds (range 1 to 300)")
            ping_freq = int(input("> "))
            if ping_freq in definitions['ping_freq']:
                break
            else:
                print(errors['argument'])
    else:
        ping_freq = defaults['sleep']

    use_default_logfile = True #a_question("Would you like to use default logfile location? (Y/N) ", errors["y/n input"], "y/n")
    if not use_default_logfile:
        pass # Maybe one day
    else:
        logfile_path = defaults['win_logfile_path']
    
    use_default_threshold = ask(f"Would you like to use default limit, above which pings get logged? Default is {defaults['ping_threshold']} (Y/N) ", errors['y/n input'])
    if not use_default_threshold:
        while True:
            print("Type in new ping limit (between 1 and 1999).")
            try:
                ping_threshold = float(input("> "))
            except ValueError:
                print(errors['int'])
                continue

            if ping_threshold in definitions['ping_threshold']:
                break
            else:
                print(errors['argument'])
    else:
        ping_threshold = defaults['ping_threshold']
            
    if use_default_address:
        for x in defaults['address_list']:
            address_list.append(x)

    if custom_address_list != []:
        for x in custom_address_list:
            address_list.append(x)

    if address_list == []:
        input(errors['critical_addresses'])
        sys.exit()

    print("The program will ping these addresses:")
    for x in address_list:
        print(x)

    is_configuration_successful = ask("Would you like to proceed or would you like to configure again? (Y to continue, N to config) ", errors['y/n input'])
    if is_configuration_successful:
        break
    else:
        address_list = []
        custom_address_list = []

##### PROCESSOR #####
time_outs = 0
timed_out = False
print_timestamp = time()

test_timeouts = []
bruh = False
print("Testing ...")
while True:                     # Run a test through pipes to define if pings can even come out
    firewall_ping = subprocess.Popen("ping 8.8.8.8", stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
    firewall_pull = firewall_ping.communicate()
    for x in firewall_pull:     # Analyze if 100% packet loss occured
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
for x in address_list:          # See if pings can get through using main method
    a_ping = ping(x, verbose=False, count=1, payload="32")
    analyzed = analyze_response(str(a_ping), address_list[ip_id], False, [reg_reply, reg_timeout])
    ip_id += 1

    if analyzed[1] > 999:
        timed_out = True
    else:
        timed_out = False
    test_timeouts.append(timed_out)
    
falses = 0                      # Review the results and ask user about methodology
for x in test_timeouts:
    if x:
        falses += 1

if falses < 4:
    firewall_active = False
else:                           # If it's determined firewall might be blocking the program, let user quit or agree to alternative method.
    if test_success:
        print("The program is most likely blocked by either local or network firewall.")
        firewall_choice = ask("Would you like to continue using alternative method? (Y/N) ", errors['y/n input'])
        if not firewall_choice:
            sys.exit()

        print("Do note, alternative method may become unstable over long period of time, please monitor the program.")
        firewall_active = True

logfile = open_log_file(logfile_path)
print("Pinging ...")
print(f"Results will be saved in a log in {defaults['win_logfile_path']}\\event log.txt")
while True:
    ip_id = 0
    network_change = False
    did_print = False
    for x in address_list:      # Ping with either method and process the ping.
        if not firewall_active:
            try:
                a_ping = ping(x, verbose=False, count=1, payload="32")
            except OSError:
                print("Network change detected. Waiting 15 seconds")
                network_change = True
                sleep(15)
                break
        else:
            ping_temp = subprocess.Popen(f"ping -n 1 {x}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
            a_ping = ping_temp.communicate()            

        analyzed = analyze_response(str(a_ping), address_list[ip_id], firewall_active, [reg_reply, reg_timeout])
        ip_id += 1

        if analyzed == 0:
            input("Press ENTER to close the program")
            sys.exit()
        
        if analyzed[1] >= ping_threshold:   # Print and log high ping / timeout events
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

            print_timestamp = time()    # Register a print
            time_outs = add_one(time_outs, timed_out)

    if network_change:          # Restart the loop to avoid errors.
        logfile.write(f"""{ctime()} Network change exception occured. """)
        continue

    if time_outs == len(address_list):
        print(f"CRITICAL!!!! ALL SERVERS TIMED OUT AT {ctime()}")
        logfile.write(f"""{ctime()} CRITICAL!!!! ALL SERVERS TIMED OUT """)
    elif time_outs >= len(address_list) / 2:
        print(f"Attention!! At least half of the servers ({time_outs} servers) timed out at {ctime()}")
        logfile.write(f"""{ctime()} Attention!! At least half of the servers ({time_outs} servers) timed out """)  

    time_outs = 0
    timed_out = False

    checkup_out = checkup(print_timestamp)
    if checkup_out[0]:
        print_timestamp = checkup_out[1]
    
    sleep(ping_freq)

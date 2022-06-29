##### GENERAL FUNCTIONS #####
def get_definitions():
    return {
        "ping_freq": range(1, 301),
        "ping_threshold": range(1, 2000), # Exclude 2000 as that's the timeout code
        "cfg_len": 6,   # Change if config changes
        "forbidden_symbols": ["*", "?", "\"", "<", ">", "|"],
        "drive_letters": ["C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    }


def get_defaults():
    from getpass import getuser
    return {
        "virgin_list": [],
        "address_list": ["8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"], # DNS providers, in order Google, Cloudflare, Cisco and Quad9
        "win_logfile_path": f"C:\\Users\\{getuser()}\\Documents\\Pinger",
        "sleep": 2,
        "ping_threshold": 80.00,
        "print_all": False,
        "print_average": False,
    }


class Config:
    def __init__(self):
        from sys import executable
        from os.path import dirname

        self.definitions = get_definitions()
        self.defaults = get_defaults()
        self.path = str(executable)
        list_path = self.path.split("\\")
        exe_name = list_path[-1]
        exe_index = self.path.rfind("\\")
        if exe_name == "python.exe":
            self.path = dirname(__file__)
        else:
            self.path = self.path[:exe_index]
        # input(f"{self.path}, name = {exe_name}")


    def open_cfg(self):
        while True:
            try:
                configuration_file = open(f"{self.path}\\config.cfg" , "r")
                data = configuration_file.read()
                break
            except FileNotFoundError:
                Config().build_cfg()
            finally:
                try:
                    configuration_file.close()
                except UnboundLocalError:
                    pass
        return data

    
    def build_cfg(self):
        t_bulid = open(f"{self.path}\\config.cfg", "x")
        print(f"Config file created in {self.path}")
        t_bulid.close()
        return


    def verify_cfg(self):
        read_file = Config().read_cfg(1, return_all=True)
        with open(f"{self.path}\\config.cfg" , "w") as f:
            # print(f"len of cfg {len(Config().read_cfg(1, return_all=True))}")
            if len(read_file) != self.definitions["cfg_len"]:
                print("Wrong lenght of the config. Generating a new one.")
                f.write("")

                # Format addresses
                t_addresses = ""
                for x in self.defaults["address_list"]:
                    t_addresses += f"{x} "
                t_addresses = t_addresses[:-1]

                # Change if config changes
                t_clean_cfg = f"""logfile_path = "{self.defaults["win_logfile_path"]}"
addresses = "{t_addresses}"
sleep = "{self.defaults["sleep"]}"
ping_threshold = "{self.defaults["ping_threshold"]}"
print_all = "{convert_int_bool(self.defaults["print_all"])}"
print_average = "{convert_int_bool(self.defaults["print_average"])}"
"""
                f.write(t_clean_cfg)
                f.close()
                return
                
            else:
                logfile_error = False
                t_syspath = cleanup(read_file[0], "syspath")
                if t_syspath != read_file[0]:
                    logfile_error = True

                check_for_drive_letter = t_syspath.split(":")
                if len(check_for_drive_letter) not in [1, 2]:
                    logfile_error = True
                if check_for_drive_letter[0] not in self.definitions["drive_letters"]:
                    logfile_error = True

                if logfile_error:
                    print("Error with logfile path detected. Attempting to fix.")
                    t_syspath = "C:" + check_for_drive_letter[1]

                # Change if config changes
                t_overwrite_cfg = f"""logfile_path = "{t_syspath}"
addresses = "{read_file[1]}"
sleep = "{read_file[2]}"
ping_threshold = "{read_file[3]}"
print_all = "{read_file[4]}"
print_average = "{read_file[5]}"
"""
                f.write(t_overwrite_cfg)
                f.close()
                return


    def read_cfg(self, read_line, return_all=False):
        t_properties = []
        with open(f"{self.path}\\config.cfg" , "r", encoding="utf-8") as f:
            t_cfg = f.read()
            t_properties = read_arguments(t_cfg)
            # print(len(t_properties))
        if return_all:
            return t_properties
        return str(t_properties[read_line - 1])


def read_arguments(t_input, split1="\n", split2="\""):
    """Function serves as a slave to read_cfg, it'll pull arguments from config lines."""
    t_list = []
    t_fulldata = str(t_input).split(split1)
    for x in t_fulldata:
        t_value = x.split(split2)
        if len(t_value) != 3:   # Check for an empty line
            continue
        t_list.append(t_value[1])
    return t_list


def ask(t_question, t_error, t_lower_it=True, t_definition=["y", "n", None], t_output=None):
    """Function will ask user for the input(str), then validate it against provided list of definitions and return True/False/Output depending the selection."""
    from sys import exit
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
            print("Length of the list with definitions is not right.")
            exit()


def write_to_log(default_path, data):
    """Function will check if log file exists in the given path. If it does, it'll log given data to it, if it doesn't it'll create the file first."""
    from os import mkdir
    while True:
        try:
            with open(f"{default_path}\\pinger_log.log", "a", encoding="utf-8") as f:
                f.write(data)
            break
        except FileNotFoundError:
            mkdir(default_path)
            create_file = open(f"{default_path}\\pinger_log.log", "x")
            print(f"Log file created in {default_path}")
            create_file.close()
    return


def analyze_response(response, ip_in, firewall, reg_args):
    """Function will analyze pings and return latency with an ip address."""
    from re import search
    arg = 2
    if firewall or DEBUG_MODE:
        arg = 1
        
    if search(reg_args[1], response):
        timeout = True
    elif search(reg_args[0], response):
        timeout = False

    if timeout:
        ip, time = ip_in, 2000.00
    elif not timeout: 
        ip = cleanup(response, "ip", arg)
        time = cleanup(response, "time", arg)
        if str(ip) != str(ip_in):
            print(f"An error occured while analyzing the result. Code: ip_not_equal, ip = {ip}, ip_in = {ip_in}")
            return 0
    else:
        print(f"An error occured while analyzing the result. Code: unknown_result")
        return 0
    
    return [str(ip), float(time)]


def cleanup(t_input, case, argument=2):
    """Function will use regex to modify provided strings so they can be processed further."""
    from re import split
    if case != "syspath":
        t_reg = split(" ", t_input)

    if case == "ip":
        t_ip = t_reg[argument]
        if argument == 2:
            t_ip = t_ip.replace(",", "")
        return t_ip
    elif case == "time":
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
    elif case == "syspath":
        t_reg = str(t_input)
        t_reg = t_reg.replace("/", "\\")
        for x in get_definitions()["forbidden_symbols"]:
            t_reg = t_reg.replace(x, "")
        return t_reg           


def add_one(t_number, last_time_timeout):
    """Function will add a number if provided condition is set to True."""
    if last_time_timeout:
        t_number += 1
        return t_number
    else:
        return 0


def checkup(t_time, t_average, t_wait=600):
    """Function will make a print if nothing's been printed for last 10 minutes. It'll return True and a timestamp of the print. If print wasn't executed, function will return None."""
    from time import ctime, time, sleep
    readable_wait = t_wait * 60     # Convert to minutes
    a_string = "minutes"
    if t_wait < 120:                # Stay on seconds if it's less than 2 minutes
        readable_wait = t_wait
        a_string = "seconds"

    if time() >= t_time + t_wait and t_average == 0:
        print(f"{ctime()} stability check - no prints for past {readable_wait} {a_string}.")
        return [True, time()]
    elif time() >= t_time + 300 and t_average > 0:
        print(f"{ctime()} your current ping average is {t_average}.")
        return [True, time()]
    else:
        return [False, None]


def convert_int_bool(t_input):
    """Function will convert bool to int and int to bool"""
    if isinstance(t_input, bool):
        if t_input:
            return 1
        return 0

    elif isinstance(t_input, str):
        try:
            t_input = int(t_input)
            if t_input == 0:
                return False
            else:
                return True
        except ValueError:
            return None

    elif isinstance(t_input, int):
        if t_input == 0:
            return False
        else:
            return True

    return None


def main():
    import sys, getpass, re, subprocess
    from time import sleep, time, ctime
    from pythonping import ping

    address_list = []
    custom_address_list = []
    reg_timeout = re.compile("Request timed out")
    reg_reply = re.compile("Reply from")
    defaults = get_defaults()
    definitions = get_definitions()

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
        "cfg_logfile": "Wrong path to the log file, applying default.",
    }    

    while True:
        use_config = ask("Would you like to use config file? (Y/N) ", errors['input'])
        if use_config:
            Config().open_cfg()
            Config().verify_cfg()

        # Address list
        if use_config:
            all_addresses = Config().read_cfg(2)
            list_of_addresses = str(all_addresses).split(" ")
            amount_of_addresses_from_cfg = len(list_of_addresses)
            if amount_of_addresses_from_cfg > 10:
                input(errors["max_addresses"])
                sys.exit()
            for x in list_of_addresses:
                custom_address_list.append(x)
            use_default_address = False
        else:            
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

        # Sleep
        if use_config:
            try:
                ping_freq = Config().read_cfg(3)
                ping_freq = int(ping_freq)
            except ValueError:
                ping_freq = defaults['sleep']
                print("Inproper value in the config. Applying default 'sleep' value.")
        else:
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

        # Logfile
        if use_config:
            logfile_error = False
            logfile_path = Config().read_cfg(1)
            logfile_path = cleanup(logfile_path, "syspath")

        else:
            logfile_path = defaults['win_logfile_path']
        
        # Threshold
        if use_config:
            try:
                ping_threshold = float(Config().read_cfg(4))
            except ValueError:
                ping_threshold = defaults['ping_threshold']
                print("Inproper value in the config. Applying default 'ping_threshold' value.")
        else:
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

        # Print All
        if use_config:
            do_print_all = convert_int_bool(Config().read_cfg(5))
            if do_print_all == None:
                do_print_all = defaults['print_all']
                print("Inproper value in the config. Applying default 'print_all' value.")
            
        else:
            do_print_all = ask("Would you like to see all results even below set limit? (Y/N) ", errors['y/n input'])

        # Print averages
        if not do_print_all:    # Pointless to have it run if all pings are printed
            if use_config:
                print_averages = convert_int_bool(Config().read_cfg(6))
                if print_averages == None:
                    print_averages = defaults['print_average']
                    print("Inproper value in the config. Applying default 'print_average' value.")

            else:
                print_averages = ask("Would you like to see information about average ping? (Y/N) ", errors['y/n input']) 
        else:
            print_averages = False

        # Final     
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

        if not use_config:
            is_configuration_successful = ask("Would you like to proceed or would you like to configure again? (Y to continue, N to config) ", errors['y/n input'])
            if is_configuration_successful:
                break
            else:
                address_list = []
                custom_address_list = []
        else:
            break

    ##### PROCESSOR #####
    time_outs = 0
    timed_out = False
    print_timestamp = time()
    count_pings = 0
    ping_total = 0
    results = []

    test_timeouts = []
    bruh = False
    if not DEBUG_MODE:
        print("Testing ...")
        while not DEBUG_MODE:   # Run a test through pipes to define if pings can even come out
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
    else:
        firewall_active = True

    print("Pinging ...")
    print(f"Results will be saved in a log in {logfile_path}\\pinger_log.log")
    while True:
        ip_id = 0
        network_change = False
        did_print = False
        for x in address_list:      # Ping with either method and process the ping.
            if not firewall_active and not DEBUG_MODE:
                try:
                    a_ping = ping(x, verbose=do_print_all, count=1, payload="32")
                except OSError:
                    print("Network change detected. Waiting 15 seconds")
                    network_change = True
                    sleep(15)
                    break
            else:
                ping_temp = subprocess.Popen(f"ping -n 1 {x}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
                a_ping = ping_temp.communicate()
                if do_print_all:
                    if a_ping[1] == "":     # Avoid error msg
                        temp_data_from_pipe = str(a_ping[0]).split("\n")
                        for x in temp_data_from_pipe:
                            print(x)            

            analyzed = analyze_response(str(a_ping), address_list[ip_id], firewall_active, [reg_reply, reg_timeout])
            ip_id += 1

            if analyzed == 0:
                input("Press ENTER to close the program")
                sys.exit()

            results.append(int(analyzed[1]))

            if print_averages:
                if len(results) > 10000:
                    new_results = results[-10000:]
                    results = new_results     
                ping_average = sum(results) // len(results)
            else:
                ping_average = 0
            
            if analyzed[1] >= ping_threshold:   # Print and log high ping / timeout events
                if analyzed[1] < 2000:
                    print(f"Ping higher than {ping_threshold} to {analyzed[0]} at {ctime()} is {analyzed[1]}ms.")
                    data = (f"""{ctime()} - Ping to {analyzed[0]} is {analyzed[1]}ms ({round(analyzed[1] - ping_threshold, 1)} over threshold).\n""")
                    write_to_log(logfile_path, data)
                    if analyzed[1] >= 1000:
                        timed_out = True
                    else:
                        timed_out = False
                else:
                    print(f"Ping to {analyzed[0]} at {ctime()} timed out.")
                    data = (f"""{ctime()} - Ping to {analyzed[0]} timed out.\n""")
                    write_to_log(logfile_path, data)
                    timed_out = True

                print_timestamp = time()    # Register a print
                time_outs = add_one(time_outs, timed_out)

        if network_change:          # Restart the loop to avoid errors.
            data = (f"""{ctime()} Network change exception occured.\n""")
            write_to_log(logfile_path, data)
            continue

        if time_outs == len(address_list):
            print(f"CRITICAL!!!! ALL SERVERS TIMED OUT AT {ctime()}")
            data = (f"""{ctime()} CRITICAL!!!! ALL SERVERS TIMED OUT\n""")
            write_to_log(logfile_path, data)
        elif time_outs >= len(address_list) / 2 and len(address_list) > 2:
            print(f"Attention!! At least half of the servers ({time_outs} servers) timed out at {ctime()}")
            data = (f"""{ctime()} Attention!! At least half of the servers ({time_outs} servers) timed out\n""")  
            write_to_log(logfile_path, data)

        time_outs = 0
        timed_out = False

        if not do_print_all:
            checkup_out = checkup(print_timestamp, ping_average)
            if checkup_out[0]:
                print_timestamp = checkup_out[1]
        
        sleep(ping_freq)


if __name__ == "__main__":
    DEBUG_MODE = False
    main()
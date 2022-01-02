#pip install pythonping
import os
import sys
import getpass # To obtain OS username
import pythonping 

address_list = []
custom_address_list = []
user = getpass.getuser()

definitions = {
    "y/n": ["y", "n"],
}

defaults = {
    "virgin_list": [],
    "address_list": ["8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"], # DNS providers, in order Google, Cloudflare, Cisco and Quad9
    "win_logfile_path": rf"C:\Users\{user}\Documents\Pinger",
    "sleep": 2,
}

errors = {
    "y/n input": "Wrong answer! Please input Y for Yes or N for No",
    "max_addresses": "You reached a max amount of custom addresses.",
    "critical_addresses": "A critical error occured, no addresses to ping. Press ENTER to close the program."
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


##### CONFIGURATION #####

while True:
    use_default_address = a_question("Would you like to use default addresses? (Y/N) ", errors["y/n input"], "y/n")
    use_default_sleep = True 
    use_default_logfile = True 

    first_address = True
    if use_default_address: 
        max_list_len = 6
    else: 
        max_list_len = 10

    while True:
        if first_address and not use_default_address:
            output = "Would you like to add your own, custom address? (Y/N) "
        else:
            output = "Would you like to add another address? (Y/N) "

        while True:
            if first_address and not use_default_address:
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

    is_configuration_successful = a_question("Would you like to proceed or would you like to configure again? (Y to continue, N to config)", errors["y/n input"], "y/n")
    if is_configuration_successful:
        break
    else:
        address_list = []
        custom_address_list = []

##### PROCESSOR #####
pass


# while True:


#     def ping_address(address):
#         return os.system(f"ping -n 1 {address}")
#         #return os.system(f"ping -t {address}")





#     def data_processor(cmd):
#         t_output = cmd.split("\n")
#         print(t_output)
#         print(len(t_output))


#     def log_result(log_file, cmd):
#         pass


#     log_file = open_log_file(default_path)
#     cmd1 = ping_address(address1)
#     print(cmd1)
    #cmd1 = data_processor(cmd1)
    # while True:
    #     if address1 == "": # If no address is specified
    #         input("Ping address not specified. Check your configuration")
    #         sys.exit()
    #     cmd1 = ping_address(address1)
    #     cmd1 = data_processor(cmd1)
    #     if address2 != "":
    #         cmd2 = ping_address(address2)
    #     if address3 != "":
    #         cmd3 = ping_address(address3)

        

    #     time.sleep(sleep)
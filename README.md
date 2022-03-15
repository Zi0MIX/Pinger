# Pinger
An app to monitor network stability

# Features
- Ping up to 10 addresses at once.*
- Define how often the program will ping your addresses.
- Define the threshold above which the program will log the event
- Check past readings in the log file.
- The program is immune to firewalls in the users network. (to certain extent)
- Program will make occasional prints if there aren't any logged events (helps with stability control)
- Program will print a custom warning if at least half of the addresses timed out (only if 3 or more addresses are being pinged.)
- Use config file to preset your settings.

*due to the way program is sending pings, it'll send a ping after it receives an answer from the previous one. Simultaneous pings aren't being considered for now (but are the option further down the line)

# Planned features
- Linux support

# To-Do
- Adjust stability message to be clearer and also contain time between prints
- Optional prints of average delay
- Add print all option
- Config available before first launch
- Colored prints
# Config options
- Time between safety prints
- Print all
- Print average delay
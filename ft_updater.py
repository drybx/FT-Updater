#!/usr/bin/env python
# coding: utf-8

try:
    import json, requests, os, sys, time, re, subprocess, docker
    from pathlib import Path
    from urllib.request import urlopen
    from datetime import datetime as dt

    print('\n\n####################################\n' + str(dt.now()) + '\n')
except ModuleNotFoundError as e:
    print(str(e) + '. Please install required dependencies.')
except ImportError as e:
    print(e)
else:
    print('All required dependencies successfully loaded.')

# Put in your telegram data here
telegram_api_key = ''
telegram_chat_id = ''

# Add the paths to your files
path_local_blacklist_base = 'user_data/'
path_private_blacklist_base = 'user_data/'
path_strategy = 'user_data/strategies/'

# Don't change anything here
path_strategy1 = path_strategy + 'NostalgiaForInfinityX.py'
path_strategy2 = path_strategy + 'NostalgiaForInfinityX2.py'
path_strategy3 = path_strategy + 'NostalgiaForInfinityX3.py'
path_strategy4 = path_strategy + 'NostalgiaForInfinityX4.py'
path_strategy1 = Path(path_strategy1)
path_strategy2 = Path(path_strategy2)
path_strategy3 = Path(path_strategy3)
path_strategy4 = Path(path_strategy4)
remote_strat_version3 = 0
local_strat_version3 = 1

restart_required = False
ft_update = False

update_ft = True
update_x = False
update_x2 = False
update_x3 = False
update_x4 = True

messagetext = 'Performed updates:\n'

####################################
# NFIX UPDATER
####################################

def update_strategy_file(update_enabled, remote_url, local_path, strategy_name):
    global messagetext
    global restart_required
    if not update_enabled:
        print(f'Updates for {strategy_name} are disabled\n')
        return

    try:
        remote_strat = urlopen(remote_url).read().decode('utf-8')
        remote_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
        print(f'Remote {strategy_name} version {remote_strat_version} successfully downloaded from Github')
    except Exception as e:
        print(f'Could not download remote {strategy_name} file from Github: {e}')
        return

    try:
        with open(local_path, 'r') as local_strat:
            local_strat = local_strat.read()
            local_strat_version = re.search('return "v(.+?)"', local_strat).group(1)
            print(f'Local {strategy_name} version {local_strat_version} file successfully loaded')
    except FileNotFoundError:
        print(f'Could not load local {strategy_name} file. Please check path.')
        return
    except Exception as e:
        print(e)
        return

    if remote_strat_version == local_strat_version:
        print(f'\U00002705 Strategy {strategy_name} file up to date.\n')
    else:
        print(f'New version of strategy {strategy_name} available.\n')
        restart_required = True
        try:
            with open(local_path, 'w') as f:
                f.write(remote_strat)
                new_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
                print(new_strat_version)
        except AttributeError:
            print(f'Could not find version number of {strategy_name}\n')
            new_strat_version = f'Unknown version of {strategy_name}'
        
        messagetext = messagetext + '\U00002705 {} to v{} from v{}'.format(strategy_name, new_strat_version, local_strat_version) + '\n'

# NFIX UPDATER
update_strategy_file(update_x, 'https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX.py', path_strategy1, 'NFIX')

# NFIX2 UPDATER
update_strategy_file(update_x2, 'https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX2.py', path_strategy2, 'NFIX2')

# NFIX3 UPDATER
update_strategy_file(update_x3, 'https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX3.py', path_strategy3, 'NFIX3')

# NFIX4 UPDATER
update_strategy_file(update_x4, 'https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX4.py', path_strategy4, 'NFIX4')

####################################
# BLACKLIST UPDATER
####################################

# Function to update a blacklist for a given exchange
def update_blacklist(exchange):
    path_local_blacklist = path_local_blacklist_base + 'blacklist-' + exchange.lower() + '.json'
    path_private_blacklist = path_private_blacklist_base + 'blacklist-private.json'
    path_local_blacklist = Path(path_local_blacklist)
    path_private_blacklist = Path(path_private_blacklist)
    global messagetext
    global restart_required

    # Step 1: Download the latest blacklist from GitHub
    try:
        url_latest_bl = 'https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/configs/blacklist-' + exchange.lower() + '.json'
        response = requests.get(url_latest_bl)
        # Remove comments from the JSON data
        json_text = response.text
        json_text = "\n".join(line for line in json_text.split("\n") if not line.strip().startswith("//"))
        # Parse the modified JSON data
        latest_bl = json.loads(json_text)
        print(f'Remote blacklist {exchange} successfully downloaded from Github')
        #print("latest_bl" + str(latest_bl) + "\n")
    except Exception as e:
        print(f'Could not download remote blacklist {exchange} from Github: {e}')
        exit(1)

    # Step 2: Load the blacklist in use
    try:
        with open(path_local_blacklist, 'r') as file:
            now_bl = json.load(file)
    except FileNotFoundError:
        now_bl = {}
        print(f"Could not load local blacklist {exchange}")
    #print("now_bl" + str(now_bl) + "\n")

    # Step 3: Load local private blacklist
    try:
        with open(path_private_blacklist, "r") as file:
            json_text = file.read()
        # Remove comments from private blacklist
        json_text = "\n".join(line for line in json_text.split("\n") if not line.strip().startswith("//"))
        # Parse the modified JSON data
        private = json.loads(json_text)
        print(f"Private blacklist {exchange} successfully loaded.")
    except FileNotFoundError:
        print(f"Could not load private blacklist {exchange}.\nCreating empty private blacklist.")
        private = {"exchange": {"pair_blacklist": ["(|)/.*"]}}
        with open(path_private_blacklist, 'w') as file:
            json.dump(private, file, indent=4)
        print(f"Newly created private blacklist {exchange} successfully loaded.")

    # Step 4: Combine now_bl and private into one
    #latestprivate = {**latest_bl, **private}
    #latestprivate = {**latest_bl.copy(), **private}
    latestprivate = {
    'exchange': {
        'pair_blacklist': latest_bl['exchange']['pair_blacklist'] + private['exchange']['pair_blacklist']
    }
}
    #print("latestprivate" + str(latestprivate) + "\n") 

    # Step 6: Compare latestprivate and now_bl
    if latestprivate != now_bl: 
        # Step 7: Save latestprivate as a new JSON file
        with open(path_local_blacklist, 'w') as file:
            json.dump(latestprivate, file, indent=4)
        restart_required = True
        messagetext = messagetext + '\U0001F539 Blacklist {}'.format(exchange) + '\n'
        print(f'\U000027A1 {exchange} blacklist: Update available\n')
    else:
        print(f'\U00002705 Blacklist {exchange} up to date\n')

# List of exchanges
exchanges = ['Binance', 'Kucoin', 'GateIo']

# Update blacklists for all exchanges
for exchange in exchanges:
    print(f'BLACKLIST UPDATER {exchange}')
    update_blacklist(exchange)

####################################
# FREQTRADE UPDATER
####################################

def execute_command(command):
    output = subprocess.check_output(command, shell=True, text=True)
    return output

if update_ft:
    # Make sure it only runs this once per day
    datetoday = str(dt.now())[8:10]

    try:
        with open('date.txt', 'r') as datefromfile:
            datefromfile = datefromfile.read()
    except FileNotFoundError:
        print("Could not load date.txt\nCreating it...")
        with open('date.txt', 'w') as f:
            f.write(str(int(datetoday) - 1))
        with open('date.txt', 'r') as datefromfile:
            datefromfile = datefromfile.read()
    except Exception as e:
        print(e)
    else:
        print('date.txt successfully loaded')

    if datetoday != datefromfile:
        command = 'docker-compose exec -T ft_k python3 user_data/scripts/rest_client.py -c user_data/scripts/config-rest.json version'
        try:
            output = execute_command(command)
        except Exception as e:
            print(e)
            output = 'no version found'

        if "WARNING" not in output:
            # Step 2: Extract version information
            matches = re.search(r'"version": "(.*?)"', output)
            old_ft_version = matches.group(1) if matches else ""
            print(f"Old version: {old_ft_version}")

            # Step 3: Stop containers
            subprocess.run('docker-compose stop', shell=True)
            time.sleep(60)

            # Step 4: Pull latest version
            subprocess.run('docker-compose pull', shell=True)

            # Step 5: Start containers
            containers = ['ft_b', 'ft_k', 'ft_g', 'exchange-proxy'] #'ft_ai', 
            for container in containers:
                subprocess.run(f'docker-compose up -d {container}', shell=True)
            time.sleep(180)

            # Step 6: Execute command and capture output again
            output = execute_command(command)

            # Step 7: Extract new version information
            matches = re.search(r'"version": "(.*?)"', output)
            new_ft_version = matches.group(1) if matches else ""
            print(f"New version: {new_ft_version}")

            # Step 8: Compare old and new versions
            if new_ft_version != old_ft_version:
                print(f"New version detected: {new_ft_version}")
                messagetext = messagetext + f'\U0001F539 Freqtrade {new_ft_version}' + '\n'
                restart_required = True
            else:
                print("\U00002705 No new version for freqtrade")

            with open('date.txt', 'w') as f:
                f.write(datetoday)
    else:
        print("Already checked for updates for Freqtrade today. Skipping this step until tomorrow.")
else:
    print('Updates for freqtrade are disabled')

####################################
# NOTIFICATION VIA TELEGRAM
####################################

if restart_required:
    print('Scheduling restart...')
    minute = int(str(dt.now())[15:16])

    if minute in [0, 5]:
        print('wait 150 seconds')
        time.sleep(150)
    elif minute in [1, 6]:
        print('wait 90 seconds')
        time.sleep(90)
    elif minute in [2, 7]:
        print('wait 30 seconds')
        time.sleep(30)
    elif minute in [3, 8]:
        print('no waiting time')
        time.sleep(0)
    elif minute in [4, 9]:
        print('wait 210 seconds')
        time.sleep(210)
    else:
        print('something is wrong')

    print('restarting docker container')

    if ft_update:
        os.system('docker-compose down')
        time.sleep(15)
        os.system('docker-compose up -d')
    else:
        os.system('docker-compose restart')

    # Send Telegram Notification
    print(messagetext)
    url = f"https://api.telegram.org/bot{telegram_api_key}/sendMessage?chat_id={telegram_chat_id}&text={messagetext}&parse_mode=HTML"
    print(requests.get(url).json())

else:
    print('No restart required')
    restart_required = False

#!/usr/bin/env python
# coding: utf-8

try:
    import json
    import requests
    import os    
    import sys
    from pathlib import Path
    from urllib.request import urlopen
    from datetime import datetime as dt
    import time
    import re
    import subprocess
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

# Choose your exchange and name of your freqtrade container
exchange = 'Binance' # Binance, Bybit, FTX, Gateio, Huobi, KuCoin, OKX

# Add the paths to your files
path_local_blacklist_base = 'user_data/'
path_private_blacklist_base = 'user_data/'
path_strategy = 'user_data/strategies/'

# Don't change anything here
path_strategy1 = path_strategy + 'NostalgiaForInfinityX.py'
path_strategy2 = path_strategy + 'NostalgiaForInfinityX2.py'
path_strategy1 = Path(path_strategy1)
path_strategy2 = Path(path_strategy2)

restart_required = False
ft_update = False

update_ft = True
update_x = False
update_x2 = True

messagetext = 'Performed updates:\n'

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    print("JSON invalid!")
    return False
  return True

def remove_comments(fileName):
    with open(fileName,'r') as read_file:
        lines = read_file.readlines()

    with open(fileName,'w') as write_file:
        for line in lines:
            if '//' in line:
                write_file.write("\n")
            else:
                write_file.write(line)

####################################
# NFIX UPDATER
####################################

if update_x:
    # Downloading remote strategy file from Github
    try:
        remote_strat = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX.py').read()
    except Exception:
        print('Could not download remote strategy file from Github')
    else:
        remote_strat = remote_strat.decode('utf-8')
        remote_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
        print('Remote strategy version {} successfully downloaded from Github'.format(remote_strat_version))

    # Load local strategy file
    try:
        with open (path_strategy1, 'r') as local_strat:
            local_strat=local_strat.read()
    except FileNotFoundError:
        print("Could not load local strategy file. Please check path.")
    except Exception as e:
        print(e)
    else:
        try:
            local_strat_version = re.search('return "v(.+?)"', local_strat).group(1)
            print('Local strategy version {} file successfully loaded'.format(local_strat_version))
        except Exception as e:
            print(e)
            local_strat_version = 0

    if remote_strat_version == local_strat_version :
        print('Strategy file up to date.\n')
    else:
        print('New version of strategy NFIX available.\n')
        restart_required = True
        f = open(path_strategy1, 'w')
        f.write(remote_strat)
        f.close()
        try:
            new_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
            print(new_strat_version)
        except AttributeError:
            print('Couldnt find version number of NFI\n')
            new_strat_version = 'Unknown version'
        messagetext = messagetext + '\U00002705 NFIX to  v{} from v{}'.format(new_strat_version, local_strat_version) + '\n'
else:
    print('Updates for NFI X are disabled')

####################################
# NFIX2 UPDATER
####################################

if update_x2:
    # Downloading remote strategy 2 file from Github
    try:
        remote_strat2 = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX2.py').read()
    except Exception:
        print('Could not download remote strategy 2 file from Github')
    else:
        remote_strat2 = remote_strat2.decode('utf-8')
        remote_strat_version2 = re.search('return "v(.+?)"', remote_strat2).group(1)
        print('Remote strategy X2 version {} successfully downloaded from Github'.format(remote_strat_version2))

    # Load local strategy 2 file
    try:
        with open (path_strategy2, 'r') as local_strat2:
            local_strat2=local_strat2.read()
    except FileNotFoundError:
        print("Could not load local strategy 2 file. Please check path.")
    except Exception as e:
        print(e)
    else:
        try:
            local_strat_version2 = re.search('return "v(.+?)"', local_strat2).group(1)
            print('Local strategy X2 version {} file successfully loaded'.format(local_strat_version2))
        except Exception as e:
            print(e)
            local_strat_version2 = 0

    if remote_strat_version2 == local_strat_version2:
        print('Strategy X2 file up to date.\n')
    else:
        print('New version of strategy X2 available.\n')
        restart_required = True
        f = open(path_strategy2, 'w')
        f.write(remote_strat2)
        f.close()
        try:
            new_strat_version2 = re.search('return "v(.+?)"', remote_strat2).group(1)
            print(new_strat_version2)
        except AttributeError:
            print('Couldnt find version number of NFI X2\n')
            new_strat_version2 = 'Unknown version of X2'
        messagetext = messagetext + '\U00002705 NFIX2 to v{} from v{}'.format(new_strat_version2, local_strat_version2) + '\n'
else:
    print('Updates for NFI X2 are disabled')

####################################
# BLACKLIST UPDATER 1
####################################

path_local_blacklist = str(path_local_blacklist_base) + 'blacklist-' + exchange.lower() + '.json'
path_private_blacklist = str(path_private_blacklist_base) + 'blacklist-p-' + exchange.lower() + '.txt'
path_local_blacklist = Path(path_local_blacklist)
path_private_blacklist = Path(path_private_blacklist)

# Load blacklist 1 in use
try:
    with open (path_local_blacklist, 'r') as now_bl:
        now_bl=now_bl.read()
except FileNotFoundError:
    now_bl = ""
    print(f"Could not load local blacklist {exchange}")
except Exception as e:
    print(e)
else:
    print(f'Local blacklist {exchange} successfully loaded')

# Load private blacklist 1 in use
try:
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except FileNotFoundError:
    print("Could not load private blacklist.\nCreating empty private blacklist.")
    f = open(path_private_blacklist, 'w')
    f.write('// Private Blacklist\n"(|)/.*"')
    f.close()
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except Exception as e:
    print(e)
else:
    print('Private blacklist successfully loaded')

# Download latest blacklist 1 from GitHub...
try:
    latest_bl = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/configs/blacklist-' + exchange.lower() + '.json').read()
except Exception:
    print(f'Could not download remote blacklist {exchange} from Github')
else:
    print('Remote blacklist successfully downloaded from Github')
latest_bl = latest_bl.decode('utf-8')

# Combine latest and private list 1
latestprivate = latest_bl[:-19] + ', \n' + private[:] + '\n' + latest_bl[-11:]

# write temporary file 1
g = open('tmp1.txt', 'w')
g.write(latestprivate)
g.close()

# remove comments of newly created blacklist
remove_comments("tmp1.txt")

# read in newly created blacklist without comments
with open ('tmp1.txt', 'r') as bl_to_test:
        bl_to_test=bl_to_test.read()

# Compare newly created blacklist with existing one
if bl_to_test == now_bl:
    print(f'Blacklist {exchange} up to date\n')
elif is_json(bl_to_test):
    print('Update available, JSON valid\n')
    f = open(path_local_blacklist, 'w')
    f.write(bl_to_test)
    f.close()
    restart_required = True
    messagetext = messagetext + '\U0001F539 Blacklist {}'.format(exchange) + '\n'
else:
    print('Something went wrong with the blacklists')

# delete temporary file
try:
    os.remove("tmp1.txt")
except Exception as e:
    print(e)

####################################
# BLACKLIST UPDATER 2
####################################

# Choose your second exchange and name of your freqtrade container
exchange = 'Kucoin' # Binance, Bybit, FTX, Gateio, Huobi, KuCoin, OKX

# Don't change anything here
path_local_blacklist = path_local_blacklist_base + 'blacklist-' + exchange.lower() + '.json'
path_private_blacklist = path_private_blacklist_base + 'blacklist-p-' + exchange.lower() + '.txt'
path_local_blacklist = Path(path_local_blacklist)
path_private_blacklist = Path(path_private_blacklist)

# Load blacklist 2 in use
try:
    with open (path_local_blacklist, 'r') as now_bl:
        now_bl=now_bl.read()
except FileNotFoundError:
    now_bl = ""
    print(f"Could not load local blacklist {exchange}")
except Exception as e:
    print(e)
else:
    print(f'Local blacklist {exchange} successfully loaded')

# Load private blacklist 2 in use
try:
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except FileNotFoundError:
    print(f"Could not load private blacklist {exchange}.\nCreating empty private blacklist.")
    f = open(path_private_blacklist, 'w')
    f.write('// Private Blacklist\n"(|)/.*"')
    f.close()
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except Exception as e:
    print(e)
else:
    print(f'Private blacklist {exchange} successfully loaded')

# Download latest blacklist 2 from GitHub...
try:
    latest_bl = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/configs/blacklist-' + exchange.lower() + '.json').read()
except Exception:
    print(f'Could not download remote blacklist {exchange} from Github')
else:
    print(f'Remote blacklist {exchange} successfully downloaded from Github')
latest_bl = latest_bl.decode('utf-8') 

# Combine latest and private list 2
latestprivate = latest_bl[:-19] + ', \n' + private[:] + '\n' + latest_bl[-11:]

# write temporary file 2
g = open('tmp2.txt', 'w')
g.write(latestprivate)
g.close()

# remove comments of newly created blacklist
remove_comments("tmp2.txt")

# read in newly created blacklist without comments
with open ('tmp2.txt', 'r') as bl_to_test:
        bl_to_test=bl_to_test.read()

# Compare newly created blacklist with existing one
if bl_to_test == now_bl:
    print(f'Blacklist {exchange} up to date\n')
elif is_json(bl_to_test):
    print('Update available, JSON valid\n')
    f = open(path_local_blacklist, 'w')
    f.write(bl_to_test)
    f.close()
    restart_required = True
    messagetext = messagetext + '\U0001F539 Blacklist {}'.format(exchange) + '\n'
else:
    print('Something went wrong with the blacklists')

# delete temporary file
try:
    os.remove("tmp2.txt")
except Exception as e:
    print(e)

####################################
# BLACKLIST UPDATER 3
####################################

# Choose your second exchange and name of your freqtrade container
exchange = 'GateIo' # Binance, Bybit, FTX, Gateio, Huobi, KuCoin, OKX

# Don't change anything here
path_local_blacklist = path_local_blacklist_base + 'blacklist-' + exchange.lower() + '.json'
path_private_blacklist = path_private_blacklist_base + 'blacklist-p-' + exchange.lower() + '.txt'
path_local_blacklist = Path(path_local_blacklist)
path_private_blacklist = Path(path_private_blacklist)

# Load blacklist 3 in use
try:
    with open (path_local_blacklist, 'r') as now_bl:
        now_bl=now_bl.read()
except FileNotFoundError:
    now_bl = ""
    print(f"Could not load local blacklist {exchange}")
except Exception as e:
    print(e)
else:
    print(f'Local blacklist {exchange} successfully loaded')

# Load private blacklist 3 in use
try:
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except FileNotFoundError:
    print(f"Could not load private blacklist {exchange}.\nCreating empty private blacklist.")
    f = open(path_private_blacklist, 'w')
    f.write('// Private Blacklist\n"(|)/.*"')
    f.close()
    with open (path_private_blacklist, 'r') as private:
        private=private.read()
except Exception as e:
    print(e)
else:
    print(f'Private blacklist {exchange} successfully loaded')

# Download latest blacklist 3 from GitHub...
try:
    latest_bl = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/configs/blacklist-' + exchange.lower() + '.json').read()
except Exception:
    print(f'Could not download remote blacklist {exchange} from Github')
else:
    print(f'Remote blacklist {exchange} successfully downloaded from Github')
latest_bl = latest_bl.decode('utf-8')

# Combine latest and private list 3
latestprivate = latest_bl[:-19] + ', \n' + private[:] + '\n' + latest_bl[-11:]

# write temporary file 3
g = open('tmp3.txt', 'w')
g.write(latestprivate)
g.close()

# remove comments of newly created blacklist
remove_comments("tmp3.txt")

# read in newly created blacklist without comments
with open ('tmp3.txt', 'r') as bl_to_test:
        bl_to_test=bl_to_test.read()

# Compare newly created blacklist with existing one
if bl_to_test == now_bl:
    print(f'Blacklist {exchange} up to date\n')
elif is_json(bl_to_test):
    print('Update available, JSON valid\n')
    f = open(path_local_blacklist, 'w')
    f.write(bl_to_test)
    f.close()
    restart_required = True
    messagetext = messagetext + '\U0001F539 Blacklist {}'.format(exchange) + '\n'
else:
    print('Something went wrong with the blacklists')

# delete temporary file
try:
    os.remove("tmp3.txt")
except Exception as e:
    print(e)

####################################
# FREQTRADE UPDATER
####################################

if update_ft:
    # Make sure it only runs this once per day
    datetoday = (str(dt.now())[8:10])
    #print(datetoday)

    try:
        with open ('date.txt', 'r') as datefromfile:
            datefromfile=str(datefromfile.read())
    except FileNotFoundError:
        print("Could not load date.txt\nCreating it...")
        f = open('date.txt', 'w')
        f.write(str(int(datetoday)-1))
        f.close()
        with open ('date.txt', 'r') as datefromfile:
            datefromfile=str(datefromfile.read())
    except Exception as e:
        print(e)
    else:
        print('date.txt successfully loaded')
    # print('Today: '+ datetoday)
    # print('From file: '+ str(datefromfile))

    if datefromfile != datetoday:
        output = subprocess.run("docker-compose pull", shell=True, capture_output=True, text=True)
        print(output)
        f = open('date.txt', 'w')
        f.write(datetoday)
        f.close()
        if "Pulling ... done" in str(output):
            print('No newer version of freqtrade available.')
        else:
            restart_required = True
            ft_update = True
            messagetext = messagetext + '\U0001F538 Freqtrade' + '\n'
            print('Update for Freqtrade available.')
    else:
        print('Already checked for updates for Freqtrade today. Skipping this step until tomorrow.')
else:
    print('Updates for freqtrade are disabled')

####################################
# NOTIFICATION VIA TELEGRAM
####################################

if restart_required:
    print('Scheduling restart...')
    # middle candle protection
    minute = int(str(dt.now())[15:16])
    # print(minute)
    if (minute == 0 or minute == 5):
            print('wait 150 seconds')
            time.sleep(150)
    elif (minute == 1 or minute == 6):
            print('wait 90 seconds')
            time.sleep(90)
    elif (minute == 2 or minute == 7):
            print('wait 30 seconds')
            time.sleep(30)
    elif (minute == 3 or minute == 8):
            print('no waiting time')
            time.sleep(0)
    elif (minute == 4 or minute == 9):
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
    
    #### Send Telegram Notification
    print(messagetext)
    url = f"https://api.telegram.org/bot{telegram_api_key}/sendMessage?chat_id={telegram_chat_id}&text={messagetext}&parse_mode=HTML"
    print(requests.get(url).json())

else:
    print('No restart required')
    restart_required = False

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
except ModuleNotFoundError as e:
    print(str(e) + '. Please install required dependencies.')
except ImportError as e:
    print(e)
else:
    print('All required dependencies successfully loaded.')

# Choose your exchange and name of your freqtrade container
exchange = 'Binance' # Binance, Bybit, FTX, Gateio, Huobi, KuCoin, OKX
ft_name = 'freqtrade' # Name of your freqtrade container in Docker

# Add the paths to your files
path_local_blacklist = '/path/to/folder/user_data/'
path_private_blacklist = '/path/to/folder/user_data/'
path_strategy = '/path/to/folder/strategies/'

# Put in your telegram data here
telegram_api_key = '1111111111:ABCabc11ababcClKr1D1abcdef1AB-ABCDE'
telegram_chat_id = '11111111'

# Don't change anything here
path_local_blacklist = path_local_blacklist + 'blacklist-' + exchange.lower() + '.json'
path_private_blacklist = path_private_blacklist + 'blacklist-p-' + exchange.lower() + '.txt'
path_strategy = path_strategy + 'NostalgiaForInfinityX.py'
path_local_blacklist = Path(path_local_blacklist)
path_private_blacklist = Path(path_private_blacklist)
path_strategy = Path(path_strategy)

nfiupdate = False
blupdate = False
ftupdate = False
restart_required = False

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
# BLACKLIST UPDATER
####################################

# Load blacklist in use
try:
    with open (path_local_blacklist, 'r') as now_bl:
        now_bl=now_bl.read()
except FileNotFoundError:
    print("Could not load local blacklist")
except Exception as e:
    print(e)
else:
    print('Local blacklist successfully loaded')

# Load private blacklist in use
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

# Download latest blacklist from GitHub...
try:
    latest_bl = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/configs/blacklist-' + exchange.lower() + '.json').read()
except Exception:
    print('Could not download remote blacklist from Github\n')
else:
    print('Remote blacklist successfully downloaded from Github\n')
latest_bl = latest_bl.decode('utf-8')

# Combine latest and private list
latestprivate = latest_bl[:-19] + ', \n' + private[:] + '\n' + latest_bl[-11:]

# write temporary file
g = open('tmp.txt', 'w')
g.write(latestprivate)
g.close()

# remove comments of newly created blacklist
remove_comments("tmp.txt")

# read in newly created blacklist without comments
with open ('tmp.txt', 'r') as bl_to_test:
        bl_to_test=bl_to_test.read()

# Compare newly created blacklist with existing one
if bl_to_test == now_bl:
    print('Blacklist up to date')
elif is_json(bl_to_test):
    print('Update available, JSON valid')
    restart_required = True
    f = open(path_local_blacklist, 'w')
    f.write(bl_to_test)
    f.close()
    restart_required = True
    blupdate = True
else:
    print('Something went wrong with the blacklists')

# delete temporary file
try:
    os.remove("tmp.txt")
except Exception as e:
    print(e)

####################################
# NFIX UPDATER
####################################

# Downloading remote strategy file from Github
try:
    remote_strat = urlopen('https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX2.py').read()
except Exception:
    print('Could not download remote strategy file from Github')
else:
    remote_strat = remote_strat.decode('utf-8')
    remote_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
    print('Remote strategy version {} successfully downloaded from Github'.format(remote_strat_version))

# Load local strategy file
try:
    with open (path_strategy, 'r') as local_strat:
        local_strat=local_strat.read()
except FileNotFoundError:
    print("Could not load local strategy file. Please check path.")
except Exception as e:
    print(e)
else:
    local_strat_version = re.search('return "v(.+?)"', local_strat).group(1)
    print('Local strategy version {} file successfully loaded'.format(local_strat_version))

if remote_strat_version == local_strat_version:
    print('Strategy file up to date.')
else:
    print('New version of strategy available.')
    restart_required = True
    nfiupdate = True
    f = open(path_strategy, 'w')
    f.write(remote_strat)
    f.close()
    try:
        new_strat_version = re.search('return "v(.+?)"', remote_strat).group(1)
        print(new_strat_version)
    except AttributeError:
        print('Couldnt find version number of NFI')
        new_strat_version = 'Unknown version'

####################################
# FREQTRADE UPDATER
####################################

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
    p = subprocess.Popen("docker-compose pull {}".format(ft_name), stdout=subprocess.PIPE, shell=True)
    output = p.communicate()
    f = open('date.txt', 'w')
    f.write(datetoday)
    f.close()
    if "Pulling {} ... done".format(ft_name) in output:
        print('No newer version of freqtrade available.')
    else:
        restart_required = True
        ftupdate = True
        print('Update for Freqtrade available.')
else:
    print('Already checked for updates for Freqtrade today. Skipping this step until tomorrow.')

####################################
# NOTIFICATION VIA TELEGRAM
####################################

messagetext = 'Updates for *FT {}*:\n'.format(exchange)
if nfiupdate:
    messagetext = messagetext + '\U0001F539 NFIX2 update' + '\n'
    nfiupdate = False
if blupdate:
    messagetext = messagetext + '\U0001F539 Blacklist update' + '\n'
    blupdate = False
if ftupdate:
    messagetext = messagetext + '\U0001F539 Freqtrade update' + '\n'
    ftupdate = False
print(messagetext)

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
    os.system('docker-compose restart')
    
    #### Send Telegram Notification
    url = f"https://api.telegram.org/bot{telegram_api_key}/sendMessage?chat_id={telegram_chat_id}&text={messagetext}&parse_mode=MarkdownV2"
    print(requests.get(url).json())

else:
    print('No restart required')
    restart_required = False

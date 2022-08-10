import httpx
import json
import time
import random
import base64, requests
import os
import string
import kopechka as emailhandler
import websocket
from concurrent.futures import ThreadPoolExecutor
from threading import RLock, Thread
import requests
import emailverif
from vutils import generateDOB, buy_email, random_char, username, getRandomPicture, getverifytoken_k, check_emails_kopeechka, w2s

import logging
import uuid

from utils.logging import init_logging

init_logging(level=logging.INFO)
log = logging.getLogger("gen.main")

genned = 0

class ExitCode(Exception):
    pass


def gatheremails():
    emails = []
    with open('emails.txt', 'r', encoding='UTF-8') as file:
        lines = file.readlines()

        for line in lines:
            emails.append(line.replace('\n', ''))
        return emails


proxies = [line.rstrip("\n") for line in open("proxies.txt")]
    

def get_formatted_proxy(proxy):
    if '@' in proxy:
        return proxy
    elif len(proxy.split(':')) == 2:
        return proxy
    else:
        if '.' in proxy.split(':')[0]:
            return ':'.join(proxy.split(':')[2:]) + '@' + ':'.join(proxy.split(':')[:2])
        else:
            return ':'.join(proxy.split(':')[:2]) + '@' + ':'.join(proxy.split(':')[2:])

def get_proxy2():
    if len(proxies) == 0:
        return None
    randproxy = random.choice(proxies)
    proxy = get_formatted_proxy(randproxy)

    proxysplitted = str(proxy).split("@")
    userpas = proxysplitted[0].split(":")

    user = userpas[0]
    pas = userpas[1]

    ipport = proxysplitted[1]

    serverdict = {
        'server': f"http://{ipport}",
        'username': f"{user}",
        'password': f"{pas}",
    }

    registerproxies = {
        "all://": f"http://{proxy}"
    }

    return serverdict, registerproxies

i = 1
def get_proxy():
    if len(proxies) == 0:
        return None
    # proxy = random.choice(proxies)
    # proxy = get_formatted_proxy(randproxy)

    global i
    try:
        i += 1
        proxyl = proxies[i]
        proxy = get_formatted_proxy(proxyl)
        proxysplitted = str(proxy).split("@")
        userpas = proxysplitted[0].split(":")
        user = userpas[0]
        pas = userpas[1]
        ipport = proxysplitted[1]

    except:
        i = 0
        proxyl = proxies[i]
        proxy = get_formatted_proxy(proxyl)
        proxysplitted = str(proxy).split("@")
        userpas = proxysplitted[0].split(":")
        user = userpas[0]
        pas = userpas[1]
        ipport = proxysplitted[1]

    serverdict = {
        'server': f"http://{ipport}",
        'username': f"{user}",
        'password': f"{pas}",
    }

    registerproxies = {
        "all://": f"http://{proxy}"
    }

    return serverdict, registerproxies



def generateDOB():
    year = str(random.randint(1997,2001))
    month = str(random.randint(1, 12))
    day = str(random.randint(1,28))
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    return year + '-' + month + '-' + day

def getRandomPicture():
    files = os.listdir('accountsconfig/pfps')
    with open('accountsconfig/pfps' + "/" + files[random.randrange(0, len(files))], "rb") as pic:
        return "data:image/png;base64,"+base64.b64encode(pic.read()).decode('utf-8')

def username():
    usernames = open("accountsconfig/usernames.txt", encoding="cp437", errors='ignore').read().splitlines()
    return random.choice(usernames)

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))
'''
action: getNumber
api_key: 
service: ds
country: 23
forward: 0
owner: site
operator: any
&ref=1715152
'''
def getphoneNumber():
    phoneAPI = ""
    country = "48"
    response = requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=getNumber&service=ds&country=' + country).text
    if ":" not in response:
        if response != "":
            log.warning("Failed receiving phone number ->", response)
            time.sleep(3)
            return getphoneNumber()
    try:
        id = response.split(':')[1]
        number = response.split(':')[2]
        log.debug(f"Phone ID :: {id}")
        log.debug(f"Phone Number :: {number}")
        return id, number
    except:
        log.warning(f"Response not caught -> {response}")
        return False

def requestSms(client, token, phone_number, captcha_key=None):
    log.debug(f"Requesting SMS :: {phone_number}")
    payl = {
            'change_phone_reason': "user_settings_update",
            'phone': '+' + str(phone_number)
    }
    if captcha_key is not None:
        payl['captcha_key'] = captcha_key

    response = client.post('https://discord.com/api/v9/users/@me/phone', json=payl, headers={
            'referer': 'https://discord.com/channels/@me',
            'authorization': token
    }, timeout=8)
    log.debug(f"Response text :: {response.text}")
    if response.status_code == 400:
        if 'Invalid phone number' in response.text:
            getphoneNumber()
        log.warning((f"Adding phone number without captcha failed, requesting captcha solve :: {token} :: {phone_number} :: {captcha_key}"))
    if response.status_code == 204:
            return 0
    log.warning("Unknown ->", response.status_code, response.text)
    return 
def get_sms(id, phoneAPI):
    def get_code():
        response = requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=getStatus&id=' + id).text
        if 'STATUS_OK' not in response:
            return False
        return response.split(':')[1]

    def sent() -> None:
        requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=setStatus&status=1&id=' + id)

    def done() -> None:
        requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=setStatus&status=6&id=' + id)

    def banned() -> None:
        requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=setStatus&status=8&id=' + id)

    sent()
    tries = 0
    while tries < 30:
        time.sleep(3)
        res = get_code()
        if res is not False:
            done()
            return res
        tries += 1
    banned()
    return False
def register(isImap = False):
    
    registration_uuid = str(uuid.uuid4())
    
    try:
        
        
       
        serverdict, registerproxy = get_proxy()

        client = httpx.Client(http2=True, proxies=registerproxy)

        cookieheaders = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            #'sec-gpc': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
        }

        r = client.get("https://discord.com/register", headers=cookieheaders, timeout=10)
        t = r.headers['Set-Cookie']
        dcfduid = r.headers['Set-Cookie'].split('__dcfduid=')[1].split(';')[0]
        sdcfduid = r.headers['Set-Cookie'].split('__sdcfduid=')[1].split(';')[0]

        fingerprintheaders = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'Authorization': 'undefined',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'referer': 'https://discord.com/register',
            #'sec-gpc': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
            'X-Context-Properties': 'eyJsb2NhdGlvbiI6IlJlZ2lzdGVyIn0=',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2Ojk3LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvOTcuMCIsImJyb3dzZXJfdmVyc2lvbiI6Ijk3LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTIyMDg3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',

        }

        fingerprintreq = client.get("https://discord.com/api/v9/experiments", headers=fingerprintheaders, timeout=10)
        fingerprint = fingerprintreq.json()['fingerprint']

        # email = random_char(20) + "@outlook.com"

        registerheaders = {
            'accept': '*/*',
            'authorization': 'undefined',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            #'sec-gpc': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Fingerprint': fingerprint,
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2Ojk3LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvOTcuMCIsImJyb3dzZXJfdmVyc2lvbiI6Ijk3LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTIyMDg3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
            'referer': 'https://discord.com/register',
            'origin': 'https://discord.com',
            'Cookie': f'__dcfduid={dcfduid}; __sdcfduid={sdcfduid};'
        }
        log.debug(f'Solving Captcha :: {registration_uuid}')
        # key = captcha.solve(serverdict)
        url = "http://127.0.0.1:8000/captcha/"
#        url2 = "http://capservertwo.eu.ngrok.io//captcha/"
        try:
            key = requests.post(url, json = serverdict)
            log.debug("Post sent to local server")
        except Exception as e:
            log.warning("Local Post Failed")
            log.exception(e)

            '''
        if "P0" not in key:
            register()
            '''
        log.debug(key.text)
        log.debug(f'Captcha solved :: {registration_uuid} :: {key}')
        #log.debug(f'Captcha solved :::: {key}')

        
        if isImap == False:
            order, emailj = buy_email()
            log.debug("Ordering emails")
            #log.debug(f'Email Order :: {order} :: {registration_uuid}')
         #  log.debug(f'Email Order :: {order} :: {registration_uuid}')

       # elif isImap == True:
         #   email = request.get()
        #    splituser = email.split(":")
          #  emailj = splituser[0]
            
        DOB = generateDOB()

            
        
        

        pas = random_char(20)

        r2 = {
            "fingerprint": fingerprint,
            "email": emailj,
            "gift_code_sku_id": None,
            "invite": None,
            "username": "xX{}Xx".format(username()),
            "password": pas,
            "consent": True,
            "date_of_birth": DOB,
            "captcha_key": key.text,
        }


        response = client.post('https://discord.com/api/v9/auth/register', headers=registerheaders, json=r2, timeout=20)
        log.debug(f"Client Response :: {response.text}")

        try:
            token = response.json()['token']
        except:
            return
        log.debug(f"Token :: {token} :: {registration_uuid}")
        w2s(token)


def getRandomPicture():
    files = os.listdir('accountsconfig/pfps')
    with open('accountsconfig/pfps' + "/" + files[random.randrange(0, len(files))], "rb") as pic:
        return "data:image/png;base64,"+base64.b64encode(pic.read()).decode('utf-8')

        f = {
            "avatar": getRandomPicture()
        }

        avatarheader = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': token,
            'Content-Type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-gpc': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Super-Properties':  'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2Ojk3LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvOTcuMCIsImJyb3dzZXJfdmVyc2lvbiI6Ijk3LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTIyMDg3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
            'Cookie': f'__dcfduid={dcfduid}; __sdcfduid={sdcfduid};'
        }

        r = client.patch("https://discord.com/api/v9/users/@me", headers=avatarheader, json=f)

        '''
        if isImap == False:
            verifytoken = emailhandler.getverifytoken(order)
        else:
            log.debug("verifying email --->", emailr[0])
            verifytoken = emailverif.verifier(emailrs[0])
        '''

        

        
        if isImap == False:
            verifytoken = emailhandler.getverifytoken(order)
        elif isImap == True:
            print("verifying email --->", splituser[0])
            verifytoken = emailverif.verifier(splituser)        
        
        verifyheaders = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-gpc': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk4LjAuNDc1OC44NyBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiOTguMC40NzU4Ljg3Iiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjExNDc2NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
            'Cookie': f'__dcfduid={dcfduid}; __sdcfduid={sdcfduid};'
        }

        verifypayload = {
            'token': verifytoken
        }

        client.post("https://discord.com/api/v9/auth/verify", headers=verifyheaders, json=verifypayload)

        response = client.get('https://discord.com/api/v9/users/@me/library', headers={
            'referer': 'https://discord.com/app',
            'authorization': token
        }, timeout=20)
        log.debug(f"Client Response :: {response.text} :: {response.status_code} :: {registration_uuid}")

        if response.status_code == 403:
            log.info(f"[-] Account locked :: {registration_uuid} :: {token}")
            
        else:
            log.info(f"[+] Account unlocked --->  {token} :: {registration_uuid}")
            save(emailj,pas,token)
        '''
        id, number = getphoneNumber()
        log.debug(number)
        rs = requestSms(client, token, number, captcha_key=None)
        log.debug(rs)
        sms = get_sms(id, phoneAPI)
        log.debug("sms code is: ", sms)
        '''

    except Exception as e:
        raise e

def w2s(token):
    
    log.debug(f"Token Connecting to websocket :: {token}")
    v = {
        "op": 2,
        "d": {
            "token": token,
            "capabilities": 253,
            "properties": {
                "os": "Windows",
                "browser": "Chrome",
                "device": "",
                "system_locale": "en-US",
                "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
                "browser_version": "98.0.4758.87",
                "os_version": "10",
                "referrer": "",
                "referring_domain": "",
                "referrer_current": "",
                "referring_domain_current": "",
                "release_channel": "stable",
                "client_build_number": 114764,
                "client_event_source": ""
            },
            "presence": {
                "status": "online",
                "since": 0,
                "activities": [],
                "afk": False
            },
            "compress": False,
            "client_state": {
                "guild_hashes": {},
                "highest_last_message_id": "0",
                "read_state_version": 0,
                "user_guild_settings_version": -1,
                "user_settings_version": -1
            }
        }
    }
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')
    response = ws.recv()
    event = json.loads(response)
    f = json.dumps(v)
    ws.send(f)
    ws.close()
    
def save(email,pas,token):
    f = open('tokens.txt', "a+")
    f.write(email + ":" + pas + ":" + token)
    f.write("\n")
    f.close()

def main2(isImap):

    while True:
        try:
            register(isImap)
        except httpx.ProxyError:
            log.debug("Proxy Failed to dial. Retrying...")
        except ExitCode as e:
            log.error(e)
            exit(0)
        except Exception as e:
            log.debug(e)
        
        genned # this isnt the file where the oslver implementation is for the ohte guys thing

def main():
    threadAmount = input("Enter threads: ")
    isImap = input("Type 1 for imap or 2 for kopeechka: ")
    threadAmount = 1 if threadAmount == "" else int(threadAmount)
    isImap = True if isImap == "1" else False
    threads = []
    with ThreadPoolExecutor(max_workers=threadAmount) as ex:
        for x in range(threadAmount):
            t = ex.submit(main2, isImap)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.fatal("Sigterm End")
        exit()

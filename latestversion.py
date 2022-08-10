from vutils import generateDOB, buy_email, random_char, username, getRandomPicture, getverifytoken_k, check_emails_kopeechka, w2s
import httpx, json, time, asyncio, base64, random, os, string, websocket, requests
import kopechka as emailhandler
from concurrent.futures import ThreadPoolExecutor
from threading import RLock, Thread
from colorama import init, Fore, Style
import emailverif
import string

isImap = False
init(convert=True)
proxies = [line.rstrip("\n") for line in open("proxies.txt")]

class SynchronizedEcho(object):
    print_lock = RLock()

    def __init__(self, global_lock=True):
        if not global_lock:
            self.print_lock = RLock()

    def __call__(self, msg):
        with self.print_lock:
            print(msg)

s_print = SynchronizedEcho()

def gatheremails():

    emails = []
    with open('emails.txt', 'r', encoding='UTF-8') as file:
        lines = file.readlines()

        for line in lines:
            emails.append(line.replace('\n', ''))
        return emails


s_print = SynchronizedEcho()
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
        


def getphoneNumber():
    phoneAPI = "4"
    country = "0"
    response = requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=&action=getNumber&service=ds&country=1' + country).text
    if ":" not in response:
        if response != "":
            print("Failed receiving phone number ->", response)
            time.sleep(3)
            return getphoneNumber()
    try:
        id = response.split(':')[1]
        number = response.split(':')[2]
        print(id)
        print(number)
        return id, number
    except:
        print(response)
        return False

def sent():
    phoneAPI = "4"

    requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=4&action=setStatus&status=1&id=' + id)


def requestSms(client, token, phone_number, captcha_key=None):
    print("inside request sms ", phone_number)
    sent()
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
    print(response.text)
    if response.status_code == 400:
        if 'Invalid phone number' in response.text:
            getphoneNumber()
        print(("Adding phone number without captcha failed, requesting captcha solve"))
    if response.status_code == 204:
            return 0
    print("Unknown ->", response.status_code, response.text)
    sent()
    return 
def get_sms(id, phoneAPI):
    def get_code():
        response = requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + phoneAPI + '&action=getStatus&id=' + id).text
        if 'STATUS_OK' not in response:
            return False
        return response.split(':')[1]

    def done() -> None:
        requests.get('https://api.sms-activate.org/stubs/handler_api.php?api_key=' + '&action=setStatus&status=6&id=' + id)

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


def save(email,pas,token):
    f = open('tokens.txt', "a+")
    f.write(email+":"+pas+":"+token)
    f.write("\n")
    f.close()
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




def register(isImap = False):
    try:
       
        serverdict, registerproxy = get_proxy()
        phoneAPI = ""

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
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk4LjAuNDc1OC44NyBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiOTguMC40NzU4Ljg3Iiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjExNDc2NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',

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
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk4LjAuNDc1OC44NyBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiOTguMC40NzU4Ljg3Iiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjExNDc2NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
            'referer': 'https://discord.com/register',
            'origin': 'https://discord.com',
            'Cookie': f'__dcfduid={dcfduid}; __sdcfduid={sdcfduid};'
        }
        print('solving captcha')
        #key = captcha.solve(serverdict)
        url = "http://127.0.0.1:5000/captcha/"
        url2 = "http://capservertwo.eu.ngrok.io//captcha/"
        
        try:
            key = requests.post(url2, json = serverdict)
        except Exception as e:
            key = requests.post(url2, json = serverdict) 
        

        if 'P0' not in key.text or key.text == None:
            register()
            print("No key")
            print('++++' + key)
        elif 'P0' in key.text:
          #  print('key')
            print('solved')
            

        
            
            if isImap == False:
                order, emailj = buy_email()
                print("Ordering emailO")
            else:
                emailrs =[]
                email = get_email()
                emailrs.append(email)
                emailr = []
                splituser = email.split(":")
                emailj = splituser[0]
                emailr.append(emailj)
            pas = random_char(20)
            
            r2 = {
                "fingerprint": fingerprint,
                "email": emailj,
                "gift_code_sku_id": None,
                "invite": None,
                "username": username(),
                "password": pas,
                "consent": True,
                "date_of_birth": "1992-03-04",
                "captcha_key": key.text,
            }


            response = client.post('https://discord.com/api/v9/auth/register', headers=registerheaders, json=r2, timeout=20)
            print(response.text)
            print("______")
            print("------")

            token = response.json()['token']
            w2s(token)

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
                'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk4LjAuNDc1OC44NyBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiOTguMC40NzU4Ljg3Iiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjExNDc2NCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
                'Cookie': f'__dcfduid={dcfduid}; __sdcfduid={sdcfduid};'
            }

            r = client.patch("https://discord.com/api/v9/users/@me", headers=avatarheader, json=f)

            
            if isImap == False:
                verifytoken = emailhandler.getverifytoken(order)
            else:
                print("verifying email --->", emailr[0])
                verifytoken = emailverif.verifier(emailrs[0])
            

            
        # print("verifying email --->", emailr[0])
        #  verifytoken = emailverif.verifier(emailrs[0])
            
            
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
            print(response.text)

            if response.status_code == 403:
                s_print(f"{Fore.RED}{Style.BRIGHT}[-] Account locked {Style.RESET_ALL}")
                
            else:
                s_print(f"{Fore.GREEN}{Style.BRIGHT}[+] Account unlocked --->  {token} {Style.RESET_ALL}")
                save(emailj, pas, token)

  
  
    except Exception as e:
        print(e)
        return register()
 
'''            
            id, number = getphoneNumber()
            print(number)
            rs = requestSms(client, token, number, captcha_key=None)
            print(rs)
            sms = get_sms(id, phoneAPI)
            print("sms code is: ", sms)
            '''

        

def save(email,pas,token):
    f = open('tokens.txt', "a+")
    f.write(email+":"+pas+":"+token)
    f.write("\n")
    f.close()



def main2(isImap):

    while True:
        register(isImap)

def main():
    threadAmount = input("enter threads: ")
    isImap = input("type 1 for imap or 2 for kopeechka: ")
    threadAmount = 1 if threadAmount == "" else int(threadAmount)
    isImap = True if isImap == "1" else False
    threads = []
    with ThreadPoolExecutor(max_workers=threadAmount) as ex:
        for x in range(threadAmount):
            time.sleep(1)
            t = ex.submit(main2, isImap)




if __name__ == '__main__':
    main()


import httpx, json, time, asyncio, base64, random, os, string, websocket, requests, sys
from urlextract import URLExtract

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

def buy_email():
    tries = 1
    email_type1 = ['outlook', 'hotmail']# starts at 09:14:03
    #email_type1 = ['outlook', 'hotmail']
   # email_type1 = ['mail.ru']
    email_type = random.choice(email_type1)
  #  email_type = 'mail.ru'
   # email_type = 'mail.ru' # testing now
    EMAIL_BUY = f'https://api.kopeechka.store/mailbox-get-email?api=2.0&spa=1&site=discord.com&sender=discord&regex=&mail_type={email_type}&token='
    response = requests.get(EMAIL_BUY).json()
    if not 'id' in response:
#        print('Email Error: ' + str(response))
        if response['value'] == 'OUT_OF_STOCK' and tries < 30:
            tries = tries + 1

            buy_email()
  #  if tries > 29:
   #     print('Exiting.. Email Error: ' + str(response))
    #    sys.exit()
    elif 'id' in response:
        order = response['id']
        emailj = response['mail']
       # print(response)
      #  print(emailj)
        #print(order)
        return order, emailj

def getverifytoken_k(order):
    timelimit = 100
    verify_token = None
    timeout = 0
    while timelimit > timeout:
        time.sleep(5)
        timeout += 5
        verify_token = check_emails_kopeechka(order)
        if verify_token is not None:
            print('email recieved')
            return verify_token


    else:

        return False
        
def check_emails_kopeechka(order):
    EMAIL_CHECK = f'http://api.kopeechka.store/mailbox-get-message?full=1&id={order}&token=&type=JSON&api=2.0'
    response = requests.get(EMAIL_CHECK).json()
    '''
    print(response)
    '''
    if response['value'] != 'WAIT_LINK':
        body = response['fullmessage']
        extractor = URLExtract()
        urls = extractor.find_urls(body)
        if len(urls) > 4:
            headers = {
                'Referer': urls[5]
            }
            verify_token = requests.get(urls[5], allow_redirects=False, headers=headers).headers['Location'].split('#token=')[1]
            return verify_token
    return None




def w2s(token):
    
    
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

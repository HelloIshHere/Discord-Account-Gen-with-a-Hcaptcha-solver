import requests
import sys
from urlextract import URLExtract
import time
import logging

email_token = ''
email_domain = 'hotmail.com,outlook.com,rambler.ru'
email_site = 'discord.com'
email_timeout = 120
email_method = 'kopeechka'

log = logging.getLogger("gen.kp")

def check_emails_kopeechka(order):
    EMAIL_CHECK = f'http://api.kopeechka.store/mailbox-get-message?full=1&id={order}&token={email_token}&type=JSON&api=2.0'
    response = requests.get(EMAIL_CHECK).json()
    log.debug(f" KPResponse :: {response}")
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

def buy_email():
    EMAIL_BUY = f'http://api.kopeechka.store/mailbox-get-email?site={email_site}&mail_type={email_domain}&token={email_token}&type=JSON&api=2.0'
    response = requests.get(EMAIL_BUY).json()

    tries = 0
    
    
    if not 'id' in response:
        log.warning('Email Error: ' + str(response))
        if response['value'] == 'OUT_OF_STOCK' and tries < 30:
            log.warning("Emails out of stock..sleeping for 2 secs and retrying again..")
            time.sleep(2)
            tries = tries + 1
            buy_email()
            
    if tries > 29:
        log.critical('Exiting.. Email Error: ' + str(response))
        sys.exit()
    if 'id' in response:
        order = response['id']
        email = response['mail']
        return order, email

def getverifytoken(order):
    timelimit = False
    verify_token = None
    timeout = 0
    while timelimit is False:
        time.sleep(5)
        timeout += 5
        verify_token = check_emails_kopeechka(order)
        if verify_token is not None:
            log.debug('Email Recieved' + str(verify_token))
            return verify_token


        if timeout >= email_timeout:
            log.warning(f"Order :: {order} :: Timeout reached")

            if email_method == "kopeechka":
                log.debug(f"Order :: {order} Timout reached, cancelling order")
                requests.get(
                    f'http://api.kopeechka.store/mailbox-cancel?id={order}&token={email_token}&type=JSON&api=2.0')

            return False


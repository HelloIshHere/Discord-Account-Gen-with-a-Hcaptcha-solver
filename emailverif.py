import httpx
from imap_tools import MailBox, AND
import requests
import time
from urlextract import URLExtract
import logging

log = logging.getLogger("gen.emailverif")

email_timeout = 120

def gatheremails():

    emails = []
    with open('emails.txt', 'r', encoding='UTF-8') as file:
        lines = file.readlines()

        for line in lines:
            emails.append(line.replace('\n', ''))
        return emails

def getmail(splituser):
    # domain2 = email.split("@")
    # domain3 = domain2[1]
    # domain3 = domain3.split(":")
    # domain = domain3[0]

    log.debug(f"Email :: {splituser}")

    log.debug(f"Email :: {username}, {domain}, {password}")

    with MailBox('outlook.office365.com').login(splituser[0], splituser[1]) as mailbox:
        for msg in mailbox.fetch(AND(all=True)):
            if msg.subject == 'Verify Email Address for Discord':
                log.debug(f"Email Fetched :: {msg.subject}")
                return msg.html



def verifier(splituser):
 
    timelimit = False
    timeout = 0
    # log.debug("Adding email to discord") 
    # addemail(email, token)
    log.debug(f"Verifying email :: {email}")
    # emailverify(token, email)
    log.debug("EMAIL VERIFYING..")

    found = False
    while timelimit is False:
        time.sleep(5)
        timeout += 5
        mail = getmail(splituser)
        if mail is not None:
            log.debug(f"Email :: {splituser[1]} :: recieved verifier link")
            extractor = URLExtract()
            urls = extractor.find_urls(mail)
            log.debug(f"Url :: {urls[5]}")
            geturltoken = requests.get(urls[5], allow_redirects=False)
            s = geturltoken.headers['Location']
            splitted = s.split("#token=")
            verifytoken = splitted[1]
            log.debug(f"Verify Token :: {verifytoken}")
            found = True
            return verifytoken
        if timeout >= email_timeout:
            log.debug(f"Email :: {email} :: Timeout")
            return False





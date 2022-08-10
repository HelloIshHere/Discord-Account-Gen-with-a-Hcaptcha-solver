from turtle import radians
from playwright.sync_api import sync_playwright,TimeoutError as playwrightTimeoutError
from playwright_stealth import stealth_sync
import time
import requests
import random
import re
import os
import logging

log = logging.getLogger("gen.captcha")

class SolverException(Exception):
    pass

class SolverAPI:
    
    def __init__(self):
    
       # urls = ["https://recognition.discordservice.info", "https://recognition.discordservice.info"]
        urls = ["old server redacted"]


        self.main_reco_url = random.choice(urls)#os.environ["MAIN_RECO_URL"]
        self.fallback_reco_url = random.choice(urls)# os.environ["FALLBACK_RECO_URL"]
        self.current_reco_url = self.main_reco_url

    def solveCaptcha(self, proxy):
        log.debug("Solving captcha with proxy: " + str(proxy))
        with sync_playwright() as p:
            # Loop discord.com to the local server serving the HCaptcha Harvester
            a = [
                "--disable-gpu",
                '--ignore-certificate-errors',
                '--host-rules=MAP discord.com 127.0.0.1:22003',
                '--proxy-bypass-list="<-loopback>"',
              #  '--ingcognito',
            ]
            browser = p.chromium.launch(
                #executable_path='/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser', args=a,
                executable_path='C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe', args=a,

                headless=False, proxy=proxy)
            # Create a new context with the user agent
            context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36')
            # context.add_cookies()
            page = context.new_page()
            #page = browser.new_page()
            page.set_viewport_size({"width": 500, "height": 600}) # Set the size of the browser
            stealth_sync(page) # This somehow makes it less detectable by hcaptcha
            page.goto('https://discord.com') # Go to discord.com in the browser ( Actually looped to the local html file )

            # getting checkbox iframe
            try:
                checkboxframe = page.wait_for_selector("body > section > form > div > iframe", timeout=20000).content_frame()
            except playwrightTimeoutError:
                log.warning("Timeout error on checkbox frame")
                browser.close()
                raise SolverException()
            
            # Get the checkbot button
            try:
                checkboxbutton = checkboxframe.wait_for_selector('#checkbox', timeout=10000) # Get the checkbox button
            except playwrightTimeoutError:
                log.warning("Timeout error on checkbox button")
                browser.close()
                raise SolverException()
            
            # Click the checkbox button
            try:
                checkboxbutton.hover()
                checkboxbutton.click(button='left', delay=2, click_count=1, timeout=10000)
            except playwrightTimeoutError:
                log.warning("Ratelimit or an issue occurred on the checkbox button")
                browser.close()
                raise SolverException()

            imageurls = []

            # This is catching the urls from hcaptcha and storing them in imageurls
            def on_response(response):

                if '/getcaptcha' in response.url:
                    challengedata = response.json()
                    imageurls.clear()
                    for image in challengedata['tasklist']:
                        imageurls.append(image['datapoint_uri'])

            time.sleep(200)
            page.on('response', on_response)

            # getting challenge iframe
            try:
                challengeiframe = page.wait_for_selector("body > div > div:nth-child(1) > iframe", timeout=20000).content_frame()
            except playwrightTimeoutError:
                log.warning("Timeout error on challenge frame")
                browser.close()
                raise SolverException()
            
            try:
                challengetext = challengeiframe.wait_for_selector('body > div.challenge-container > div > div > div.challenge-header > div.challenge-prompt > div.prompt-padding > div.prompt-text')
            except playwrightTimeoutError:
                log.warning("Error getting selector for challengetext")
                browser.close() 
                raise SolverException()
            
            challengetextsplitted = challengetext.inner_text().split() # No idea what this is spilitting by but somehow getting the word
            word = challengetextsplitted[6]

            json = {'word': word, 'urls': imageurls}
            
            try:
                solve = requests.post(f'{self.current_reco_url}/resolve/', json=json)
            except Exception:
                log.warning("Main reco server is down, switching to fallback url.")
                self.main_reco_url = self.fallback_reco_url
                solve = requests.post(f'{self.fallback_reco_url}/resolve/', json=json)
                
            answers = solve.json()['answers']
            tilestoclick = []
            
            # Example {'answers': [True, False, False, False, False, True, True, False, False]}

            for correct in answers:
                
                if correct:
                    correctindexs = imageurls.index(correct)
                    correctindexs += 1
                    tilestoclick.append(correctindexs)
                else: continue

            for x in tilestoclick:
                time.sleep(1)
                tile = challengeiframe.wait_for_selector(
                    f'body > div.challenge-container > div > div > div.task-grid > div:nth-child({x})')
                tile.hover(timeout=1000)
                tile.click(button='left', delay=2, click_count=1)

            submit = challengeiframe.wait_for_selector('body > div.challenge-interface > div.button-submit.button')
            submit.hover(timeout=1000)
            submit.click(button='left', delay=2, click_count=2)

            time.sleep(2)
            tries = 0
            while tries < 10:
                time.sleep(1)
                tries += 1
                handle = page.evaluate('hcaptcha.getResponse()')
                if handle == "":
                    continue
                else:
                    return handle
            return handle
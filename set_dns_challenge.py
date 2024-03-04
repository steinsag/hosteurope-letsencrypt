#!/usr/bin/env python3
# coding=utf-8
import argparse
import asyncio
import json
import time

from pyppeteer import launch

from shared import config_file

# parse cmdline
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--domain', dest='domain', required=True)
parser.add_argument('-c', '--challenge', dest='challenge', required=True)
args = parser.parse_args()

# zu validierende Domain, Dateinamen and Token Inhalt werden von certbot per Umgebungsvariable übergeben
domain = args.domain
content = args.challenge

print('Domain:    ' + domain)
print('Challenge: ' + content)

# Mapping zwischen Domains und Verzeichnis auf FTP laden
with open(config_file('domains.json')) as domain_file:
    domains_file = json.load(domain_file)

path = domains_file.get(domain)
if not path:
    print('Kein Mapping für Domain gefunden. Breche ab! ->' + domain)
    exit(1)

cfg_file = open(config_file('einstellungen.json'))
config = json.load(cfg_file)


async def set_challenge_for(browser, url, token, domain_name):
    page = await browser.newPage()
    # Open SSL page
    print("-> Lade DNS Seite")
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.setViewport({'width': 1366, 'height': 1000})
    time.sleep(1)

    # Fill in form and submit
    print("-> Suche nach Zieleintrag und füge Challenge-String ein")
    parent_element = await page.Jx(f'//td[text()[contains(., "_acme-challenge.{domain_name}")]]/..')
    time.sleep(2)
    if len(parent_element) <= 0:
        print(f"-> !!! DNS TXT record _acme-challenge.{domain_name} nicht gefunden. Bitte auf KIS-DNS-Seite manuell hinzufügen!")
        input('ENTER zum Beenden.')
        exit(1)
    text_field = await parent_element[0].querySelector('input[name="pointer"]')
    await text_field.focus()
    await text_field.click({'clickCount': 3})
    await page.keyboard.type(token)
    await page.keyboard.press("Enter")
    time.sleep(1)
    await page.waitForNavigation({'waitUntil': 'networkidle2'})

    # Log result
    print("-> Update Challenge fertig")
    await page.screenshot({'path': domain_name + '-dns-validate.log.jpeg'})


async def set_challenge():
    # Login
    print("Starte Browser...")
    browser = await launch({'headless': False, 'slowMo': 1, 'devtools': False, 'executablePath': '/usr/bin/chromium-browser'})
    time.sleep(2)
    page = await browser.newPage()
    print("Starte Login...")
    await page.goto('https://kis.hosteurope.de', {'waitUntil': 'networkidle2'})
    time.sleep(1)
    await page.focus("input[autocomplete=email]")
    await page.keyboard.type(config["kis-username"])
    await page.focus("input[type=password]")
    await page.keyboard.type(config["kis-password"])
    await page.keyboard.press("Enter")
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    time.sleep(1)

    # 2FA
    if (config["kis-2fa"]):
        print("Starte 2FA")
        await page.focus("input[id=1]")
        await page.keyboard.type(input("Enter the 2FA you got via SMS here: "))
        await page.keyboard.press("Enter")
        await page.waitForNavigation({'waitUntil': 'networkidle2'})
        time.sleep(1)

    # process domains
    for (domain_cfg,
         url) in domains_file.items():  # url as "https://kis.hosteurope.de/administration/domainservices/index.php?menu=<idx>&mode=autodns&submode=edit&domain=<domain.de>"
        if (domain_cfg in domain):
            if domain_cfg.startswith("*."):
                domain_name = domain_cfg[2:]
            else:
                domain_name = domain_cfg

            print(f"Setze Challenge für: {domain_name}")
            await set_challenge_for(browser, url, content, domain_name)
            print(f"... ca. 15 Sekunden warten, bis die Änderungen verfügbar sind.")

    print("Fertig.")
    await browser.close()


try:
    asyncio.get_event_loop().run_until_complete(set_challenge())
except Exception as err:
    print(f"FEHLER: Unerwarteter {err=}, {type(err)=}")
    exit(1)

exit(0)

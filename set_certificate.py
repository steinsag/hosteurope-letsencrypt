#!/usr/bin/env python3
# coding=utf-8
import json
import os
import asyncio
from pyppeteer import launch
from shared import domain_list, config_file
import time
import sys


cfg_file = open(config_file('einstellungen.json'))
config = json.load(cfg_file)

cert_conf_file = open(config_file('cert-urls.json'))
cert_config = json.load(cert_conf_file)

async def set_certificate_for(browser, url, cert_file, key_file, domain_name):
    page = await browser.newPage()
    # Open SSL page
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.setViewport({'width': 1366, 'height': 1000})
    time.sleep(1)

    # Fill in form
    certfileUpload = await page.querySelector("input[name=certfile]")
    keyfileUpload = await page.querySelector("input[name=keyfile]")
    
    await certfileUpload.uploadFile(cert_file)
    await keyfileUpload.uploadFile(key_file)

    # Submit form
    await page.focus("input[name=keypass]")
    await page.keyboard.press("Enter")
    time.sleep(1)
    await page.waitForNavigation({'waitUntil': 'networkidle2'})

    # Log result
    await page.screenshot({'path': domain_name+'.log.jpeg'})
    


async def set_certificate():
    # Login
    browser = await launch({'headless': False, 'slowMo': 1, 'devtools': True})
    page = await browser.newPage()
    await page.goto('https://kis.hosteurope.de', {'waitUntil': 'networkidle2'})
    await page.focus("input[autocomplete=email]")
    await page.keyboard.type(config["kis-username"])
    await page.focus("input[type=password]")
    await page.keyboard.type(config["kis-password"])
    await page.keyboard.press("Enter")
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    time.sleep(1)

    #2FA
    if (config["kis-2fa"]):
        await page.focus("input[id=1]")
        await page.keyboard.type(input("Enter the 2FA you got via SMS here: "))
        await page.keyboard.press("Enter")
        await page.waitForNavigation({'waitUntil': 'networkidle2'})
        time.sleep(1)

    for (domain, url) in cert_config.items():
        cert_file = config_file(os.path.join('live', domain, 'fullchain.pem'))
        key_file = config_file(os.path.join('live', domain, 'privkey.pem'))
        await set_certificate_for(browser, url, cert_file, key_file, domain)

    time.sleep(10)
    await browser.close()

asyncio.get_event_loop().run_until_complete(set_certificate())
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

async def set_certificate_for(browser, url, certificate_folder, domain_name):
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.setViewport({'width': 1366, 'height': 1000})
    time.sleep(1)

    certfileUpload = await page.querySelector("input[name=certfile]")
    keyfileUpload = await page.querySelector("input[name=keyfile]")
    
    await certfileUpload.uploadFile(os.path.join(certificate_folder, domain_name, 'cert.pem'))
    await keyfileUpload.uploadFile(os.path.join(certificate_folder, domain_name, 'privkey.pem'))

    await page.focus("input[name=keypass]")
    await page.keyboard.press("Enter")
    time.sleep(1)
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    await page.screenshot({'path': domain_name+'.log.png'})
    time.sleep(10)
    await browser.close()

cert_conf_file = open(config_file('cert-urls.json'))
cert_config = json.load(cert_conf_file)

async def set_certificate():
    # Login
    browser = await launch({'headless': False, 'slowMo': 1, 'devtools': True})
    page = await browser.newPage()
    await page.goto('https://kis.hosteurope.de', {'waitUntil': 'networkidle2'})
    await page.keyboard.press("Tab")
    await page.keyboard.press("Tab")
    await page.keyboard.type(config["kis-username"])
    await page.keyboard.press("Tab")
    await page.keyboard.type(config["kis-password"])
    await page.keyboard.press("Enter")
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    time.sleep(1)

    certificate_folder = os.path.expanduser('~/.config/hosteurope-letsencrypt/live')
    for (domain, url) in cert_config.items():
        await set_certificate_for(browser, url, certificate_folder, domain)

asyncio.get_event_loop().run_until_complete(set_certificate())
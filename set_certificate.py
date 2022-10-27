#!/usr/bin/env python3
# coding=utf-8
import json
import os
import asyncio
from playwright.async_api import async_playwright
from shared import domain_list, config_file
import sys


cfg_file = open(config_file('einstellungen.json'))
config = json.load(cfg_file)

cert_conf_file = open(config_file('cert-urls.json'))
cert_config = json.load(cert_conf_file)

async def set_certificate_for(page, url, cert_file, key_file, domain_name):
    # page = await browser.new_page()
    # Open SSL page
    print(f"Opening SSL-Form for {domain_name}: {url}")
    await page.goto(url, wait_until = 'networkidle')
    await page.set_viewport_size({'width': 1366, 'height': 1000})
    await asyncio.sleep(1)

    # Fill in form
    # certfileUpload = await page.query_selector("input[name=certfile]")
    # keyfileUpload = await page.query_selector("input[name=keyfile]")
    
    # await certfileUpload.uploadFile(cert_file)
    # await keyfileUpload.uploadFile(key_file)
    print(f"Uploading cert files: {cert_file} and {key_file}")

    await page.set_input_files("input[name=certfile]", cert_file)
    await page.set_input_files("input[name=keyfile]", key_file)

    # Submit form
    print(f"Submit form")
    await page.focus("input[name=keypass]")
    await page.keyboard.press("Enter")
    await asyncio.sleep(1)
    await page.wait_for_load_state('networkidle')

    # Log result
    print(f"Done! Logging output")
    await asyncio.sleep(5)
    await page.pdf(path=f"{domain_name}.log.pdf", print_background=True, format='A4')
    await page.screenshot(path = f"{domain_name}.log.jpeg")
    


async def set_certificate():
    # Login
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo= 1, devtools= True)
        page = await browser.new_page()
        await page.goto('https://kis.hosteurope.de', wait_until = 'networkidle')
        await page.focus("input[autocomplete=email]")
        await page.keyboard.type(config["kis-username"])
        await page.focus("input[type=password]")
        await page.keyboard.type(config["kis-password"])
        await page.keyboard.press("Enter")
        await asyncio.sleep(1)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)

        #2FA
        if (config["kis-2fa"]):
            await page.focus("input[id=1]")
            await page.keyboard.type(input("Enter the 2FA you got via SMS here: "))
            await page.keyboard.press("Enter")
            await asyncio.sleep(10)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(10)

        for (domain, url) in cert_config.items():
            cert_file = config_file(os.path.join('live', domain, 'fullchain.pem'))
            key_file = config_file(os.path.join('live', domain, 'privkey.pem'))
            await set_certificate_for(page, url, cert_file, key_file, domain)

        await asyncio.sleep(10)
        await browser.close()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(set_certificate())
    except KeyboardInterrupt:
        pass

#!/usr/bin/env python3
# coding=utf-8

from shared import prepare_domain_list, get_config, prepare_certbot_dirs, process_cert_request

config = get_config('einstellungen.json')
challenge = config.get('preferred-challenge', 'http')

# certbot Kommando zusammenbauen
cmd = 'certbot certonly --manual --agree-tos'
cmd += ' -m ' + config['email']
cmd += ' --preferred-challenge=' + challenge
if 'http' == challenge:
    cmd += ' --manual-auth-hook "python3 validate.py"'
if config['staging']:
    cmd += ' --staging'
cmd += prepare_certbot_dirs()
cmd += prepare_domain_list()

# Sicherheitsabfrage
print(cmd)
answer = input('Für diese Domains ein neues Zertifikat erstellen? (j/n): ')
if answer != 'j':
    print('Abbruch, es wurde kein Zertifikat erstellt.')
    exit(0)

# neues Zertifikat erstellen
process_cert_request(cmd, challenge)

# coding=utf-8
import ftplib
import json
import logging
import os
import uuid

from shared import config_file

# manuelles Logging, da certbot Ausgabe dieses Skripts unterdrückt
logging.basicConfig(filename='validation.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Mapping zwischen Domains und Verzeichnis auf FTP laden
with open(config_file('domains.json')) as domain_file:
    DOMAINS = json.load(domain_file)

# zu validierende Domain, Dateinamen and Token Inhalt werden von certbot per Umgebungsvariable übergeben
domain = os.environ['CERTBOT_DOMAIN']
filename = os.environ['CERTBOT_TOKEN']
content = os.environ['CERTBOT_VALIDATION']

logging.debug('Domain: ' + domain)
logging.debug('Inhalt: ' + content)
logging.debug('Dateiname: ' + filename)

path = DOMAINS.get(domain)
if not path:
    logging.debug('Kein Mapping für Domain gefunden. Breche ab!')
    exit(1)

# FTP Zugangsdaten laden
with open(config_file('ftp.json')) as ftp_file:
    ftp_cfg = json.load(ftp_file)

# mit FTP verbinden
ftp = ftplib.FTP_TLS(ftp_cfg['server'], ftp_cfg['login'], ftp_cfg['passwort'])
root_dir = ftp.pwd()

# zum Pfad navigieren, in dem Challenge angelegt werden muss
ftp.cwd(root_dir + path)
try:
    ftp.cwd('.well-known/acme-challenge')
except:
    logging.debug('Creating missing .well-known/acme-challenge directory.')
    ftp.mkd('.well-known')
    ftp.cwd('.well-known')
    ftp.mkd('acme-challenge')
    ftp.cwd('acme-challenge')

# temporäre Datei mit Token Inhalt anlegen
temp_filename = str(uuid.uuid4())
logging.debug('Lege temporäre Datei {} mit Token Inhalt an.'.format(temp_filename))
with open(temp_filename, 'wb') as temp:
    temp.write(str.encode(content))

# temporäre Datei unter von certbot vorgegebenen Namen auf FTP hochladen
with open(temp_filename, 'rb') as temp:
    ftp.storbinary('STOR %s' % filename, temp)
ftp.close()

# temporäre Datei löschen
os.remove(temp_filename)

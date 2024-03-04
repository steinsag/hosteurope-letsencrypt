# coding=utf-8
import json
import os

# Is script started as root?
is_root = os.geteuid() == 0

def config_file(name):
    f = os.path.expanduser('~/.config/hosteurope-letsencrypt/' + name)
    return os.path.abspath(name if os.path.isfile(name) or not os.path.isfile(f) else f)

# Einstellungen einlesen
def get_config(file):
    with open(config_file(file)) as cfg_file:
        return json.load(cfg_file)

# Prepares log, work and config dirs for certbot
def prepare_certbot_dirs():
    # certbot tries to write to /var/log/letsencrypt by default; because of this, running as root is required.
    # certbot Error Message:
    # Either run as root, or set --config-dir, --work-dir, and --logs-dir to writeable paths.
    home_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt')
    certbot_config_dir = home_dir
    certbot_work_dir = home_dir
    certbot_logs_dir = os.path.expanduser('~/.config/hosteurope-letsencrypt/logs')
    if not is_root and not os.path.exists(certbot_logs_dir):
        os.makedirs(certbot_logs_dir)

    certbot_dirs = ''
    if not is_root:
        certbot_dirs += ' --logs-dir ' + certbot_logs_dir
        certbot_dirs += ' --work-dir ' + certbot_work_dir
        certbot_dirs += ' --config-dir ' + certbot_config_dir

    return certbot_dirs

# Domain Mapping einlesen
def prepare_domain_list():
    domain_map = get_config('domains.json')

    # Domains auflisten wie von certbot erwartet
    domain_list = ' -d ' + ' -d '.join(domain_map.keys())
    return domain_list

# Zertifikat erstellen
def process_cert_request(cmd, challenge_type):
    if not 'dns' == challenge_type:
        os.system(cmd)
    else:
        print('Folgenden Aufruf ausführen:')
        print('')
        print(f'    {cmd}')
        print('')
        print('Dann in einem separaten Terminal das Skript set_dns_challenge.py mit den Parametern aus dem obigen Aufruf starten!')
        print('')
        print(f'    ./set_dns_challenge.py --domain <*.domain.tld> --challenge <challenge-string>')
        print('')
        print('Ca. 15 Sekunden warten bis die DNS-Änderungen verfügbar sind und dann im ersten Terminal ENTER drücken.')




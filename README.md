# Let's Encrypt Skripte für Hosteurope WebHosting

Dies ist eine Sammlung kleiner Python 3 Skripte, um die Erstellung und Validierung von
[Let's Encrypt](https://letsencrypt.org/) SSL Zertifikaten in Verbindung mit Hosteurope 
WebHosting Paketen so weit als möglich zu automatisieren.

Die Skripte automatisieren folgende Schritte:

- Aufruf des [certbot](https://certbot.eff.org/) mit den richtigen Optionen, um ein Sammel-Zertifikat für
die gewünschten Domains zu erstellen oder zu verlängern
- Hochladen der von _certbot_ vorgegebenen Validierungstokens für die einzelnen Domains mittels FTP

Das abschließende Einbinden des Zertifikats bleibt ein manueller Schritt, da Hosteurope dafür keine API
bietet, die eine Automatisierung ermöglicht.


## Anforderungen
 
Für die Nutzung der Skripte wird benötigt:

- Python 3
- [certbot](https://certbot.eff.org/)

Die Skripte wurden unter Linux getestet und 
[das Vorgehen auf meinem Blog beschrieben](https://sebstein.hpfsc.de/2017/09/17/lets-encrypt-mit-hosteurope-webhosting-nutzen/).


## Konfiguration

Die Skripte werden mittels 3 JSON Dateien konfiguriert, die manuell zu erstellen sind.
Die Konfigurationsdateien müssen im gleichen Verzeichnis wie die Python Skripte liegen.

In der Datei __einstellungen.json__ wird die im Zertifikat zu hinterlegende Emailadresse gepflegt.
Weiterhin wird konfiguriert, ob die 
[Staging Umgebung von Let's Encrypt](https://letsencrypt.org/docs/staging-environment/)
verwendet werden soll.
Die Staging Umgebung sollte man nutzen, wenn man kein richtiges Zertifikat erstellen will, sondern
zum Beispiel noch mit den richtigen Parametern experimentiert. 

    {
      "email": "webmaster@example.com",
      "staging": false
    }

In der Datei __domains.json__ gibt man die Domains an, für die ein Zertifikat erstellt werden soll.
Neben den Domainamen muss weiterhin der Pfad auf dem FTP Server angegeben werden, damit die Skripte
die von _certbot_ vorgegebenen Validierungstoken an den richtigen Stellen platzieren können.

    {
        "domain1.example.com": "domain1",
        "domain2.example.com": "domain-2/komischer_pfad"
    }
 
Es können natürlich nicht nur Sub-Domains, sondern alle im WebHosting Paket enthaltenen Domains angegeben werden.
Da Let's Encrypt erst 
[experimentelle Unterstützung für Wildcard Zertifikate](https://letsencrypt.org/2017/07/06/wildcard-certificates-coming-jan-2018.html)
bietet, muss jede Sub-Domain einzeln aufgeführt werden!

In der Datei __ftp.json__ gibt man die FTP Zugangsdaten an. Diese werden vom __validate.py__ Skript genutzt,
um per FTP die entsprechenden Validierungstoken auf dem Webserver zu platzieren.

    {
        "server": "ftp-server.hosteurope.de",
        "login": "ftp-user",
        "passwort": "GEHEIM"
    }

Das Skript löscht die hochgeladenen Tokens nicht. Die Tokens liegen im jeweiligen Domainpfad auf dem
Webserver im Unterverzeichnis _.well-known/acme-challenge_.

## Nutzung

Ein neues Zertifikat wird erstellt mittels:

    sudo python3 neu.py

Ein bestehendes Zertifikat wird verlängert mittels:

    sudo python3 verlaengern.py
    
Die Skripte müssen mit Root-Rechten laufen, da _certbot_ die generierten Zertifikate unter _/etc/letsencrypt_
ablegt.

Die folgenden Abschnitte erklären im Detail, was bei jedem Skript genau geschieht.   


### Zertifikat erstellen (neu.py)

Das Skript __neu.py__ ruft _certbot_ auf und fordert die Erstellung eines Zertifikats für alle
in __domains.json__ angegebenen Domains an.

Um eine Domain gegenüber Let's Encrypt zu validieren, muss eine Datei hochgeladen werden. Dazu wird beim
Aufruf von _certbot_ das __validate.py__ Skript übergeben. Dieses erhält von _certbot_ Namen und Inhalt der
hochzuladenden Datei und lädt diese via FTP auf den Hosteurope Webserver hoch.

Da _certbot_ Ausgaben des __validate.py__ Skripts unterdrückt, werden Debug Meldungen in die
Datei __validation.log__ geschrieben.

Nachdem das Zertifikat erstellt wurde, muss es manuell im KIS eingebunden werden.


### Zertifikat verlängern (verlaengern.py)

Let's Encrypt Zertifikate haben eine Gültigkeit von 90 Tagen.
Deshalb müssen die Zertifikate verlängert werden. Falls man in __einstellungen.json__ eine gültige
Emailadresse angegeben hat, wird man von Let's Encrypt einige Tage vor Ablauf daran erinnert.

Es muss kein komplett neues Zertifikat erstellt werden, sondern ein bestehendes Zertifikat
kann verlängert werden. Das __verlaengern.py__ Skript führt diese Verlängerung durch.
Dazu wird wiederum mittels __validate.py__ die Domain gegenüber Let's Encrypt validiert.

Nachdem das Zertifikat verlängert wurde, muss es manuell über das KIS eingebunden werden.

Zertifikate können nur verlängert werden, wenn die zugehörigen Dateien nicht gelöscht wurden.
_certbot_ legt alle zu einem Zertifikat zugehörigen Dateien unterhalb von 
_/etc/letsencrypt_ ab. Die Zertifikatsdateien enthalten eine Nummer in ihrem Dateinamen,
die bei jeder Verlängerung um 1 hochgezählt wird. Das neueste Zertifikat ist immer jenes, mit
der höchsten Nummer im Dateinamen.


### Zertifikat manuell im KIS einbinden

Durch _certbot_ wird ein Zertifikat erstellt, das alle angegebenen Domains abdeckt. Dieses Zertifikat muss
manuell im Hosteurope KIS als globales Zertifikat angegeben werden. Der entsprechende Menüpunkt findet sich
unter:

Webhosting -> Sicherheit & SSL -> SSL administrieren

Soll ein neues Zertifikat hochgeladen werden, muss das oberste _globale_ Zertifikat ersetzt werden. Dieses
Zertifikat gilt für alle Domains und Sub-Domains, für die kein eigenes Zertifikat gesetzt ist.

_certbot_ erzeugt 4 Dateien. Lediglich die folgenden 2 Dateien müssen im KIS im entsprechenden Formular
hochgeladen werden:

- Zertifikat: fullchain.pem
- Key: privkey.pem

Das Passwort Feld muss leer bleiben!

Nach dem Hochladen startet Hosteurope den Webserver neu und das Zertifikat ist innerhalb weniger Minuten
online.

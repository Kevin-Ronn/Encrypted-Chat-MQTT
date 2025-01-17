# Encrypted-Chat-MQTT

Av: Kevin Rönn.

Uppgift 1, Test och säkerhet.

En nyckel skapas från en lösenfras och justeras för att vara 32 tecken lång, som krävs av Fernet.

Använder paho-mqtt för att ansluta till en offentlig MQTT-broker och prenumerera på valda ämnen.

Meddelanden krypteras innan de skickas och avkrypteras när de tas emot.

Användaren kan avsluta chatten genom att skriva /exit.

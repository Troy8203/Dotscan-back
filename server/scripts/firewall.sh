#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Usar las variables
echo "API NAME: $NAME ($VERSION)"
echo "DESCRIPTION: $DESCRIPTION"
echo "HOST: $HOST"
echo "PORT: $PORT"

# BANLIST
while read ip; do
    [[ -z "$ip" ]] && continue
    sudo iptables -A INPUT -s "$ip" -j DROP
done < "$FILE"

# Rules for the API
sudo iptables -A INPUT -p tcp --dport "$PORT" \
  -m limit --limit 10/second --limit-burst 20 \
  -j ACCEPT

sudo iptables -A INPUT -p tcp --dport "$PORT" -j DROP

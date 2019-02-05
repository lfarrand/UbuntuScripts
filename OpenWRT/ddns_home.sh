#!/bin/bash

# Crontab entry: * * * * * /root/scripts/ddns_home.sh >> /tmp/ddns.log 2>&1

if [[ $(find /tmp/ddns.log -type f -size +51200c 2>/dev/null) ]]; then
    echo "/tmp/ddns.log is over 50KB, deleting..."
    rm /tmp/ddns.log
    touch /tmp/ddns.log
else
    echo "/tmp/ddns.log is less than 50KB"
fi

TOKEN="u7dFzDkMuMkyzbvLdYRAdfGJol2u8Erk"  # The API v2 OAuth token
ACCOUNT_ID="1998"        # Replace with your account ID
ZONE_ID="thefarrands.com"  # The zone ID is the name of the zone (or domain)
RECORD_ID="14265691"       # Replace with the Record ID
WANIP=$(dig +short myip.opendns.com @resolver1.opendns.com)
DNSIP=$(dig +short @ns1.dnsimple.com home.thefarrands.com)

CURRENTTIME="`date "+%Y-%m-%d %H:%M:%S"`";

echo "Checking DDNS at $CURRENTTIME"

echo WAN: $WANIP
echo IP: $DNSIP

if [ $WANIP != $DNSIP ]
then
        echo "WAN IP is different to DNS record, updating..."

        curl -H "Authorization: Bearer $TOKEN" \
                -H "Content-Type: application/json" \
                -H "Accept: application/json" \
                -X "PATCH" \
                -i "https://api.dnsimple.com/v2/$ACCOUNT_ID/zones/$ZONE_ID/records/$RECORD_ID" \
                -d "{\"content\":\"$WANIP\"}"
else
        echo "WAN IP is same as DNS record, no need to update."
fi

echo "Finished"
echo ""

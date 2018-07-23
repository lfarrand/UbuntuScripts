!/bin/bash

TOKEN="u7dFzDkMuMkyzbvLdYRAdfGJol2u8Erk"  # The API v2 OAuth token
ACCOUNT_ID="1998"        # Replace with your account ID
ZONE_ID="thefarrands.com"  # The zone ID is the name of the zone (or domain)
RECORD_ID="14265691"       # Replace with the Record ID
WANIP=$(ifconfig pppoe-wan | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)
DNSIP=$(dig +short @ns1.dnsimple.com home.thefarrands.com)

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

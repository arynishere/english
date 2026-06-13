#!/bin/bash
set -e
certbot --nginx -d english.v4vendetta.sbs --non-interactive --agree-tos --register-unsafely-without-email
echo "SSL فعال شد: https://english.v4vendetta.sbs"

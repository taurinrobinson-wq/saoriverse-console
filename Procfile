web: sh -c "cd velinor-web && npm start > /tmp/frontend.log 2>&1 & python3 velinor_api.py > /tmp/api.log 2>&1 & sleep 2 && exec nginx -g 'daemon off;'"

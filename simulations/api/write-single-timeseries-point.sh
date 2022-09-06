#!/bin/bash
# Write single timeseries point

curl --request POST \
  "http://localhost:8086/api/v2/write?org=persuader-technology&bucket=automata"  \
  --header "Authorization: Token q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --header "Accept: application/json" \
  --data-binary '
    timeseries-test,instrument=test price=10.123456789012 1662482974593347564
  '
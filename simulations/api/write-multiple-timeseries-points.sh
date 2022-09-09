#!/bin/bash
# Write multiple timeseries points

curl --request POST \
  "http://localhost:8086/api/v2/write?org=persuader-technology&bucket=automata&precision=ns"  \
  --header "Authorization: Token q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --header "Accept: application/json" \
  --data-binary '
    timeseries-test,instrument=test price=10.123456789012 1662473484448608385
    timeseries-test,instrument=test price=9012345678901.0 1662482460798568965
    timeseries-test,instrument=test price=111.0 1662482768962413104
    timeseries-test,instrument=test price=0.000000000012 1662482974593347564
    timeseries-test,instrument=test price=0.00 1662489746609256622
    timeseries-test,instrument=test price=0.000000000001 1662752474914966498
  '
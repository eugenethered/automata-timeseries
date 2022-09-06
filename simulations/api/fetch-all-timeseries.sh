#!/bin/bash
# Fetch all timeseries points

curl --request POST \
  http://localhost:8086/api/v2/query?org=persuader-technology  \
  --header "Authorization: Token q3cfJCCyfo4RNJuyg72U-3uEhrv3qkKQcDOesoyeIDg2BCUpmn-mjReqaGwO7GOebhd58wYVkopi5tcgCj8t5w==" \
  --header "Accept: application/csv" \
  --header "Content-type: application/vnd.flux" \
  --data 'from(bucket:"automata")
        |> range(start: -72h)
        |> filter(fn: (r) => r._measurement == "timeseries-test")'

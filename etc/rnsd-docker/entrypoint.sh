#!/bin/bash
[[ -z "$RNS_PORT" ]] \
  && RNS_PORT=/dev/ttyACM0
sed -i "s,CFG_PORT,$RNS_PORT,g" $CONFIG_FILE_PATH

[[ -z "$RNS_FREQUENCY" ]] \
  && RNS_FREQUENCY="867500000"
sed -i "s,CFG_FREQUENCY,$RNS_FREQUENCY,g" $CONFIG_FILE_PATH

[[ -z "$RNS_BANDWIDTH" ]] \
  && RNS_BANDWIDTH="125000"
sed -i "s,CFG_BANDWIDTH,$RNS_BANDWIDTH,g" $CONFIG_FILE_PATH

[[ -z "$RNS_TXPOWER" ]] \
  && RNS_TXPOWER="17"
sed -i "s,CFG_TXPOWER,$RNS_TXPOWER,g" $CONFIG_FILE_PATH

[[ -z "$RNS_SF" ]] \
  && RNS_SF="9"
sed -i "s,CFG_SF,$RNS_SF,g" $CONFIG_FILE_PATH

[[ -z "$RNS_CR" ]] \
  && RNS_CR="5"
sed -i "s,CFG_CR,$RNS_CR,g" $CONFIG_FILE_PATH

[[ -z "$RNS_CALLSIGN_ID" ]] \
  && RNS_CALLSIGN_ID="X0XXX"
sed -i "s,CFG_CALLSIGN_ID,$RNS_CALLSIGN_ID,g" $CONFIG_FILE_PATH

[[ -z "$RNS_CALLSIGN_INTERVAL" ]] \
  && RNS_CALLSIGN_INTERVAL="36000"
sed -i "s,CFG_CALLSIGN_INTERVAL,$RNS_CALLSIGN_INTERVAL,g" $CONFIG_FILE_PATH

[[ -z "$RNS_NAME" ]] \
  && RNS_NAME="RNodeInterface"
sed -i "s,CFG_NAME,$RNS_NAME,g" $CONFIG_FILE_PATH

exec /bin/bash --login -c "$*"

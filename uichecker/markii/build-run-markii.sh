#!/bin/bash
# This script will mount the current source directory to docker and build the
# artifact incrementally before running on the target APK

set -e
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

$DIR/check-jdk-version

APK_PATH=$(realpath $1)
OUTPUT_PATH=$(realpath $2)
if [ -z "$3" ]; then
    TEMPFILE_REMOVE="F"
else
    TEMPFILE_REMOVE=$3
fi

if [ ! -z "$API_SEMANTICS_CONFIG" ]; then
    API_SEMANTICS_CONFIG_PARAM="-clientParam apiSemanticConfig:$(realpath $API_SEMANTICS_CONFIG)"
fi

if [ ! -z "$VASCO_MODE" ]; then
    VASCO_MODE_PARAM="-clientParam vascoMode:$VASCO_MODE"
fi

cd $DIR
if [ -z "$BATCH_RUN" ]; then
    if ! command -v sbt &> /dev/null
    then
        echo "sbt could not be found. Install it here -- https://www.scala-sbt.org/1.x/docs/Setup.html"
        exit
    fi

    ./markii b
fi

./markii a -p $APK_PATH -clientParam output:$OUTPUT_PATH $API_SEMANTICS_CONFIG_PARAM $VASCO_MODE_PARAM -temp $TEMPFILE_REMOVE

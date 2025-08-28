#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"

rm -rf $DIR/others/seqLib/ $DIR/others/seqan/
pushd $DIR/V_Next
  mkdir Build
    pushd Build
      cmake ..
      make
    popd
popd

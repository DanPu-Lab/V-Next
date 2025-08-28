#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"

rm -rf $DIR/others/SeqLib/ $DIR//others/seqan/
pushd $DIR/V_Next
  mkdir build
    pushd build
      cmake ..
      make
    popd
popd

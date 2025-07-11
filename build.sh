#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"

rm -rf $DIR/third_party/SeqLib/ $DIR/third_party/seqan/
pushd $DIR/V_Next
  mkdir build
    pushd build
      cmake ..
      make
    popd
popd

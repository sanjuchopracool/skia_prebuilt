#!/bin/bash


echo "CHECKING ENVIRONMENTS"
echo  PWD= $PWD
echo  HOME= $HOME
echo  USER= $USER

pushd $HOME

# check if the depot_tools exist
DEPOT_TOOLS_DIR=$HOME/depot_tools
if [ -d "$DEPOT_TOOLS_DIR" ];
then
    echo "$DEPOT_TOOLS_DIR directory exists. skipping depot_tools installation"
else
	  echo "$DEPOT_TOOLS_DIR directory does not exist. clonging depot_tools"
    git clone 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
fi

export PATH="${DEPOT_TOOLS_DIR}:${PATH}"
echo PATH= $PATH
popd

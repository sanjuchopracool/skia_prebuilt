#!/bin/bash


echo "CHECKING ENVIRONMENTS"
echo  PWD= $PWD
echo  HOME= $HOME
echo  USER= $USER

pushd ${HOME}

#check if GOOGLE exist in home directory
GOOGLE_DIR=${HOME}/GOOGLE

if [ -d "${GOOGLE_DIR}" ];
then
    echo "${GOOGLE_DIR} directory exists"
else
    echo "${GOOGLE_DIR} directory does not exist. creating it"
    mkdir -p ${GOOGLE_DIR}
fi

cd ${GOOGLE_DIR}

# check if the depot_tools exist
DEPOT_TOOLS_DIR=${GOOGLE_DIR}/depot_tools
if [ -d "${DEPOT_TOOLS_DIR}" ];
then
    echo "${DEPOT_TOOLS_DIR} directory exists. skipping depot_tools installation"
else
    echo "${DEPOT_TOOLS_DIR} directory does not exist. cloning depot_tools"
    git clone 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
fi

export PATH="${DEPOT_TOOLS_DIR}:${PATH}"
echo PATH=${PATH}

SKIA_DIR=${GOOGLE_DIR}/skia
if [ -d "${SKIA_DIR}" ];
then
    echo "${SKIA_DIR} directory exists. skipping skia fetch"
else
    echo "${SKIA_DIR} directory does not exist. fetching skia"
    fetch skia
    cd ${SKIA_DIR}
    python3 tools/git-sync-deps
    bin/fetch-ninja
fi

cd ${SKIA_DIR}
git pull
python3 tools/git-sync-deps
tools/install_dependencies.sh
bin/gn gen out/x64_linux --args="is_official_build=true skia_use_harfbuzz=false cc=clang ccx=clang++"
bin/gn args out/x64_linux --list
ninja -C out/x64_linux
popd

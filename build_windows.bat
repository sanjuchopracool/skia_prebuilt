@echo off
set GOOGLE_DIR=%userprofile%\GOOGLE

IF EXIST %GOOGLE_DIR%\ (
   ECHO %GOOGLE_DIR% exists
) ELSE (
   ECHO %GOOGLE_DIR% does not exist. creating it
   mkdir %GOOGLE_DIR%
)

cd /d %GOOGLE_DIR%
ECHO CWD : %cd%
set DEPOT_TOOLS_DIR=%GOOGLE_DIR%\depot_tools

IF EXIST %DEPOT_TOOLS_DIR%\ (
   ECHO %DEPOT_TOOLS_DIR% exists
) ELSE (
   ECHO %DEPOT_TOOLS_DIR% does not exist. cloning depot_tools
   git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
)

set "PATH=%DEPOT_TOOLS_DIR%;%PATH%"

ECHO CWD : %cd%
set SKIA_DIR=%GOOGLE_DIR%\skia

IF EXIST %SKIA_DIR%\ (
   ECHO %SKIA_DIR% exists
) ELSE (
   ECHO %SKIA_DIR% does not exist. cloning skia
   fetch skia
)
ECHO skia fetch done
cd /d %SKIA_DIR%
ECHO syncing skia
git pull
ECHO CWD : %cd%
ECHO "syncing tools"
python3 tools\git-sync-deps
ECHO "installing dependencies"
tools\install_dependencies.sh
bin\gn gen out\x64_win --args="is_official_build=true skia_use_harfbuzz=false"
ninja -C out\x64_win

@echo off
set GOOGLE_DIR=%userprofile%\GOOGLE

IF EXIST %GOOGLE_DIR%\ (
   ECHO %GOOGLE_DIR% exists
) ELSE (
   ECHO %GOOGLE_DIR% does not exist. creating it
   mkdir %GOOGLE_DIR%
)

cd %GOOGLE_DIR%

set DEPOT_TOOLS_DIR=%GOOGLE_DIR%\depot_tools

IF EXIST %DEPOT_TOOLS_DIR%\ (
   ECHO %DEPOT_TOOLS_DIR% exists
) ELSE (
   ECHO %DEPOT_TOOLS_DIR% does not exist. cloning depot_tools
   git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
)

set "PATH=%DEPOT_TOOLS_DIR%;%PATH%"
ECHO %PATH%

DIR %DEPOT_TOOLS_DIR%
set SKIA_DIR=%GOOGLE_DIR%\skia

IF EXIST %SKIA_DIR%\ (
   ECHO %SKIA_DIR% exists
) ELSE (
   ECHO %SKIA_DIR% does not exist. cloning skia
   fetch skia'
)

cd skia
python3 tools/git-sync-deps
bin/fetch-ninja


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import pathlib
import subprocess
from urllib.request import urlretrieve
from pathlib import Path
from subprocess import check_output, STDOUT

K_IS_WINDOWS: bool = False
K_DOWNLOAD_DIR = ""
K_PROJECTS_DIRECTORY = ""
K_GOOGLE_DIRECTORY = ""
K_SKIA_PATH = ""


def run_cmd(cmd, in_shell=False):
    my_env = os.environ.copy()
    path = my_env["PATH"]
    return_code = 0
    print(f"Running command : {cmd} in: {os.getcwd()} with PATH={path}")
    try:
        p = subprocess.run(cmd, stderr=sys.stderr, stdout=sys.stdout, env=my_env, shell=in_shell)
        return_code =  p.returncode
    except subprocess.CalledProcessError as e:
        print("Oops... output:\n" + str(e.output))
        return_code = 1

    if return_code:
        print(f"failed to run command : {cmd}")
        sys.exit(return_code)

    return return_code


def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    print("Download Progress {:.2f}".format(downloaded * 100 / total_size))


def install_clang():
    if K_IS_WINDOWS:
        llvm_path = "C:/Program Files/LLVM"
        if os.path.exists(llvm_path):
            print("LLVM is already installed!")
        else:
            print("LLVM is not installed!")
            llvm_url = 'https://github.com/llvm/llvm-project/releases/download/llvmorg-16.0.0/LLVM-16.0.0-win64.exe'
            llvm_download_path: str = K_DOWNLOAD_DIR + '/LLVM-16.0.0-win64.exe'
            if os.path.exists(llvm_download_path):
                print(f"{llvm_download_path} already exist!")
            else:
                print(f"Downloading {llvm_url} at {llvm_download_path}")
                urlretrieve(llvm_url, llvm_download_path, show_progress)
            print(f"Installing {llvm_download_path}")
            cmd = llvm_download_path + ' /S /V/qn'
            check_output(cmd, shell=True, stderr=STDOUT)
            print(f"Installed {llvm_download_path}")


def setup_global_variables():
    global K_DOWNLOAD_DIR
    global K_GOOGLE_DIRECTORY
    global K_PROJECTS_DIRECTORY
    global K_SKIA_PATH
    global K_IS_WINDOWS
    if os.name == 'nt':
        K_IS_WINDOWS = True

    home_path = os.path.normpath(Path.home())
    if os.path.sep == '\\':
        home_path = pathlib.PureWindowsPath(home_path).as_posix()
    home_path = str(home_path)
    K_DOWNLOAD_DIR = home_path + "/Downloads"
    if K_IS_WINDOWS:
        K_PROJECTS_DIRECTORY = "D:/PROJECTS"
    else:
        K_PROJECTS_DIRECTORY = home_path + "/PROJECTS"

    K_GOOGLE_DIRECTORY = K_PROJECTS_DIRECTORY + "/GOOGLE"
    K_SKIA_PATH = K_GOOGLE_DIRECTORY + "/skia"


def clone_depot_tools():
    os.makedirs(K_GOOGLE_DIRECTORY, exist_ok=True)
    depot_tools_path = K_GOOGLE_DIRECTORY + "/depot_tools"
    if os.path.exists(depot_tools_path):
        print("depot tools are already cloned!")
    else:
        print(f"cloning depot_tools at {depot_tools_path}")
        os.chdir(K_GOOGLE_DIRECTORY)
        cmd = ["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"]
        run_cmd(cmd)
    #     add depot_tools to path
    os.environ["PATH"] = depot_tools_path + os.pathsep + os.environ["PATH"]


def clone_skia():
    os.chdir(K_GOOGLE_DIRECTORY)
    if os.path.exists(K_SKIA_PATH):
        print("skia is already cloned!")
    else:
        print(f"cloning skia at {K_SKIA_PATH}")
        cmd = ["git", "clone", "https://skia.googlesource.com/skia.git"]
        run_cmd(cmd)
    os.chdir(K_SKIA_PATH)
    cmd = ["git", "pull"]
    run_cmd(cmd)
    cmd = ["python3", "tools/git-sync-deps"]
    run_cmd(cmd)
    if K_IS_WINDOWS:
        cmd = ["python3", "bin/fetch-ninja"]
        run_cmd(cmd, True)
    else:
        run_cmd(["bin/fetch-ninja"])
    # check_output("bin/fetch-ninja", shell=True, stderr=STDOUT)


def compile_for_win64():
    # X64 MSVC DEBUG
    # cmd = ('bin/gn gen out/win/x64/msvc_debug --args="'
    #        ' skia_use_system_libjpeg_turbo=false skia_use_system_zlib=false skia_use_system_harfbuzz=false'
    #        ' skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_icu=false'
    #        ' skia_use_system_expat=false"')
    # if not run_cmd(cmd):
    #     run_cmd("third_party/ninja/ninja.exe -C out/win/x64/msvc_debug")
    #
    # # X64 MSVC RELEASE
    # cmd = ('bin/gn gen out/win/x64/msvc --args="is_official_build=true'
    #        ' skia_use_system_libjpeg_turbo=false skia_use_system_zlib=false skia_use_system_harfbuzz=false'
    #        ' skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_icu=false'
    #        ' skia_use_system_expat=false"')
    # if not run_cmd(cmd):
    #     run_cmd("third_party/ninja/ninja.exe -C out/win/x64/msvc")

    # X64 CLANG DEBUG
    cmd = (
        'bin/gn gen out/win/x64/clang_debug --args="clang_win = \\"C:\\\Program Files\\\LLVM\\" cc=\\"clang\\" cxx=\\"clang++\\"'
        ' skia_use_system_libjpeg_turbo=false skia_use_system_zlib=false skia_use_system_harfbuzz=false'
        ' skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_icu=false'
        ' skia_use_system_expat=false extra_cflags=[ \\"/MDd\\" ]"')
    if not run_cmd(cmd):
        run_cmd("third_party/ninja/ninja.exe -C out/win/x64/clang_debug")

    # X64 CLANG RELEASE
    cmd = (
        'bin/gn gen out/win/x64/clang_release --args="is_official_build=true clang_win = \\"C:\\\Program Files\\\LLVM\\" cc=\\"clang\\" cxx=\\"clang++\\"'
        ' skia_use_system_libjpeg_turbo=false skia_use_system_zlib=false skia_use_system_harfbuzz=false'
        ' skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_icu=false'
        ' skia_use_system_expat=false extra_cflags=[ \\"/MD\\" ]"')
    if not run_cmd(cmd):
        run_cmd("third_party/ninja/ninja.exe -C out/win/x64/clang_release")

def compile_for_linux():
    cmd = ["bin/gn", "gen", "out/linux/x64/clang_release", '--args=\'is_official_build=true','cc="clang"', 'cxx="clang++"\'']
    if not run_cmd(cmd):
        cmd = ["third_party/ninja/ninja", "-C", "out/linux/x64/clang_release"]
        run_cmd(cmd)


def compile_skia():
    os.chdir(K_SKIA_PATH)
    if K_IS_WINDOWS:
        compile_for_win64()
    else:
        compile_for_linux()


def build_skia():
    clone_depot_tools()
    clone_skia()
    compile_skia()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    setup_global_variables()
    # install_clang()
    build_skia()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

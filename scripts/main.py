# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import pathlib
import subprocess
import platform
from urllib.request import urlretrieve
from pathlib import Path
from subprocess import check_output, STDOUT
import glob, shutil

K_IS_WINDOWS: bool = False
K_DOWNLOAD_DIR = ""
K_PROJECTS_DIRECTORY = ""
K_GOOGLE_DIRECTORY = ""
K_SKIA_PATH = ""
k_SKIA_INCLUDE_PATH = ""
k_SKIA_LIBS_PATH = ""
K_ARCHIEVE_DIR = "skia"


def run_cmd(cmd, in_shell=False):
    my_env = os.environ.copy()
    path = my_env["PATH"]
    return_code = 0
    print(f"Running command : {cmd} in shell {in_shell}: {os.getcwd()} with PATH={path}")
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
    global k_SKIA_INCLUDE_PATH
    if os.name == 'nt':
        K_IS_WINDOWS = True

    home_path = os.path.normpath(Path.home())
    if os.path.sep == '\\':
        home_path = pathlib.PureWindowsPath(home_path).as_posix()
    home_path = str(home_path)
    K_DOWNLOAD_DIR = home_path + "/Downloads"
    project_dir = os.getenv("PROJECT_DIR")
    print(f"{project_dir}")
    if K_IS_WINDOWS and project_dir:
        K_PROJECTS_DIRECTORY = "D:/PROJECTS"
    else:
        K_PROJECTS_DIRECTORY = home_path + "/PROJECTS"

    K_GOOGLE_DIRECTORY = K_PROJECTS_DIRECTORY + "/GOOGLE"
    K_SKIA_PATH = K_GOOGLE_DIRECTORY + "/skia"
    k_SKIA_INCLUDE_PATH = K_SKIA_PATH + "/include"


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
    try :
        inShell =  K_IS_WINDOWS
        cmd = ["python3", "tools/git-sync-deps"]
        if run_cmd(cmd, inShell):
            run_cmd(["python3", "tools/git-sync-deps"], inShell)
        if K_IS_WINDOWS:
            cmd = ["python3", "bin/fetch-ninja"]
            if run_cmd(cmd):
                cmd = ["python3", "bin/fetch-ninja"]
        else:
            run_cmd(["bin/fetch-ninja"])
    except:
        print("FAILED TO SYNC dependencies!")
        raise
    # check_output("bin/fetch-ninja", shell=True, stderr=STDOUT)


def copy_libs_files(source_dir, destination_dir, lib_filter):
    source_dir = source_dir.strip()
    if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)

    out_dir = destination_dir + "/include"
    shutil.copytree (k_SKIA_INCLUDE_PATH, out_dir)
    print(f"copying include files from {k_SKIA_INCLUDE_PATH} to {out_dir}")
    index_of_first_slash = source_dir.find('/',1)
    out_dir = destination_dir + "/" + source_dir[index_of_first_slash+1:]
    os.makedirs(out_dir, exist_ok=True)
    # shutil.copytree (source_dir, out_dir)
    files = glob.iglob(os.path.join(source_dir, lib_filter))
    for file in files:
         if os.path.isfile(file):
             print(f"copying file from {file} to {out_dir}")
             shutil.copy2(file, out_dir)


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
        copy_libs_files("out/win/x64/clang_debug", "skia_win_x64_clang_debug" ,"*.lib")

    # X64 CLANG RELEASE
    cmd = (
        'bin/gn gen out/win/x64/clang_release --args="is_official_build=true clang_win = \\"C:\\\Program Files\\\LLVM\\" cc=\\"clang\\" cxx=\\"clang++\\"'
        ' skia_use_system_libjpeg_turbo=false skia_use_system_zlib=false skia_use_system_harfbuzz=false'
        ' skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_icu=false'
        ' skia_use_system_expat=false extra_cflags=[ \\"/MD\\" ]"')
    if not run_cmd(cmd):
        run_cmd("third_party/ninja/ninja.exe -C out/win/x64/clang_release")
        copy_libs_files("out/win/x64/clang_release", "skia_win_x64_clang_release" ,"*.lib")

def compile_for_linux():
    global k_SKIA_LIBS_PATH
    out_dir_path = "out/linux/x64/clang_release"
    cmd = ["bin/gn", 'gen', out_dir_path, '--args=is_official_build=true skia_use_system_harfbuzz=false cc="clang" cxx="clang++"']
    if not run_cmd(cmd):
        cmd = ["third_party/ninja/ninja", "-C", out_dir_path]
        run_cmd(cmd)
        k_SKIA_LIBS_PATH = K_SKIA_PATH + out_dir_path


def compile_for_mac():
    global k_SKIA_LIBS_PATH
    out_dir_path = "out/macos/x64/clang_release"
    cmd = ["bin/gn", 'gen', out_dir_path, '--args=is_official_build=true skia_use_system_harfbuzz=false skia_use_system_libjpeg_turbo = false skia_use_system_libwebp = false skia_use_system_libpng = false skia_use_system_icu = false cc="clang" cxx="clang++"']
    if not run_cmd(cmd):
        cmd = ["third_party/ninja/ninja", "-C", out_dir_path]
        run_cmd(cmd)
        k_SKIA_LIBS_PATH = K_SKIA_PATH + out_dir_path


def compile_skia():
    os.chdir(K_SKIA_PATH)
    if K_IS_WINDOWS:
        compile_for_win64()
    elif platform.system() == "Linux":
        compile_for_linux()
    elif platform.system() == "Darwin":
        compile_for_mac()


def build_skia():
    clone_depot_tools()
    clone_skia()
    compile_skia()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    setup_global_variables()
    if K_IS_WINDOWS:
        install_clang()
    build_skia()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

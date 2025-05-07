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
import zipfile
import argparse


K_IS_WINDOWS: bool = False
K_DOWNLOAD_DIR = ""
K_PROJECTS_DIRECTORY = ""
K_GOOGLE_DIRECTORY = ""
K_SKIA_PATH = ""
k_SKIA_INCLUDE_PATH = ""
k_SKIA_LIBS_PATH = ""
K_ARCHIEVE_DIR = "skia"
K_BUILD_WITH_CLANG_ON_WINDOWS: bool = True
K_COMMON_BUILD_ARGS = [' skia_use_system_libwebp=false ',
                        ' skia_use_system_libjpeg_turbo=false',
                        ' skia_use_system_zlib=false',
                        ' skia_use_system_harfbuzz=false',
                        ' skia_use_system_libpng=false',
                        ' skia_use_system_libwebp=false',
                        ' skia_use_system_icu=false',
                        ' skia_use_system_expat=false']

def run_cmd(cmd, in_shell=False):
    my_env = os.environ.copy()
    path = my_env["PATH"]
    return_code = 0
    print(f"Running command : {cmd} in shell {in_shell}: {os.getcwd()} with PATH={path}")
    try:
        p = subprocess.run(cmd, stderr=sys.stderr, stdout=sys.stdout, env=my_env, shell=in_shell)
        return_code = p.returncode
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
            llvm_url = 'https://github.com/llvm/llvm-project/releases/download/llvmorg-15.0.7/LLVM-15.0.7-win64.exe'
            llvm_download_path: str = K_DOWNLOAD_DIR + '/LLVM-15.0.7-win64.exe'
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
    try:
        inShell = K_IS_WINDOWS
        cmd = ["python3", "tools/git-sync-deps"]

        if K_IS_WINDOWS:
            os.environ["EMSDK"] = K_SKIA_PATH + "/third_party/externals/emsdk"
            os.environ["EMSDK_NODE"] = K_SKIA_PATH + "/third_party/externals/emsdk/node/16.20.0_64bit/bin"
            os.environ["EMSDK_PYTHON"] = K_SKIA_PATH + "/third_party/externals/emsdk/upstream/emscripten"
            os.environ["PATH"] = K_SKIA_PATH + "/third_party/externals/emsdk" + os.pathsep + os.environ["PATH"]
            os.environ["PATH"] = K_SKIA_PATH + "/third_party/externals/emsdk/node/16.20.0_64bit/bin" + os.pathsep + \
                                 os.environ["PATH"]
            os.environ["PATH"] = K_SKIA_PATH + "/third_party/externals/emsdk/upstream/emscripten" + os.pathsep + \
                                 os.environ["PATH"]

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


def copy_and_publish(source_dir, destination_dir, lib_filter, delete_destination=True, skip_header=False, skip_package=False):
    source_dir = source_dir.strip()
    if delete_destination:
        if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
            shutil.rmtree(destination_dir)

    if not skip_header:
        out_dir = destination_dir + "/include"
        print(f"copying include files from {k_SKIA_INCLUDE_PATH} to {out_dir}")
        shutil.copytree(k_SKIA_INCLUDE_PATH, out_dir)
        libweb_dir = K_SKIA_PATH + "/third_party/externals/libwebp/src/webp/"
        out_dir = destination_dir + "/libwebp/"
        print(f"copying include files from {libweb_dir} to {out_dir}")
        shutil.copytree(libweb_dir, out_dir)

    index_of_first_slash = source_dir.find('/', 1)
    out_dir = destination_dir + "/" + source_dir[index_of_first_slash + 1:]
    os.makedirs(out_dir, exist_ok=True)
    # shutil.copytree (source_dir, out_dir)
    files = glob.iglob(os.path.join(source_dir, lib_filter))
    for file in files:
        if os.path.isfile(file):
            print(f"copying file from {file} to {out_dir}")
            shutil.copy2(file, out_dir)

    if not skip_package:
        extension = ""
        format_str = ""
        if K_IS_WINDOWS:
            format_str = "zip"
            extension = ".zip"
        else:
            format_str = "gztar"
            extension = ".tar.gz"

        archived = destination_dir + extension

        if os.path.exists(archived) and os.path.isfile(archived):
            os.remove(archived)

        compressed_file = shutil.make_archive(
            base_name=destination_dir,  # archive file name w/o extension
            format=format_str,  # available formats: zip, gztar, bztar, xztar, tar
            root_dir=destination_dir  # directory to compress
        )

        if os.path.exists(archived) and os.path.isfile(archived):
            print(f"Created archieve {archived}")
        else:
            print(f"Failed to create archieve {archived}")


def build_for_windows():
    if K_BUILD_WITH_CLANG_ON_WINDOWS:
        # X64 CLANG DEBUG
        cmd = (
            r'bin/gn gen out/win/x64/clang_debug --args="'
            ' is_official_build=true'
            ' is_debug=false'
            r' extra_cflags=[\"/MDd\"]'
            r' clang_win=\"C:\Program Files\LLVM\"'
            ' target_cpu=\\"x64\\"'
            ' skia_use_system_libjpeg_turbo=false'
            ' skia_use_system_zlib=false'
            ' skia_use_system_harfbuzz=false'
            ' skia_use_system_libpng=false'
            ' skia_use_system_libwebp=false'
            ' skia_use_system_icu=false'
            ' skia_use_system_expat=false"')
        if not run_cmd(cmd):
            run_cmd("third_party/ninja/ninja.exe -v -C out/win/x64/clang_debug")
            copy_and_publish("out/win/x64/clang_debug", "skia_win_x64_clang_debug_and_release",
                             "*.lib", True, True, True)

        # # X64 clang RELEASE
        cmd = (
            r'bin/gn gen out/win/x64/clang_release --args="'
            ' is_official_build=true'
            ' is_debug=false'
            r' extra_cflags=[\"/MD\"]'
            r' clang_win=\"C:\Program Files\LLVM\"'
            ' target_cpu=\\"x64\\"'
            ' skia_use_system_libjpeg_turbo=false'
            ' skia_use_system_zlib=false'
            ' skia_use_system_harfbuzz=false'
            ' skia_use_system_libpng=false'
            ' skia_use_system_libwebp=false'
            ' skia_use_system_icu=false'
            ' skia_use_system_expat=false"')
        if not run_cmd(cmd):
            run_cmd("third_party/ninja/ninja.exe -v -C out/win/x64/clang_release")
            copy_and_publish("out/win/x64/clang_release", "skia_win_x64_clang_debug_and_release", "*.lib", False)


def build_for_linux():
    global k_SKIA_LIBS_PATH
    out_dir_path = "out/linux/x64/clang_release"
    arg = '--args=is_official_build=true skia_use_system_harfbuzz=false cc="clang" cxx="clang++" '
    arg = arg + arg.join(K_COMMON_BUILD_ARGS)
    cmd = ["bin/gn", 'gen', out_dir_path, arg]

    if not run_cmd(cmd):
        cmd = ["third_party/ninja/ninja", "-C", out_dir_path]
        run_cmd(cmd)
        k_SKIA_LIBS_PATH = K_SKIA_PATH + out_dir_path
        copy_and_publish(out_dir_path, "skia_linux_x64_clang_release", "*.a")


def build_for_mac():
    global k_SKIA_LIBS_PATH

    if platform.machine() == "arm64":
            out_dir_path = "out/macos/arm64/clang_release"
            arg = '--args=is_official_build=true skia_use_system_harfbuzz=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_icu = false cc="clang" cxx="clang++" target_cpu="arm64"'
            arg = arg + arg.join(K_COMMON_BUILD_ARGS)
            cmd = ["bin/gn", 'gen', out_dir_path, arg]
            if not run_cmd(cmd):
                cmd = ["third_party/ninja/ninja", "-C", out_dir_path]
                run_cmd(cmd)
                k_SKIA_LIBS_PATH = K_SKIA_PATH + out_dir_path
                copy_and_publish(out_dir_path, "skia_macos_arm64_clang_release", "*.a")
            return

    out_dir_path = "out/macos/x64/clang_release"
    arg = '--args=is_official_build=true skia_use_system_harfbuzz=false skia_use_system_libjpeg_turbo=false  skia_use_system_libpng=false skia_use_system_icu = false cc="clang" cxx="clang++"'
    arg = arg + arg.join(K_COMMON_BUILD_ARGS)
    cmd = ["bin/gn", 'gen', out_dir_path, arg]
    if not run_cmd(cmd):
        cmd = ["third_party/ninja/ninja", "-C", out_dir_path]
        run_cmd(cmd)
        k_SKIA_LIBS_PATH = K_SKIA_PATH + out_dir_path
        copy_and_publish(out_dir_path, "skia_macos_x64_clang_release", "*.a")


def compile_skia():
    os.chdir(K_SKIA_PATH)
    if K_IS_WINDOWS:
        build_for_windows()
    elif platform.system() == "Linux":
        build_for_linux()
    elif platform.system() == "Darwin":
        build_for_mac()


def build_skia(build_only):
    if not build_only:
        clone_depot_tools()
        clone_skia()
    compile_skia()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
        # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Skia build.')
    # Add a boolean argument
    parser.add_argument('--build_only', type=bool, required=False, help='build only, do not sync')
    # Parse the command line arguments
    args = parser.parse_args()

    setup_global_variables()
    if K_IS_WINDOWS and K_BUILD_WITH_CLANG_ON_WINDOWS:
        install_clang()
    build_skia(args.build_only)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import vdf
from pathlib import Path,PosixPath,WindowsPath
from sys import platform
from subprocess import run
from shutil import rmtree
def getpath():
    if platform.startswith('linux'):
        target_path = Path.home() / Path('.steam/steam/steamapps/sourcemods/open_fortress')
    elif platform.startswith('win32'):
        target_path = Path('C:/Program Files (x86)/Steam/steamapps/sourcemods/open_fortress')
    else:
        print("you aren't on anything we support.")
        return -1
    if target_path.exists():
        print("Old Open fortress installations aren't compatible with the new launcher. Deleting...")
        #rmtree(target_path)
    elif target_path.parents[0].exists():
        print('All good, carrying on')
    elif target_path.parents[1].exists():
        print('Generating sourcemods folder...')
        Path.mkdir(target_path.parents[0])
    else:
        print("Ok something's wrong, put in your path manually")
        return -1
    return target_path

def sdk_download(path_to_steamapps):
    library_folders = vdf.load(open(path_to_steamapps/Path('libraryfolders.vdf')))['libraryfolders']
    already_downloaded = False
    for x in library_folders:
        try:
            z = library_folders[x]['apps']['243750']
            already_downloaded = True
        except KeyError:
            continue
    if not already_downloaded:
        print("not installed!")
        if platform.startswith('win32'):
            run(["start","steam://install/243750"])
        else:
            run(["xdg-open","steam://install/243750"])
    else:
        print("already installed!")


#handle other inputs here
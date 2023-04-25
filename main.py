import shutil
import sys
import tempfile
import traceback
import zipfile

from colormap_fixer import ColormapFixer, ColormapFixerError
from message_box import MessageBox


def full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]
    if exc is not None:
        del stack[-1]
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr


fixer = ColormapFixer()

if len(sys.argv) == 1:
    MessageBox.show_error("Failure", "Please drag and drop the texture pack to this executable to convert it "
                                     "(or specify the path to the texture pack as the first argument in the "
                                     "command line/terminal).")
    exit(1)

zip_location = sys.argv[1]

if not zipfile.is_zipfile(zip_location):
    MessageBox.show_error("Failure", "Provide a texture pack..")
    exit(1)

print("Now you will see many useless text...")
print("Extracting texture pack into temporary directory... ", end="")
with tempfile.TemporaryDirectory(prefix="colormapfixer") as directory:
    with zipfile.ZipFile(zip_location, "r") as zip_file:
        zip_file.extractall(directory)
    print("done")
    try:
        print("Starting initial fixing process...")
        fixer.fix(directory)
        print("Initial fixing process done")
        print("Archiving texture pack... ", end="")
        shutil.make_archive(f"./{'.'.join((zip_location.split('/')[-1].split('.')[:-1]))}_CMFixed", "zip", directory)
        print("done")
    except ColormapFixerError as colormap_error:
        MessageBox.show_error("Failure", colormap_error.message)
        exit(1)
    except:
        with open("./error.txt", "w") as error:
            error.write(full_stack())
            MessageBox.show_error("Failure", "Unknown error happened. Please create new issue on Github "
                                             "with contents of error.txt file")
        exit(1)

print("end of useless text spam :thumbs_up:")
MessageBox.show_info("Success", f"Done! Your converted ZIP is available under "
                                f"\"{'.'.join((zip_location.split('/')[-1].split('.')[:-1]))}_CMFixed.zip\"")

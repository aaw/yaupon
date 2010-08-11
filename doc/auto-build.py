import os
import time

start_path = "source"
ends_with = ".rst"
sleep_time = 2
build_command = "./build-docs"

def modified_files(path):
    try:
        if os.path.isfile(path):
            if not path.endswith(ends_with):
                return False
            mtime = os.stat(path).st_mtime
            if path not in files or files[path] < mtime:
                files[path] = mtime
                print '%s modified' % path
                return True
            else:
                return False
        else:
            return any(modified_files(os.path.join(path,x)) \
                       for x in os.listdir(path))
    except:
        return False

def populate_dict(path):
    if os.path.isfile(path) and path.endswith(ends_with):
        files[path] = os.stat(path).st_mtime
    elif os.path.isdir(path):
        for x in os.listdir(path):
            populate_dict(os.path.join(path,x))

files = {}
populate_dict(start_path)
while True:
    if modified_files(start_path):
        os.system(build_command)
    time.sleep(sleep_time)

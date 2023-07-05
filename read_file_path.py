import os
with open("dump_files/file_path_dump.txt", "r", encoding="utf8") as f:
    for file_path in f.readlines():
        print(os.path.splitext(file_path.strip()))
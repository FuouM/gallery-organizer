from util import get_file_paths

test_folder = "test/raw"
file_paths = get_file_paths(test_folder)
with open("file_path_dump.txt", "w", encoding="utf8") as f:
    for file_path in file_paths:
        f.write(f"{file_path}\n")
import os

def check_file(file_path):
    response = input(f"{file_path} already exists. Do you want to replace it? (y/n): ")
    return response.lower() == 'y'

def user_continue():
    response = input(f"Do you want to continue? (Append to existing file) (y/n): ")
    return response.lower() == 'y'


def get_file_paths(directory_path, absolute=False):
    if not os.path.isdir(directory_path):
        raise ValueError("Invalid directory path")

    file_paths = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if absolute:
                file_path = os.path.abspath(file_path)
            else:
                file_path = os.path.relpath(file_path, directory_path)
            file_paths.append(file_path)
    
    return file_paths

def get_file_paths_non_rec(directory_path, absolute=False):
    if not os.path.isdir(directory_path):
        raise ValueError("Invalid directory path")

    file_paths = []
    
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            if absolute:
                file_path = os.path.abspath(file_path)
            else:
                file_path = os.path.relpath(file_path, directory_path)
            file_paths.append(file_path)
    
    return file_paths


def get_file_names(directory_path, ext=False):
    file_names = []
    for path in get_file_paths(directory_path):
        file_name = os.path.basename(path)
        if ext:
            file_names.append(file_name)
        else:
            file_names.append(os.path.splitext(file_name)[0])
    
    return file_names

def extract_file_names(file_paths: list) -> list:
    file_names = []
    for path in file_paths:
        file_name = os.path.basename(path)
        file_names.append(os.path.splitext(file_name)[0])
    
    return file_names

def dump_file_paths(input_folder: str, output_file: str):
    file_paths = get_file_paths(input_folder)
    with open(output_file, "w", encoding="utf8") as f:
        for file_path in file_paths:
            f.write(f"{file_path}\n")

def dump_file_paths_ext_cond(input_folder: str, output_file: str, exts: list[str]):
    file_paths = get_file_paths(input_folder)
    with open(output_file, "w", encoding="utf8") as f:
        for file_path in file_paths:
            file_path: str
            if any(file_path.endswith(ext) for ext in exts):
                f.write(f"{file_path}\n")

def read_filepath_dump(input_txt_path: str):
    with open(input_txt_path, "r", encoding="utf8") as f:
        for file_path in f.readlines():
            print(os.path.splitext(file_path.strip()))
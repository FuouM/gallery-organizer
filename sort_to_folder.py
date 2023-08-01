import os
import time

from tqdm import tqdm
from extractor import *
from util import get_file_paths, extract_file_names, get_file_paths_non_rec
import shutil

def init_extractors() -> list[is_gallery_type]:
    is_tagged = is_tagged_string()
    is_4chan = is_4chan_timestamp()
    is_twitter = is_twitter_key()
    is_pixiv = is_pixiv_post()
    is_yandere = is_yandere_post()
    is_gelbooru = is_gelbooru_post()
    is_hash = is_hash_string()
    is_release = is_release_shot()
    is_soundfile = is_soundfile_post()
    is_non_ascii = is_not_ASCII()
    is_manga = is_manga_page()
    is_meaningful = is_meaningful_text()
    is_photo_file = is_photo()
    is_screenshot = is_screen_shot()
    is_date = is_date_time()
    is_misc = is_misc_semirandom()
    is_site = is_site_from()
    extractors = [
        is_tagged
        ,is_4chan
        ,is_twitter
        ,is_pixiv
        ,is_yandere
        ,is_gelbooru
        ,is_hash
        ,is_release
        ,is_soundfile
        ,is_non_ascii
        ,is_manga
        ,is_site
        ,is_misc
        ,is_meaningful
        ,is_photo_file
        ,is_screenshot
        ,is_date
    ]
    return extractors

def create_folder(directory: str, folder_name: str):
    path = os.path.join(directory, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f"Folder '{folder_name}' already exists at '{directory}'.")


directory = input("Enter folder path: ")

if os.path.isdir(directory):
    print(f"Working at {directory}")
    extractors = init_extractors()
    for extr in extractors:
        extr_name = extr.gallery_type
        create_folder(directory, extr_name)
    create_folder(directory, "is_unknown")
    file_lists = get_file_paths_non_rec(directory, True)
    print(f"Total files: {len(file_lists)}")

    for i, file_path in enumerate(tqdm(file_lists, desc="Processing files", unit="file")):
        file_raw = os.path.basename(file_path)
        file_raws = os.path.splitext(file_raw)
        filename = file_raws[0]
        # print(filename, file_raw, file_path)
        # print(file_raw)
        for extr in extractors:
            if tmp:= extr.test(filename):
                print(f"{i:<3}| Match {extr.gallery_type} {tmp}")
                dir_path = os.path.join(directory, extr.gallery_type)
                shutil.move(file_path, dir_path)
                break
        else:
            shutil.move(file_path, os.path.join(directory, "is_unknown"))

        
    
    
    
    
    
import os
import time
from extractor import *

test_folder = "test/raw"


st = time.time()
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
# Ordered by importance and occurence 
tests = [
    is_tagged
    ,is_date
    ,is_4chan
    ,is_pixiv
    ,is_yandere
    ,is_gelbooru
    ,is_release
    ,is_manga
    ,is_soundfile
    ,is_screenshot
    ,is_photo_file
    ,is_site
    ,is_misc
    ,is_meaningful
    ,is_twitter
    ,is_hash
    ,is_non_ascii
    ,
    # is random (default case)
]

def run_test(tests: list[is_gallery_type], dump_file_path: str, output_path:str, dump=False):
    dump_file = open(dump_file_path, "r", encoding="utf8")
    file_lists = [x.strip() for x in dump_file.readlines()]

    dump_file.close()
    print(f"Total files: {len(file_lists)}")
    output_dump = None
    if dump:
        output_dump = open(output_path, "w", encoding="utf8")
        
    for i, file_path in enumerate(file_lists):
        file_raw = os.path.splitext(file_path.strip())
        filename = file_raw[0]
        for test_type in tests:
            if tmp:= test_type.test(filename):
                if output_dump is not None:
                    output_dump.write(f"{i:<3}| Match {test_type.gallery_type} {tmp}\n")
                print(f"{i:<3}| Match {test_type.gallery_type} {tmp}")
                break
        else:
            if output_dump is not None:
                output_dump.write(f"{i:<3}| No match found (random) {repr(filename)}\n")
            print(f"{i:<3}| No match found (random) {repr(filename)}")

    if output_dump is not None:
        output_dump.close()

run_test(tests, 
         "dump_files/file_path_dump.txt", 
         "dump_files/output_dump.txt", 
         False)

# print(is_pixiv.test("gwitch_suletta_ham_Mineori_108521179_p0"))

print(f"\nTime taken: {time.time() - st:.2f}s")
import time
from extractor import *

test_folder = "test/raw"
dump_file = open("file_dump.txt", "r", encoding="utf8")
file_lists = [x.strip() for x in dump_file.readlines()]

dump_file.close()
print(f"Total files: {len(file_lists)}")

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
# Ordered by probability and importance
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
    ,is_meaningful
    ,is_twitter
    ,is_hash
    ,is_non_ascii
    ,is_misc
    # is random (default case)
]
def run_test():
    for i, filename in enumerate(file_lists):
        for test_type in tests:
            if tmp:= test_type.test(filename):
                # if test_type.gallery_type == "screenshot":
                # print(f"{i:<3}| Match {test_type.gallery_type} {tmp}")
                break
        else:
            print(f"{i:<3}| No match found (random) {repr(filename)}")
current_test = is_manga
# run_test()
test_list = (
    "FxAZQFfacAA5p3E.jpg_orig",
    "FxFUX6CagAEEz_y",
    'FJ396yjVUAQo8-0-orig',
    'Fk2Z_ubXoAMp4dy',
    'Fili_cwVsAMJAtM',
    'E079quPVIAEaQK4-orig',
    "FwzddJ3aQAEAwdH chuchu suletta",
    "Fwsu8-8aEAAQmc4 (1)",
    'FFm6PX-VUAAX8je-orig',
    'EIYcj_KW4AES_qw-orig',
    'FxDp8t3aMAMcWj3 chuchu felsi',
    'FsDkFCaakAAMSP5 Till'
)
for test_sample in test_list:
    print(
        is_twitter.test(test_sample)
    )
# run_test(current_test)
# run_test(current_test)
# print(is_pixiv.test("gwitch_suletta_ham_Mineori_108521179_p0"))
print(f"\nTime taken: {time.time() - st:.2f}s")
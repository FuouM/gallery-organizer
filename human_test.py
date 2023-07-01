import time
from extractor import *

test_folder = "test/raw"
dump_file = open("file_dump.txt", "r", encoding="utf8")
file_lists = [x.strip() for x in dump_file.readlines()]

dump_file.close()
print(f"Total files: {len(file_lists)}")

st = time.time()
# Test x3 no print
# 4chan: 0.13s
# Twitter: 0.08s
# pixiv: 0.09s
# yandere: 0.01s, gelbooru: 0.01s
# hash: 0.05s
# release: 0.07s
is_4chan = is_4chan_timestamp()
is_twitter = is_twitter_key()
is_pixiv = is_pixiv_post()
is_yandere = is_yandere_post()
is_gelbooru = is_gelbooru_post()
is_hash = is_hash_string()
is_release = is_release_shot()
def run_test(test_type):
    for i, filename in enumerate(file_lists):
        if tmp:= test_type.test(filename):
            print(f"{i:<3}| Match {test_type.gallery_type} {tmp}")
            pass

run_test(is_release)
# run_test()
# run_test()
# print(is_pixiv.test("gwitch_suletta_ham_Mineori_108521179_p0"))
print(f"\nTime taken: {time.time() - st:.2f}s")
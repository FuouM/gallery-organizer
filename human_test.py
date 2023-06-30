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
is_4chan = is_4chan_timestamp()
is_twitter = is_twitter_key()
is_pixiv = is_pixiv_post()
def run_test():
    for i, filename in enumerate(file_lists):
        # if tmp:= is_4chan.test(filename):
        #     print(f"{i:<3}| Match {is_4chan.gallery_type} {tmp}")
        #     pass
        # if tmp:= is_twitter.test(filename):
        #     print(f"{i:<3}| Match {is_twitter.gallery_type} {tmp}")
        #     pass
        if tmp:= is_pixiv.test(filename):
            print(f"{i:<3}| Match {is_pixiv.gallery_type} {tmp}")
            pass

run_test()
# run_test()
# run_test()
# print(is_pixiv.test("gwitch_suletta_ham_Mineori_108521179_p0"))
print(f"\nTime taken: {time.time() - st:.2f}s")
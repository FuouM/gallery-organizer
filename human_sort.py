from util import *
from nostril import nonsense
import time

test_folder = "test/raw"
# from nostril import nonsense

# print(get_file_names("test/raw", False))
# print(timestamp_datetime(1684905753220810))
# file_paths = get_file_paths(test_folder)
# file_lists = extract_file_names(file_paths)

# with open("file_dump.txt", "w", encoding="utf8") as f:
#     f.writelines(s + '\n' for s in file_lists)

dump_file = open("file_dump.txt", "r", encoding="utf8")
file_lists = [x.strip() for x in dump_file.readlines()]

dump_file.close()
# output_dump = open("output_dump.csv", "w", encoding="utf8")

# output_dump.write("type, filename, extract")

print(f"Total files: {len(file_lists)}")

def general_test(file_lists, num_start, num_end):
    st = time.time()
    hash_regex = [re.compile(regex) for regex in hash_regexes]  # Precompile regular expressions
    
    conditions = {
        'Characterized match': lambda file_name: file_name.startswith("__"),
        'Sound file match': lambda file_name: is_soundfile(file_name),
        'Default filename': lambda file_name: any(file_name.startswith(x) for x in default_filenames),
        'Whitelist match' : lambda file_name: any(x in file_name for x in white_list),
        'Site match': lambda file_name: is_possible_link(file_name),
        '4chan match': lambda file_name: is_4chan_stamp(file_name),
        'Datetime match': lambda file_name: is_datetime(file_name),
        'Manga match': lambda file_name: is_manga(file_name),
        'Pixiv match': lambda file_name: is_pixiv(file_name),
        'Yande.re match': lambda file_name: is_yandere(file_name),
        'Screenshot match': lambda file_name: is_screenshot(file_name),
        'Photo match': lambda file_name: is_photo(file_name),
        'Release match': lambda file_name: is_release_screenshot(file_name),
        'Hash match': lambda file_name: any(regex.search(file_name) for regex in hash_regex),
        'Random match': lambda file_name: is_probably_random(file_name),
        'Twitter possible match': lambda file_name: twitter_possible_id(file_name),
        'Too short (<7)': lambda file_name: count_digits_vs_alphabets(file_name)[1] < 7,
        'Possible meaning': lambda file_name: not nonsense(file_name),
        # 'Nonsense meaning': lambda file_name: True
    }
    
    for i, file_name in enumerate(file_lists):
        if i in range(num_start, num_end+1):
            print(f"{i:<3}| ", end="")
            try:
                for condition, action in conditions.items():
                    result = action(file_name)
                    if result:
                        print(f"{condition:<30} - {file_name}", end="")
                        if result is not True:
                            print(f" - {result}", end="")
                        print()
                        break
                else:
                    print(f"{'-' * 10} Error: {file_name} {'-' * 50}")
            except: 
                print(f"{'X' * 10} FATAL: {file_name} {'-' * 50}")
    
    print(f"\nTime taken: {time.time() - st:.2f}s")

# checkpoint: 7200
num_start = 0
num_end = 7807
general_test(file_lists, 0, 8000)
print("*" * 30)
# output_dump.close()
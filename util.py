import datetime
import os
import re
from urllib.parse import unquote

default_filenames = [
    "maxresdefault",
    "file",
    "ezgif",
    "download", "Download", "Clipboard", "clipboard",
    "image_", "image-", "images", "image."
    "Illustration", "illustration",
    "sample_", "sample-", "Untitled", "untitled"
]

hash_regexes = [
    '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}',
    '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
]

white_list = [
    "_by_",
    "_raw_", "Vol.", "vol.", "Chapter", "chapter", "Volume", "volume",
    "Ch.", "Pg."
]

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

def timestamp_datetime(timestamp: float, divisor=1_000_000) -> str:
    timestamp /= divisor

    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    if dt.year > 2023:
        return ""
    return dt.strftime('%Y%m%d')

def is_4chan_stamp(string: str) -> str:
    string = string.split("_")[0]
    # print(string)
    len_str = len(string)
    if len_str != 16 and len_str != 13 and len_str != 10:
        return ""

    divisor_map = {16: 1_000_000, 13: 1_000}
    divisor = divisor_map.get(len_str, 1)

    match = re.match(r'^\d+$', string)
    if match:
        return timestamp_datetime(int(string), divisor)

    return ""

twitter_suffix = [
    ".jpg_large", ".jpg large", ".jpg_orig"
    ".png_large", ".png large", ".png_orig"
    "-orig",  "-stitch"
]

def twitter_possible_id(media_key: str) -> dict:
    twitter_info = dict()
    if media_key.startswith("media_"):
        media_key = media_key.removeprefix("media_")
    else:
        for x in twitter_suffix:
            if media_key.endswith(x):
                media_key = media_key.removesuffix(x)
    media_keys = media_key.split(" ")
    if len(media_keys[0]) == 15:
        twitter_info["id"] = media_keys[0]
        if len(media_keys) > 1:
            twitter_info["extra"] = media_keys[1:]
    elif len(media_key) > 16:
        if media_key[15] == "_":
            raw = media_key.split("_")
            if len(raw[0]) == 15:
                twitter_info["id"] = raw[0]
                twitter_info["extra"] = raw[1:]
        elif media_key[15] == ".":
            raw = media_key.split(".")
            if len(raw[0]) == 15:
                twitter_info["id"] = raw[0]
    return twitter_info

sites = [
    "seiga.nicovideo.jp",
    "twitter.com",
    "tumblr", "twitter_"
]

def is_possible_link(string: str) -> list:
    link_info = []
    if any([string.startswith(x) for x in sites]):
        link_info = string.split(" ")
    return link_info

def is_datetime(string: str) -> bool:
    pattern = r'^(20\d{2})([-/]?)(0[1-9]|1[0-2])\2(0[1-9]|[12]\d|3[01]).*'
    return bool(re.match(pattern, string))

def is_pixiv(string: str) -> dict:
    pixiv_info = dict()
    if string.startswith("p_") or string.startswith("P_"):
        # p_002
        pixiv_info["page"] = string.split("_")[-1]
    elif string.startswith("illust_"):
        # illust_98246152_20220513_212357
        raw = string.split("_")
        pixiv_info["link"] = f"https://www.pixiv.net/en/artworks/{raw[1]}"
    else:
        pattern = r"^(?:(.+)_)?p(\d+)(?:[\s_](.+))?$"
        match = re.match(pattern, string)
        if match:
            raw = match.group(1).split("_")
            for i in raw:
                if i.isnumeric():
                    post_id = i
                    raw.remove(i)
                    pixiv_info["link"] = f"https://www.pixiv.net/en/artworks/{post_id}"
                    pixiv_info["page"] = match.group(2)
                    extra = match.group(3)
                    if extra:
                        pixiv_info["extra"] = extra
                    if raw:
                        pixiv_info["extra"] += raw
                        
    return pixiv_info

def is_yandere(string: str) -> dict:
    # yande.re 747477 sample animal_ears ass 
    # bottomless chiyoda_momo horns machikado_mazoku mel_(melty_pot) 
    # nekomimi tail yoshida_yuuko_(machikado_mazoku) yuri
    yandere_info = dict()
    if string.startswith("yande.re"):
        raw = string.split(" ")
        post_id = raw[1]
        tags = raw[2:]
        yandere_info["link"] = f"https://yande.re/post/show/{post_id}"
        yandere_info["tags"] = tags
        
    return yandere_info

release_magic_words = [
    "720p", "1080p", "h264", "mkv", "HEVC", "BDRip", "OVA", "X264",
    "720P", "1080P", "BD "
]

release_patterns_1 = [
    r'^(.+?) - (\d+) \[(.+?)\]\[(.+?)\]', # "Birdie Wing - Golf Girls&#039; Story - 19 [1080p HEVC][028727AC].mkv_snapshot_03.12_[2023.05.26_23.14.04]"
    r'^(.*?)\s-\s(.*?)\s-\s(.*?)\s\[(.*?)\].*$', # "cap_[Exp] Ookami Shoujo to Kuro Ouji - S01E07 - Mutual Love -White Day- [BDRip 1920x1080 x264 FLAC] [4DA4C155]_00_20_13_13"
]

release_patterns_2 = [
    r"(?:\[(.*?)\]\s)?(.*?)\s-\s(\d{2})", # "[anon] The Idolmaster Cinderella Girls U149 - 01v4.mkv_snapshot_01.04.524"
]

def is_release_screenshot(string: str) -> dict:
    screenshot_info = dict()
    if any([x in string for x in release_magic_words]):
        screenshot_info["raw"] = string

    for pattern in release_patterns_1:
        match = re.match(pattern, string)
        if match:
            screenshot_info.pop("raw")
            screenshot_info["title"] = match.group(1)
            screenshot_info["episode"] = match.group(2)
            screenshot_info["format"] = match.group(3)
            screenshot_info["id"] = match.group(4)
            return screenshot_info
    # for pattern in release_patterns_2:
    #     match = re.match(pattern, string)
    #     if match:
    #         screenshot_info.pop("raw")
    #         screenshot_info["title"] = match.group(1)
    #         screenshot_info["episode"] = match.group(2)
    #         return screenshot_info
    return screenshot_info

screenshot_prefixes = [
    "screenshot", "screen shot", "screen_shot",
    "Screenshot", "Screen Shot", "Screen_shot", "Screen_Shot",
    
]
def is_screenshot(string: str) -> dict:
    screenshot_info = dict()
    if string.startswith("mpv-shot"):
        screenshot_info["extra"] = string.removeprefix("mpv-shot")
        return screenshot_info
    # vlcsnap-2019-11-03-21h22m03s730
    if string.startswith("vlcsnap-"):
        match = re.search(r'(\d{4}-\d{2}-\d{2})-(\d{2})h(\d{2})m(\d{2})s(\d{3})', string)
        if match:
            date = match.group(1)
            hour = match.group(2)
            minute = match.group(3)
            second = match.group(4)
            millisecond = match.group(5)
            
            screenshot_info["date"] = date
            screenshot_info["time"] = f"{hour}:{minute}:{second}.{millisecond}"
        else:
            screenshot_info["extra"] = string.removeprefix("vlcsnap-")
        return screenshot_info
    for prefix in screenshot_prefixes:
        if string.startswith(prefix):
            raw = string.removeprefix(prefix).split("_")
            screenshot_info["extra"] = raw
    return screenshot_info

def count_digits_vs_alphabets(s: str) -> tuple[int, int]:
    num_digits = 0
    num_alpha = 0
    for char in s:
        if char.isdigit():
            num_digits += 1
        elif char.isalpha():
            num_alpha += 1
    return (num_digits, num_alpha)

def is_probably_random(s: str, threshold = 1) -> bool:
    num_digits, num_alpha = count_digits_vs_alphabets(s)
    return num_digits - num_alpha > threshold

photo_prefixes = [
    "img_", "IMG_",
]


def is_photo(string: str) -> dict:
    photo_info = dict()
    if string.startswith("IMG-"):
        photo_info["extra"] = string.removeprefix("IMG-")
    if any(string.startswith(x) for x in photo_prefixes):
        raw = string.split("_")
        if len(raw[1]) == 8:
            photo_info["date"] = raw[1]
            photo_info["extra"] = raw[2:]
        else: 
            photo_info["extra"] = raw[1:]
    elif string.startswith("FB_IMG"):
        raw = string.split("_")
        photo_info["datetime"] = timestamp_datetime(int(raw[-1]), 1000)
    return photo_info

def is_soundfile(string: str) -> dict:
    soundfile_info = dict()
    match = re.search(r'^(.+)?\[sound=(.+)\]$', string)
    if match:
        soundfile_info["name"] = match.group(1)
        file_link = unquote(match.group(2))
        if not file_link.startswith("http"):
            file_link = "http://" + file_link
        soundfile_info["file_link"] = file_link
    return soundfile_info

def is_gelbooru(string: str) -> dict:
    gelbooru_info = dict()
    if string.startswith("gelbooru"):
        raw = string.split("_")
        gelbooru_info["link"] = f"https://gelbooru.com/index.php?page=post&s=view&id={raw[1]}"
    return gelbooru_info


def is_manga(string: str) -> dict:
    manga_info = dict()
    match = re.search(r"^(.*?)\s-\sc(\d+).*?\-\sp(\d+).*", string)
    if match:
        manga_info["title"] = match.group(1)
        manga_info["chapter"] = match.group(2)
        manga_info["page"] = match.group(3)
    return manga_info
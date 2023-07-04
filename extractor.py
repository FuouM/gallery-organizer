import re
import datetime
from urllib.parse import unquote
from typing import Optional


class datetime_processor:
    def __init__(self) -> None:
        self.divisor_map = {
            16: 1_000_000,
            13: 1_000,
            10: 1
        }
        
        self.year = datetime.date.today().year
        self.date_format = r'%Y%m%d'
        self.timezone = datetime.timezone.utc
    
    def find_timestamp(self, substrings: list[str]):
        for raw in substrings:
            raw_length = len(raw)
            if raw.isnumeric() and any(raw_length == x for x in (10, 13, 16)):
                raw_date = self.timestamp_to_datetime(
                    int(raw), divisor=self.divisor_map[raw_length])
                if raw_date:
                    return raw_date
        return None

    def timestamp_to_datetime(self, timestamp: float, divisor=1_000_000) -> str:
        timestamp /= divisor
        dt = datetime.datetime.fromtimestamp(timestamp, tz=self.timezone)
        if dt.year > self.year:
            return ""
        return dt.strftime(self.date_format)

class is_gallery_type:
    def __init__(self, gallery_type: str) -> None:
        self.gallery_type = gallery_type
        self._delimiter = "_"
        self._delimiter_thres = 3
    
    def test(self, string: str) -> dict:
        return {
            "type": self.gallery_type,
            "raw": string
        }

class is_4chan_timestamp(is_gallery_type):
    def __init__(self, dt_processor: Optional[datetime_processor] = None) -> None:
        super().__init__("4chan_timestamp")
        if dt_processor is None:
            self.dt_processor = datetime_processor()
        else:
            self.dt_processor = dt_processor
    
    def test(self, string: str) -> dict:
        raws = self.preprocess(string)
        if raws:
            raw_date = self.dt_processor.find_timestamp(raws)
            if raw_date:
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "datetime": raw_date
                }
        return {}

    def preprocess(self, string: str):
        substrings = string.split(self._delimiter)
        if len(substrings) > self._delimiter_thres:
            return None
        return substrings

class is_twitter_key(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("twitter_key")
        self.possible_prefix = "media_"
        self.possible_suffixes = (
            ".jpg_large", ".jpg large", ".jpg_orig",
            ".png_large", ".png large", ".png_orig",
            "-orig",  "-stitch"
        )
        self.special_pattern = re.compile(r'(.*-\d{19})-img(\d+)')
        self.length = 15
        self.possible_delimiter = " "
    
    def test(self, string: str) -> dict:
        match = re.search(self.special_pattern, string)
        if match:
            before, number = match.groups()
            return {
                "type": self.gallery_type,
                "raw" : string,
                "artist" : before,
                "number": number
            }
        raw, is_hit = self.preprocess(string)
        if raw and is_hit:
            assert type(raw) is str
            return {
                "type": self.gallery_type,
                "raw" : raw,
                "id"  : raw
            }
        elif raw:
            if type(raw) == str:
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "id": raw
                }
            tmp_id, tmp_extra = self.find_id_and_extra(raw)
            if tmp_id:
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "id": tmp_id,
                    "extra": tmp_extra
                }
        return {}
    
    def find_id_and_extra(self, substrings):
        tmp_id = None
        tmp_extra = []
        found_id = False
        for sub_raw in substrings:
            _tmp_raw = sub_raw.replace(" ", "")
            if not found_id and len(_tmp_raw) == self.length:
                tmp_id = _tmp_raw
                found_id = True
            else:
                tmp_extra.append(sub_raw)
        return tmp_id, tmp_extra
    
    def preprocess(self, string: str):
        string = string.strip()
        is_hit = True
        if string.startswith(self.possible_prefix):
            return (string.removeprefix(self.possible_prefix), is_hit)
        for suffix in self.possible_suffixes:
            if string.endswith(suffix):
                return (string.removesuffix(suffix), is_hit)
        if len(string) == self.length:
            return (string, False)
        substrings = string.split(self._delimiter)
        if len(substrings) == 1:
            substrings = string.split(self.possible_delimiter)
        if len(substrings) > self._delimiter_thres:
            return None, False
        return (substrings, False)
    
class is_pixiv_post(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("pixiv_id")
        self.link_template = "https://www.pixiv.net/en/artworks/"
        self.prefixes = {
            "page": ["p_", "P_", "p-"],
            "illust": "illust_" # illust_98246152_20220513_212357
        }
        self.pattern = re.compile(r"^(?:(.+)_)?p(\d+)(?:[\s_](.+))?$")
        self.page_pattern = re.compile(r'(.*)_p(\d+)(.*)')
        self.page_thres = 1000
    
    def test(self, string: str) -> dict:
        methods = [self.parse_page, 
                   self.parse_illust_prefix,
                   self.parse_pattern
                ]
        for method in methods:
            result = method(string)
            if result:
                return result
        return {}

    def parse_page(self, string: str):
        for prefix in self.prefixes["page"]:
            if string.startswith(prefix) :
                return {
                    "type": self.gallery_type,
                    "raw": string,
                    "page" : string.removeprefix(prefix),
                }
        match = re.search(self.page_pattern, string)
        if match:
            before, page, after = match.groups()
            return {
                "type": self.gallery_type,
                "raw": string,
                "page": page,
                "extra": (" ".join((before, after))).strip()
            }

    def parse_illust_prefix(self, string: str):
        if string.startswith(self.prefixes["illust"]):
            raw = string.split("_")
            return {
                "type": self.gallery_type,
                "raw" : string,
                "id"  : raw[1],
                "link": self.link_template + raw[1],
                "datetime": raw[2:]
            }
        return None
    
    def parse_pattern(self, string: str):
        match = re.match(self.pattern, string)
        if match:
            tmp_id, tmp_pg, tmp_extra = self.extract_info_from_groups(match.groups())
            if tmp_id and tmp_pg:
                return {
                    "type": self.gallery_type,
                    "raw": string,
                    "id" : tmp_id,
                    "page": tmp_pg,
                    "extra": tmp_extra,
                    "link": self.link_template + tmp_id,
                    "output": match.groups()
                }
        return None


    def extract_info_from_groups(self, groups):
        tmp_id = None
        tmp_pg = None
        tmp_extra = []
        for group in groups:
            if group:
                sub_groups = group.split(self._delimiter)
                for sub_group in sub_groups:
                    if not tmp_id and sub_group.isnumeric() and int(sub_group) > self.page_thres:
                        tmp_id = sub_group
                    elif not tmp_pg and sub_group.isnumeric() and int(sub_group) < self.page_thres:
                        tmp_pg = sub_group
                    else:
                        tmp_extra.append(sub_group)
        return tmp_id, tmp_pg, tmp_extra

class is_yandere_post(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("yandere_id")
        self.prefix = "yande.re"
        self.link_template = "https://yande.re/post/show/"
        self._delimiter = " "
    
    def test(self, string: str) -> dict:
        if string.startswith(self.prefix):
            raw = string.split(self._delimiter)
            return {
                "type": self.gallery_type,
                "raw" : string,
                "post_id": raw[1],
                "tags": raw[2:],
                "link": self.link_template + raw[1]
            }
        return {}
    
class is_gelbooru_post(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("gelbooru_id")
        self.prefix = "gelbooru"
        self.link_template = "https://gelbooru.com/index.php?page=post&s=view&id="
        
    def test(self, string: str) -> dict:
        if string.startswith(self.prefix):
            raw = string.split(self._delimiter)
            return {
                "type": self.gallery_type,
                "raw" : string,
                "post_id": raw[1],
                "extra": raw[2:],
                "link": self.link_template + raw[1]
            }
        return {}

class is_hash_string(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("hash_string")
        self.patterns = [re.compile(regex) for regex in (
            '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}',
            '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        )]
    
    def test(self, string: str) -> dict:
        if any(regex.search(string) for regex in self.patterns):
            return {
                "type": self.gallery_type,
                "raw" : string
            }
        return {}
    
class is_release_shot(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("release_screenshot")
        self.prefix = "["
        self.magic_words = {
            "720p", "1080p", "h264", "H264", "mkv", "HEVC", "BDRip", "OVA", "X264",
            "720P", "1080P", "BD ", "AAC"
        }
        self.bracket_regex = re.compile(r'\[(.*?)\]')
    
    def test(self, string: str) -> dict:
        if any(magic in string for magic in self.magic_words):
            return {
                "type": self.gallery_type,
                "raw" : string,
                "extra_1": re.findall(self.bracket_regex, string),
                "extra_2": re.sub(self.bracket_regex, '', string)
            } 
        return {}
    
class is_soundfile_post(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("soundfile_dl")
        self._dl_prefix = "[sound="
        self._base_url  = "http://"
        self._dl_suffix = "]"
    
    def test(self, string: str) -> dict:
        if self._dl_prefix in string:
            raws = self.parse_soundfile(string)
            return {
                "type": self.gallery_type,
                "raw" : string,
                "link": raws[0],
                "extra": raws[1],
            }
        return {}
    
    def parse_soundfile(self, string: str):
        raws = string.split(self._dl_prefix)
        filename = raws[0]
        link, extra = raws[1].split(self._dl_suffix)
        link = unquote(link)
        if not link.startswith(self._base_url):
            link = self._base_url + link
            
        if extra:
            return (link, [filename, extra])
        else:
            return (link, filename)

class is_not_ASCII(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("non_ascii")
    
    def test(self, string: str) -> dict:
        if not string.isascii():
            ascii_chars, unicode_chars = self.separate_ascii(string)
            return {
                "type": self.gallery_type,
                "raw" : string,
                "ascii": ascii_chars,
                "unicode": unicode_chars
            }
        return {}
    
    def separate_ascii(self, string: str):
        if string.isascii():
            return string
        ascii_chars = ''.join([char for char in string if char.isascii()])
        unicode_chars = ''.join([char for char in string if not char.isascii()])
        return [ascii_chars, unicode_chars]



class is_manga_page(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("manga_page")
        self.pattern = re.compile(r"^(.*?)\s-\sc(\d+).*?\-\sp(\d+).*")
        self.magic_words = (
            "Vol.", "vol.", "Ch.", "ch.", "Pg.",
            "Volume", "volume", 
            "Chapter", "chapter", 
            "Page", "page", 
            "_raw_"
        )
        
    def test(self, string: str) -> dict:
        match = re.search(self.pattern, string)
        if match:
            return {
                "type": self.gallery_type,
                "raw" : string,
                "title": match.group(1),
                "chapter": match.group(2),
                "page": match.group(3)
            }
        if any(magic in string for magic in self.magic_words):
            return {
                "type": self.gallery_type,
                "raw" : string
            }
        return {}

class is_meaningful_text(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("meaningful")
        from nostril import nonsense
        self.nonsense = nonsense
        self.min_length = 6 # nonsense's input min_length = 6 (only count ascii, alpha, nospace)
        self.alpha_thres = 2
    
    def test(self, string: str) -> dict:
        alpha, num = self.separate_alpha_num(string)
        alpha_trim = alpha.replace(" ", "")
        trim_len = len(alpha_trim)
        if trim_len < self.min_length and trim_len - len(num) > self.alpha_thres \
            or trim_len >= self.min_length and not self.nonsense(string):
            return {
                "type": self.gallery_type,
                "raw" : string,
                "alpha": alpha,
                "num" : num
            }
            
        return {}
    
    def separate_alpha_num(self, string: str) -> tuple[str, str]:
        alpha = ''.join([char for char in string if char.isalpha() and char.isascii()])
        num = ''.join([char for char in string if char.isnumeric()])
        return alpha, num

class is_tagged_string(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("tagged")
        self._delimiter = "__"
        self._artist = "_drawn_by_"
        self._sample = "sample-"
        # __[tags...]_drawn_by_[artist]__[hash]
        # __[tags...]_[series]_drawn_by_[artist]__sample-[hash]
    
    def test(self, string: str) -> dict:
        if not string.startswith(self._delimiter):
            return {}

        raws = string.split(self._delimiter)
        tags_artist = raws[1]
        if self._artist in tags_artist:
            tags, artist = tags_artist.split(self._artist)
        else:
            tags = tags_artist
            artist = "is_empty"

        result = {
            "type": self.gallery_type,
            "raw": string,
            "tags": tags,
            "artist": artist
        }

        if len(raws) > 3:
            img_hash = raws[2].removeprefix(self._sample)
            result["hash"] = img_hash

        return result

class is_photo(is_gallery_type):
    def __init__(self, dt_processor: Optional[datetime_processor] = None) -> None:
        super().__init__("photo")
        self.prefixes = {
            "img": ("IMG_", "img_"),
            "img_dt": "IMG-",
            "fb" : "FB_IMG",
            "photo": "photo_"
        }
        if dt_processor is None:
            self.dt_processor = datetime_processor()
        else:
            self.dt_processor = dt_processor
            
    def test(self, string: str) -> dict:
        if string.startswith(self.prefixes["img_dt"]):
            return {
                "type": self.gallery_type,
                "raw" : string,
                "extra": string.removeprefix(self.prefixes["img_dt"])
            }
        for prefix in self.prefixes["img"]:
            if string.startswith(prefix):
                raws = string.split(self._delimiter)
                # IMG_[date]_[extra]
                if len(raws[1]) == 8:
                    return {
                        "type": self.gallery_type,
                        "raw" : string,
                        "date": raws[1],
                        "extra": raws[2:]
                    }
                else:
                    return {
                        "type": self.gallery_type,
                        "raw" : string,
                        "extra": raws[1:]
                    }
        if string.startswith(self.prefixes["fb"]):
            raws = string.split(self._delimiter)
            return {
                "type": self.gallery_type,
                "raw" : string,
                "datetime": self.dt_processor.timestamp_to_datetime(int(raws[-1]), 1000),
            }
        if string.startswith(self.prefixes["photo"]):
            return {
                "type": self.gallery_type,
                "raw" : string,
                "extra": string.removeprefix(self.prefixes["photo"]),
            }
        return {}

class is_screen_shot(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("screenshot")
        self.pattern = re.compile(r'(.*?)(\bscreen[-_\s]?shot\b)(.*)', re.IGNORECASE)
        self.prefixes = {
            "mpv": "mpv-shot",
            "vlc": "vlcsnap-"
        }
        self.vlc_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})-(\d{2})h(\d{2})m(\d{2})s(\d{3})')
        
    def test(self, string: str) -> dict:
        match = re.search(self.pattern, string)
        if match:
            before, _, after = match.groups()
            return {
                "type": self.gallery_type,
                "raw" : string,
                "output": (" ".join((before, after))).strip()
            }
        if string.startswith(self.prefixes["vlc"]):
            match = re.search(self.vlc_pattern, string)
            if match:
                date = match.group(1)
                hour = match.group(2)
                minute = match.group(3)
                second = match.group(4)
                millisecond = match.group(5)
                
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "date": date,
                    "time": f"{hour}:{minute}:{second}.{millisecond}"
                }
                
            else:
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "extra": string.removeprefix(self.prefixes["vlc"])
                }
        
        if string.startswith(self.prefixes["mpv"]):
            return {
                "type": self.gallery_type,
                "raw" : string,
                "extra": string.removeprefix(self.prefixes["mpv"])
            }
        return {}

class is_site_from(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("semirandom")
        self.site_prefixes = {
            "twitter": "twitter.com",
            "tumblr" : "tumblr_",
            "seiga": "seiga.nicovideo.jp"
        }
    
    def test(self, string: str) -> dict:
        for site, prefix in self.site_prefixes.items():
            if string.startswith(prefix):
                return {
                    "type": "site",
                    "raw": string,
                    "site": site,
                    "extra": string.removeprefix(prefix)
                }
        return {}

class is_misc_semirandom(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("semirandom")
        self.prefixes = {
            "sample": ["sample_", "sample-"],
            "default": (
                "file", "image_", "image-", "images", "image.", "i-", "maxresdefault", 
                "download", "Download", "Clipboard", "clipboard",
                "Illustration", "illustration"
            ),
            "ezgif": ["ezgif-"],
            
        }
        self.pixiv_id_len = 7 # 2303363
    
    def test(self, string: str) -> dict:
        for prefixes in (self.prefixes["sample"],
                       self.prefixes["ezgif"]):
            for prefix in prefixes:
                if string.startswith(prefix):
                    return {
                        "type": self.gallery_type,
                        "raw" : string,
                        "prefix": prefix,
                        "extra": string.removeprefix(prefix)
                    }
        
        for default in self.prefixes["default"]:
            if string.startswith(default):
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "rand_type": "default",
                    "extra": string.removeprefix(default)
                }
                
        if string[:self.pixiv_id_len].isnumeric() and string[0] != "0":
            return {
                "type": self.gallery_type,
                "raw" : string,
                "rand_type": "possible_pixiv",
                "id": string[:self.pixiv_id_len],
                "extra": string[self.pixiv_id_len:]
            }
        return {}

class is_date_time(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("datetime")
        self.patterns = {
            "yyyyxxxx_tttttt": re.compile(r'(\d{8})_(\d{6}).*'),
            "yyyy-xx-xx[-_ ]tt_tt_tt": re.compile(r'(\d{4}-\d{2}-\d{2})[-_\s](\d{2}[-_]\d{2}[-_]\d{2})'),
            "yy-xx-xx-tttttt": re.compile(r'(\d{4}-\d{2}-\d{2})[-_](\d{6})'),
            }
    
    def test(self, string: str) -> dict:
        for pattern in self.patterns.values():
            match = re.search(pattern, string)
            if match:
                # if len(match.groups()) :
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "date" : match.group(0),
                    "time" : match.group(1),
                    "extra" : match.group(2)
                }
        return {}
    
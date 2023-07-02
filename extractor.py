import re
import datetime
from urllib.parse import unquote

class is_gallery_type:
    def __init__(self, gallery_type: str) -> None:
        self.gallery_type = gallery_type
        self._delimiter = "_"
        self._delimiter_thres = 2
    
    def test(self, string: str) -> dict:
        return {
            "type": self.gallery_type,
            "raw": string
        }

class is_4chan_timestamp(is_gallery_type):
    def __init__(self) -> None:
        super().__init__(
            "4chan_timestamp"
        )
        
        self.divisor_map = {
            16: 1_000_000,
            13: 1_000,
            10: 1
        }
        
        self.year = datetime.date.today().year
        self.date_format = r'%Y%m%d'
        self.timezone = datetime.timezone.utc
    
    def test(self, string: str) -> dict:
        raws = self.preprocess(string)
        if raws:
            raw_date = self.find_timestamp(raws)
            if raw_date:
                return {
                    "type": self.gallery_type,
                    "raw" : string,
                    "datetime": raw_date
                }
        return {}

        
    def find_timestamp(self, substrings):
        for raw in substrings:
            raw_length = len(raw)
            if raw.isnumeric() and any(raw_length == x for x in (10, 13, 16)):
                raw_date = self._timestamp_to_datetime(
                    int(raw), divisor=self.divisor_map[raw_length])
                if raw_date:
                    return raw_date
        return None

    def _timestamp_to_datetime(self, timestamp: float, divisor=1_000_000) -> str:
        timestamp /= divisor
        dt = datetime.datetime.fromtimestamp(timestamp, tz=self.timezone)
        if dt.year > self.year:
            return ""
        return dt.strftime(self.date_format)

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
            ".jpg_large", ".jpg large", ".jpg_orig"
            ".png_large", ".png large", ".png_orig"
            "-orig",  "-stitch"
        )
        self.length = 15
    
    def test(self, string: str) -> dict:
        raw, is_hit = self.preprocess(string)
        if raw and is_hit:
            assert type(raw) is str
            return {
                "type": self.gallery_type,
                "raw" : raw,
                "id"  : raw
            }
        elif raw:
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
        is_hit = True
        if string.startswith(self.possible_prefix):
            return (string.removeprefix(self.possible_prefix), is_hit)
        for suffix in self.possible_suffixes:
            if string.endswith(suffix):
                return (string.removesuffix(suffix), is_hit)
        substrings = string.split(self._delimiter)
        if len(substrings) > self._delimiter_thres:
            return None, False
        return (substrings, False)
    
class is_pixiv_post(is_gallery_type):
    def __init__(self) -> None:
        super().__init__("pixiv_id")
        self.link_template = "https://www.pixiv.net/en/artworks/"
        self.prefixes = {
            "page": ["p_", "P_"],
            "illust": "illust_" # illust_98246152_20220513_212357
        }
        self.pattern = re.compile(r"^(?:(.+)_)?p(\d+)(?:[\s_](.+))?$")
        self.page_thres = 1000
    
    def test(self, string: str) -> dict:
        result = self.parse_illust_prefix(string)
        if result:
            return result
        result = self.parse_pattern(string)
        if result:
            return result
        return {}


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
            "Volume", "volume", "Vol.", "vol.",
            "Chapter", "chapter", "Ch.", "ch."
            "Page", "page", "Pg.",
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

            
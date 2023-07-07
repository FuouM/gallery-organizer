from PIL import Image
import numpy as np
import torch
import TorchDeepDanbooru.deep_danbooru_model as deep_danbooru_model
from torch.amp.autocast_mode import autocast
import os
from typing import Optional
import json
import time

model_path = "model\\DeepDanbooru\\model-resnet_custom_v3.pt"


def set_device():
    if torch.cuda.is_available():
        print("CUDA IS AVAILABLE. GPU MODE")
        return "cuda"
    else:
        print("CUDA NOT AVAILABLE. CPU MODE")
        return "cpu"
        
class danbooru_recognizer:
    def __init__(self, model_path: Optional[str] = None, general_thres=0.9, char_thres=0.5,
                 config_path: Optional[str] = None) -> None:
        
        self.model = deep_danbooru_model.DeepDanbooruModel()
        self.device = set_device()
        if model_path is None:
            model_path = "model\\DeepDanbooru\\model-resnet_custom_v3.pt"
            assert os.path.isfile(model_path), "Model file not found"
        self.model_path = model_path
        self.general_thres = general_thres
        self.char_thres = char_thres
        self.unsupported_ext = {
            "animated": ("gif", "webm")
        }
        
        if config_path is None:
            config_path = "model\\DeepDanbooru\\categories.json"
            assert os.path.isfile(config_path), "Config file not found"
            
            with open(config_path, "r") as config:
                categories = json.load(config)
                self.char_index = categories[1]["start_index"]
                self.rating_index = categories[2]["start_index"]

    
    def load(self, is_eval = True):
        st = time.time()
        self.model.load_state_dict(torch.load(self.model_path))
        if is_eval:
            self.model.eval()
            self.model.half()
            if self.device == "cuda":
                self.model.cuda()
        print(f"Model loaded in {time.time() - st:.2f}s")
                
    def inference_gpu(self, file_paths: list[str]) -> list[tuple[np.ndarray, dict]]:
        """Danbooru tags from list of image paths

        Returns:
            list[tuple[np.ndarray, dict]]: list of pairs of
            
                result [result np array of probability of each tag]
                
                result_dict [{Filepath, Character (tags), General (tags), Rating}]
        """
        st = time.time()
        res = []
        with torch.no_grad(), autocast(self.device):
            for file_path in file_paths:
                img = self.open_and_preprocess(file_path)
                if img:
                    img_to_array = np.expand_dims(np.array(img, dtype=np.float32), 0) / 255
                    array_to_tensor = torch.from_numpy(img_to_array).cuda()
                    
                    result = self.model(array_to_tensor)[0].detach().cpu().numpy()
                    
                    # the result is an array of probability at tag[i]
                    res_dict = self.parse_result_to_dict(result, file_path)
                    res.append((result, res_dict))
                    print(res_dict)
            print(f"{len(file_paths)} images done in {time.time() - st:.2f}s")
        return res
    
    def get_tag_from_index(self, index: int) -> str:
        return self.model.tags[index]
    
    def parse_result_to_dict(self, result: np.ndarray, filepath: str) -> dict:
        char_tags = []
        gen_tags = []
        ratings = []
        
        for index, probability in enumerate(result):
            tag = self.get_tag_from_index(index)
            if index < self.char_index:
                if probability >= self.general_thres:
                    gen_tags.append((tag, probability))
                continue
            elif index < self.rating_index:
                if probability >= self.char_thres:
                    char_tags.append((tag, probability))
                continue
            else:
                ratings.append((tag, probability))
               
        return {
            "Filepath" : filepath,
            "Character": self.extract_strings(self.sort_by_probability_descending(char_tags)),
            "General"  : self.extract_strings(self.sort_by_probability_descending(gen_tags)),
            "Rating"  : self.get_max_probability_item(ratings)[0]
        }    
                                
    def get_max_probability_item(self, lst: list[tuple[str, float]]) -> tuple[str, float]:
        max_item = max(lst, key=lambda x: x[1])
        return max_item
    
    def sort_by_probability_descending(self, lst: list[tuple[str, float]]) -> list[tuple[str, float]]:
        sorted_lst = sorted(lst, key=lambda x: x[1], reverse=True)
        return sorted_lst
    
    def extract_strings(self, lst: list[tuple[str, float]]):
        return [item[0] for item in lst]
                    
    def open_and_preprocess(self, file_path: str) -> Image.Image | None:
        if os.path.isfile(file_path):
            _, file_ext = os.path.splitext(file_path)
            if any(file_ext == x for x in self.unsupported_ext["animated"]):
                print(f"{file_ext} is not currently supported")
                return None
        return Image.open(file_path).convert("RGB").resize((512, 512))

    def dump_pickle(self, result_from_inference: list[tuple[np.ndarray, dict]], output_path: str):
        from pickle import dump
        file = open(output_path, 'wb')
        dump(result_from_inference, file)
        file.close()
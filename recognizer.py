from PIL import Image
import numpy as np
import torch
import TorchDeepDanbooru.deep_danbooru_model as deep_danbooru_model
from torch.amp.autocast_mode import autocast
import os
from typing import Optional
import json
import time
from util import check_file
import imageio.v3 as iio
import cv2

from tqdm import tqdm
import subprocess

def get_video_info(video_path: str):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info = json.loads(result.stdout)
    duration_str = info['streams'][0]['tags']['DURATION']
    hours, minutes, seconds = map(float, duration_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    fps = eval(info['streams'][0]['avg_frame_rate'])
    return total_seconds, fps

model_path = "model\\DeepDanbooru\\model-resnet_custom_v3.pt"


def set_device():
    if torch.cuda.is_available():
        print("CUDA IS AVAILABLE. GPU MODE")
        return "cuda"
    else:
        print("CUDA NOT AVAILABLE. CPU MODE")
        return "cpu"


        
class danbooru_recognizer:
    """Class for recognizing and dumping DeepDanbooru embedding
    
    Usage:
        ```
        recognizer = danbooru_recognizer()
        recognizer.load()
        res = danbooru.inference_gpu([])
        recognizer.dump_pickle(res, 'test.pickle')
        ```
    """
    def __init__(self, model_path: Optional[str] = None,
                 general_thres=0.9, char_thres=0.5,
                 config_path: Optional[str] = None) -> None:
        """

        Args:
            model_path (Optional[str], optional): Defaults to `model\\DeepDanbooru\\model-resnet_custom_v3.pt`.
            general_thres (float, optional): Threshold for general tags (index 0-6890). Defaults to 0.9 (90% confidence).
            char_thres (float, optional): Threshold for character tags (index 6891-9172). Defaults to 0.5 (50% confidence).
            config_path (Optional[str], optional): Defaults to `model\\DeepDanbooru\\categories.json`.
        """
        self.model = deep_danbooru_model.DeepDanbooruModel()
        self.device = set_device()
        
        if model_path is None:
            model_path = "model\\DeepDanbooru\\model-resnet_custom_v3.pt"
            assert os.path.isfile(model_path), "Model file not found"
            
        self.model_path = model_path
        self.general_thres = general_thres
        self.char_thres = char_thres
        self.video_ext = ("webm", "mp4", "mov")
        
        self.unsupported_ext = {
            "blacklist": ("part")
        }
        self.encoding = "utf8"
        
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
                   
    def preprocess_image(self, image: Image.Image, size: tuple[int, int]) -> Image.Image:
        return image.convert("RGB").resize(size)
    
    def image_to_array(self, image: Image.Image) -> np.ndarray:
        return np.expand_dims(np.array(image, dtype=np.float32), 0) / 255
    
    def array_to_tensor(self, array: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(array).cuda()
        
    def image_to_tensor(self, image: Image.Image) -> torch.Tensor:
        image = self.preprocess_image(image, (512, 512))
        img_to_array = self.image_to_array(image)
        array_to_tensor = self.array_to_tensor(img_to_array)
        return array_to_tensor
            
    def extract_frames_iio(self, video_path: str, n=5, duration=None, fps=None) -> list[torch.Tensor]:
        if duration is None or fps is None:
            duration, fps = get_video_info(video_path)
        frames = []
        for i in tqdm(range(n), desc=f'IIO: Reading frames from {os.path.basename(video_path)}'):
            t = (i+1) * duration / (n+1)
            frame_idx = int(t * fps)
            frame = iio.imread(video_path, index=frame_idx)
            frame = Image.fromarray(frame)
            frame = self.image_to_tensor(frame)
            frames.append(frame)
        return frames
        
    def extract_frames(self, video_path: str, n=5) -> list[torch.Tensor]:
        duration, fps = get_video_info(video_path)
        cap = cv2.VideoCapture(video_path)
        frames = []
        for i in tqdm(range(n), desc=f'CV2: Reading frames from {os.path.basename(video_path)}'):
            t = (i + 1) * duration / (n + 1)
            frame_idx = int(t * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (512, 512))
                frame = np.expand_dims(frame.astype(np.float32), 0) / 255
                frames.append(frame)
            else:
                print(f"CV2 Error. {duration=}, {fps=}  Switching to ImageIO-ffmpeg")
                break

        cap.release()
        if frames:
            frames = self.arrays_to_tensors(frames)
            return frames
        return self.extract_frames_iio(video_path, duration=duration, fps=fps)
        
    
    def extract_frames_gif(self, gif_path: str, n=5) -> list[torch.Tensor]:
        frames = []
        with Image.open(gif_path) as im:
            for i in tqdm(range(n), desc=f'PIL: Reading frames from {os.path.basename(gif_path)}'):
                im.seek(im.n_frames // n * i)
                frame = self.image_to_tensor(im)
                frames.append(frame)
        return frames
    
    def _predict(self, tensor: torch.Tensor) -> np.ndarray:
        result = self.model(tensor)[0].detach().cpu().numpy()
        return result
    
    def arrays_to_tensors(self, arrays: list[np.ndarray]) -> list[torch.Tensor]:
        tensors = [torch.from_numpy(array).cuda() for array in arrays]
        return tensors
        
    def _predict_multi_avg(self, tensors: list[torch.Tensor]) -> np.ndarray:
        results = [self._predict(tensor) for tensor in tensors]
        result = np.mean(results, axis=0)
        return result
    
    def inference_gpu(self, file_paths: list[str],
                      verbose=True, output_dump="output_dump_danbooru.txt"
                      ) -> list[tuple[np.ndarray, dict]]:
        """Danbooru tags from list of image paths

        Returns:
            list[tuple[np.ndarray, dict]]: list of pairs of
            
                result [result np array of probability of each tag]
                
                result_dict [{Filepath, Character (tags), General (tags), Rating}]
        """
        st = time.time()
        res = []
        i = 0
        output_dump_file = None
        if output_dump:
            if os.path.isfile(output_dump) and check_file(output_dump):
                open(output_dump, 'w').close()
            output_dump_file = open(output_dump, "a", encoding=self.encoding)
            
        with torch.no_grad(), autocast(self.device):
            print(f"Processing {len(file_paths)} files")
            for i, file_path in enumerate(file_paths):
                print(file_path)
                if os.path.exists(file_path):
                    if file_path.endswith("gif"):
                        image_arrays = self.extract_frames_gif(file_path)
                        result = self._predict_multi_avg(image_arrays)
                    elif any(file_path.endswith(ext) for ext in self.video_ext): 
                        image_arrays = self.extract_frames(file_path)
                        result = self._predict_multi_avg(image_arrays)
                            
                    else:
                        image_tensor = self.image_to_tensor(Image.open(file_path))
                        result = self._predict(image_tensor)

                    res_dict = self.parse_result_to_dict(result, file_path)
                    res.append((result, res_dict))
                    
                    if verbose:
                        print(f"{i:<3}| {res_dict}")
                    
                    if output_dump_file:
                        output_dump_file.write(f"{i:<3}| {res_dict}\n")
                        output_dump_file.flush()
                                 
            print(f"{len(file_paths)} images done in {time.time() - st:.2f}s")
            
        if output_dump_file is not None:
            output_dump_file.close()
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
                    
    def dump_pickle(self, result_from_inference: list[tuple[np.ndarray, dict]], output_path: str):
        from pickle import dump
        file = open(output_path, 'wb')
        dump(result_from_inference, file)
        file.close()
        
    
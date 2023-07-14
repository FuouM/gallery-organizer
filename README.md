# gallery-organizer
Organize massive amount of untagged randomly-named images (Experiment)

## The process
1. Separate files by their file name 
    - Sometimes, we want to keep the file name because they contain meaning created by the poster that may not be in the content of the image
    - We would like to preserve those "manually-named" files and only tag "unamed" files, such as timestamp or hash
    - High entropy --> Low entropy

2. Use AI to tag images
    * DeepDanbooru (We are here)
        - Anime vs Non-Anime images (Anime only currently)
        - Characters and Series they belong to

    * ~~OCR~~
    ~~Text content~~ OCR is slow and not very useful

    * LLM and Visual LLM
        - Semantic

3. Organize them in a tag-based and/or vectorized database
    - Similar to Hydrus
    - DeepDanbooru?

4. Deduplication
    - Image hash (fast, doesn't work for resolution/quality difference)
    - Comparison (slow)
    - AI?

### Set up environment 
```
# Python<3.11 - Important
conda create -n "gallery-organizer" python<3.11
conda activate gallery-organizer
python -m venv venv
```

### Activate venv
```
venv\Scripts\activate
```

### Libraries used
You must have ffmpeg/ffprobe installed to PATH to process animated files

```
# Important, else you'll get syscheckinterval error
pip install --upgrade tqdm 

pip install git+https://github.com/casics/nostril.git
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip install imageio-ffmpeg
pip install opencv-python

# Optional (for now)
pip install matplotlib
```

### Repositories used
```
git clone https://github.com/AUTOMATIC1111/TorchDeepDanbooru.git
```

### Models used
Place in model/DeepDanbooru folder
```
https://github.com/AUTOMATIC1111/TorchDeepDanbooru/releases/download/v1/model-resnet_custom_v3.pt 
```

### Bench mark
1050ti 4GB VRAM, 32GB RAM, Ryzen 5 1600, Windows 10
- DeepDanbooru tagging:
    - 7959 images       done in 1431.48s (Pickle size: 131  MB)
    - 502 gif/videos    done in 432.40s  (Pickle size: 8.86 MB)
    - 
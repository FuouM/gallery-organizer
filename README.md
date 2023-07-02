# gallery-organizer
Organize massive amount of untagged randomly-named images (Experiment)

## The process
1. Separate files by their file name (We are here)
    - Sometimes, we want to keep the file name because they contain meaning created by the poster that may not be in the content of the image
    - We would like to preserve those "manually-named" files and only tag "unamed" files, such as timestamp or hash
    - High entropy --> Low entropy

2. Use AI to tag images
    * DeepDanbooru
        - Anime vs Non-Anime images
        - Characters and Series they belong to
    * OCR
        - Text content 
    * LLM and Visual LLM
        - Semantic

3. Organize them in a tag-based and/or vectorized database
    - Similar to Hydrus
    - DeepDanbooru?

4. Deduplication
    - Image hash (fast, doesn't work for resolution/quality difference)
    - Comparison (slow)
    - AI?

### Activate venv
```
.venv\Scripts\activate
```

### Libraries used
```
pip install git+https://github.com/casics/nostril.git
```

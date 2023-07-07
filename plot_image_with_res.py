import pickle
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
dump_pickle_path = 'public_test.pickle'
# for result, res_dict in res:
#     print(res_dict, result)
# danbooru.dump_pickle(res, dump_pickle_path)
with open(dump_pickle_path, "rb") as f:
    unpickled = pickle.load(f)

with open("model\\DeepDanbooru\\tags.txt", "r") as tag_file:
    tags = np.array([x.strip() for x in tag_file.readlines()])


def res_to_plot(result: tuple[np.ndarray, dict], prob_thres=0.5):
    result_array, result_dict = result
    img = Image.open(result_dict["Filepath"])
    width, height = img.size
    new_width = 300
    new_height = int(new_width * height / width)
    img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)

    mask = result_array > prob_thres
    filtered_tags = tags[mask]
    filtered_result_array = result_array[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2.5, 1]}, figsize=(12,4))
    ax1.bar(filtered_tags, filtered_result_array)
    plt.setp(ax1.get_xticklabels(), rotation=90)
    
    label_font_size = min(12, 500 // len(filtered_tags) - 1)
    ax1.tick_params(axis='x', labelsize=label_font_size)

    ax2.imshow(img)
    ax2.axis('off')
    
    # Add label to the image
    label_text = f"{os.path.basename(result_dict['Filepath'])}\n{result_dict['Character']}"
    ax2.text(0.5, -0.2, label_text, size=10, ha="center", transform=ax2.transAxes)
    
    plt.tight_layout()
    
    # Save the figure with a high DPI
    plt.savefig(f'plot/plot_{os.path.basename(result_dict["Filepath"]).split(".")[0]}.png', dpi=500)
    
    plt.show()
    

first_item = unpickled[0]
print(first_item)

res_to_plot(first_item, 0.5)
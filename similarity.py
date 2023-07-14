import pickle
import time
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


dump_pickle_path = 'public_test.pickle'
with open(dump_pickle_path, "rb") as f:
    unpickled = pickle.load(f)
    


def euclidean_distance(a, b):
    return np.linalg.norm(a-b)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_filename(file_path):
    return os.path.basename(file_path).split(".")[0]

first_item = unpickled[0]
second_item = unpickled[1]
def run(function, reverse=False):
    st = time.time()
    res_dict = dict()
    most_list = list()
    i = 0
    for first in unpickled:
        first_name = first[1]["Filepath"]
        res_dict[first_name] = []
        for second in unpickled:
            second_name = second[1]["Filepath"]
            if first_name == second_name:
                continue
            # print(f'{first_name:40} {second_name:30}|', end="\t")
            distance = function(first[0], second[0])
            res_dict[first_name].append((second_name, distance))
        sorted_lst = sorted(res_dict[first_name], key=lambda x: x[1],reverse=reverse)
        # print(res_dict[first_name])
        print(f"{i}.\tMost similar with {first_name}: {sorted_lst[0]}")
        most_list.append((first_name, sorted_lst[0][0], sorted_lst[0][1]))
        i += 1
    print(f"{function.__name__}. Time taken: {time.time() - st} s")
    return res_dict, most_list


def create_collage(image_a_path, image_b_path, text):
    # Open the images
    image_a = Image.open(image_a_path)
    image_b = Image.open(image_b_path)

    # Set the output image dimensions
    output_height = image_a.height
    output_width = 2 * image_a.width

    # Calculate the new dimensions for image_a
    a_width = int(output_width / 2)
    a_height = int(a_width * (image_a.height / image_a.width))

    # Resize image_a to fit in the left half of the output image
    # image_a = image_a.resize((a_width, a_height), Image.ANTIALIAS)

    # Calculate the new dimensions for image_b
    b_width = int(output_width / 2)
    b_height = int(b_width * (image_b.height / image_b.width))

    # Resize image_b to fit in the right half of the output image
    image_b = image_b.resize((b_width, b_height), Image.ANTIALIAS)

    # Create a new blank image for the output
    output_image = Image.new('RGB', (output_width, output_height))

    # Paste the images into the output image
    output_image.paste(image_a, (int(output_width / 4 - a_width / 2), int((output_height - a_height) / 2)))
    output_image.paste(image_b, (int(3 * output_width / 4 - b_width / 2), int((output_height - b_height) / 2)))

    # Add text box on bottom right corner
    
    font = ImageFont.truetype('arial.ttf', size=b_width//20)
    
    draw = ImageDraw.Draw(output_image)
    # font = ImageFont.load_default()
    text_size = draw.textsize(text, font=font)
    text_position = (output_width - text_size[0], output_height - text_size[1])
    draw.text(text_position, text, font=font)
    
    # Save the output image
    output_image.save('output.jpg')
        
# create_image_table(most_list)
res_dict, most_list = run(cosine_similarity, True)
index = 9
create_collage(most_list[index][0], most_list[index][1], f"Distance: {most_list[index][2]}")

# euclid np: 0.07001543045043945 s
# cosine np: 0.0870511531829834 s

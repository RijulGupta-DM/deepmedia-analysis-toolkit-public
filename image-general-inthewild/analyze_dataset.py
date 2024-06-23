# import os
# import glob
# import re
# import pandas as pd
# import plotly.express as px
# from pathlib import Path
# import random

# # Define the base directory
# input_dataset = "deepmedia-datasets-public/image-general-inthewild/240623"

# info_file = os.path.join(input_dataset, "image_info.txt")

# # Load the info_file
# # It looks like this
# # 0a2eb8300609,1
# # 0a06da6932ee,0
# # 0a7a77df9d9c,1
# # 00a8e5f1e79f,1

# For each line, get the uuid value and the real fake value. Load these into a dictionary.

# Get every image file at this location
# image_dir = os.path.join(input_dataset, "media")

# Loop through all the Images
# Get the UUID of the image which is the basename without the extension
# Get the real/fake value from the dictionary
# Get the CLIP location which can be found by replacing the image_dir with the clip_dir and replacing the extension with json
# Count the overall number of real and fake images
# Create the pie chart

# Example code used to create the dataset

#     # Main processing
#     export_dir = "datasets/dm-goldensets-nonfaceimages-fakedetect/assets/public-export"
#     dataset_dir = "deepmedia-datasets-public/image-general-inthewild/240623/"
#     full_dataset_dir = os.path.join(export_dir, dataset_dir)
#     images_dir = "media/images/"
#     clip_dir = "metadata/embeddings/clip_B32"

#     # Ensure directories exist
#     full_images_dir = os.path.join(export_dir, dataset_dir, images_dir)
#     os.makedirs(os.path.join(export_dir, dataset_dir, images_dir), exist_ok=True)
#     os.makedirs(os.path.join(export_dir, dataset_dir, clip_dir), exist_ok=True)

#     # Create a text file to store image information
#     info_file_path = os.path.join(export_dir, dataset_dir, "image_info.txt")
#     real_count = 0
#     fake_count = 0

#     results = {}

#     for image_obj in test_inferenceresults:

#         original_image_path = image_obj.non_face_image.image_path
#         image_is_manipulated = image_obj.non_face_image.is_manipulated
#         original_clip_path = image_obj.clip_json_path
#         image_ext = os.path.splitext(original_image_path)[1]
        
#         image_uuid = create_uuid_from_string(image_obj.non_face_image.image_path)
#         new_image_basename = image_uuid + image_ext
#         new_clip_basename = image_uuid + ".json"

#         new_image_path = os.path.join(export_dir, dataset_dir, images_dir, new_image_basename)
#         new_clip_path = os.path.join(export_dir, dataset_dir, clip_dir, new_clip_basename)

#         # Copy files
#         shutil.copy2(original_image_path, new_image_path)
#         shutil.copy2(original_clip_path, new_clip_path)

#         results[new_image_basename] = 1 if image_is_manipulated else 0

#         # Count real and fake images
#         if image_is_manipulated:
#             fake_count += 1
#         else:
#             real_count += 1


#     # Get the list of files in the directory and sort them
#     file_list = sorted(os.listdir(full_images_dir), key=natural_sort_key)

#     # Write results to the text file in the order of files in the directory
#     with open(info_file_path, 'w') as info_file:
#         for filename in file_list:
#             basename, _ = os.path.splitext(filename)
#             info_file.write(f"{basename},{results[filename]}\n")

#     # Create and save pie chart
#     create_pie_chart(real_count, fake_count, full_dataset_dir, "real_fake_distribution.png")

#     print(f"Exported {real_count + fake_count} images.")
#     print(f"Real images: {real_count}")
#     print(f"Fake images: {fake_count}")
#     print(f"Image information saved to: {info_file_path}")
#     print(f"Pie chart saved to: {os.path.join(full_dataset_dir, 'real_fake_distribution.png')}")

import os
import glob
import re
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import json

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def create_pie_chart(real_count, fake_count, output_directory, output_filename):
    total_samples = real_count + fake_count
    labels = ['Real', 'Fake']
    values = [real_count, fake_count]
    colors = ['#3498db', '#e74c3c']  # Blue for Real, Red for Fake

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent+value',
        textposition='outside',
        textfont=dict(size=16, color='white'),
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        pull=[0.05, 0.05],
        direction='clockwise',
        sort=False
    )])

    fig.update_layout(
        title=dict(
            text='Distribution of Images',
            font=dict(size=28, color='white'),
            x=0.5,
            y=0.98
        ),
        paper_bgcolor='rgba(0,0,0,0.8)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(size=18, color='white'),
            orientation='h',
            yanchor='bottom',
            y=0.9,
            xanchor='center',
            x=0.5
        ),
        annotations=[
            dict(
                text=f'Total Samples: {total_samples}',
                x=0.5,
                y=-0.15,
                showarrow=False,
                font=dict(size=20, color='white'),
                xref='paper',
                yref='paper'
            )
        ],
        margin=dict(t=100, b=100, l=40, r=40),
        width=900,
        height=700
    )

    fig.write_image(os.path.join(output_directory, output_filename), scale=2)
    print(f"Pie chart saved to: {os.path.join(output_directory, output_filename)}")

# Define the base directory
input_dataset = "deepmedia-datasets-public/image-general-inthewild/240623"

info_file = os.path.join(input_dataset, "image_info.txt")

# Load the info_file into a dictionary
image_info = {}
with open(info_file, 'r') as f:
    for line in f:
        uuid, is_fake = line.strip().split(',')
        image_info[uuid] = int(is_fake)

# Get image files
image_dir = os.path.join(input_dataset, "media", "images")
clip_dir = os.path.join(input_dataset, "metadata", "embeddings", "clip_B32")

image_files = sorted(glob.glob(os.path.join(image_dir, "*.*")), key=natural_sort_key)

dataset = []
real_count = 0
fake_count = 0

# Process each image
for image_path in image_files:
    image_uuid = Path(image_path).stem
    is_fake = image_info.get(image_uuid, None)
    
    if is_fake is None:
        print(f"Warning: No information found for image {image_uuid}")
        continue
    
    clip_path = os.path.join(clip_dir, f"{image_uuid}.json")
    
    if not os.path.exists(clip_path):
        print(f"Warning: CLIP embedding not found for image {image_uuid}")
        continue
    
    # Load CLIP embedding
    with open(clip_path, 'r') as f:
        clip_embedding = json.load(f)
    
    dataset.append({
        'uuid': image_uuid,
        'image_path': image_path,
        'clip_path': clip_path,
        'is_fake': is_fake,
        'clip_embedding': clip_embedding
    })
    
    if is_fake:
        fake_count += 1
    else:
        real_count += 1

# Convert to DataFrame
df = pd.DataFrame(dataset)

print(f"Total images processed: {len(df)}")
print(f"Real images: {real_count}")
print(f"Fake images: {fake_count}")

# Create and save pie chart
create_pie_chart(real_count, fake_count, "./", "real_fake_distribution_verification.png")

# Sample usage of the dataset
print("\nSample of 5 random images from the dataset:")
print(df[['uuid', 'image_path', 'is_fake']].sample(5))

print("\nVerification complete. If the pie chart matches the original and the counts are correct, the dataset is loaded successfully!")
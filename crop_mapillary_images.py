import glob, sys, os
import argparse
import pandas as pd
from PIL import ImageFile, Image
import numpy as np
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Cropping street-level images')
    parser.add_argument('--images_path', type=str,
                        help='path for images to crop', default='images/')
    parser.add_argument('--res_path', type=str, help='path where to store the cropped images',
                        default='cropped_images/')
    parser.add_argument('-f', '--info_file', type=str,
                        help='.csv file that matches street-level images with LPIS', default='Mapillary_annotated.csv')
    parser.add_argument('-N', '--target_size', dest='target_size', type=int, help='size to crop images', default=260)
    args, _ = parser.parse_known_args()

    return args

def main(images_path, result_path, info_file, IMG_SIZE):

    if not os.path.exists(images_path):
        print('{} does not exists (in argument --image_path)'.format(iamge_path)) 
    files = glob.glob(os.path.join(images_path, "*"))
    mapillary = pd.read_csv(info_file)
    image_ids = [int(x.split("/")[-1].split(".")[0]) for x in files]
    mapillary = mapillary[mapillary.image_id.isin(image_ids)].copy()
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    if not os.path.exists(result_path):
        os.mkdir(result_path)
        os.mkdir(os.path.join(result_path, 'Grassland'))
        os.mkdir(os.path.join(result_path, 'Non_Grassland'))
    for i,row in tqdm(list(mapillary.iterrows())):
        image_path = '{}/{}_{}.jpg'.format(row.label, row.image_id, row.direction)
        try:
            img = Image.open('{}{}.jpg'.format(images_path,row.image_id))
        except:
            print("Image with id {} is corrupted! ".format(row.image_id))
        h, w, _ = np.asarray(img).shape
        if row.direction == 'left':
            img = img.crop((0, int(h*0.5), int(w*0.3), int(h*0.8)))
        elif row.direction == 'right':
            img = img.crop((int(w*0.7), int(h*0.5), w, int(h*0.8)))
        img = img.resize((IMG_SIZE,IMG_SIZE), Image.ANTIALIAS)
        save_path = result_path + image_path
        img.save(save_path, 'JPEG', quality=90)

if __name__ == "__main__":

    args = parse_args()
    main(args.images_path, args.res_path, args.info_file, args.target_size)

import os
import sys
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--baseDir", help="directory in which all your network will live", default='models')
parser.add_argument("--name", help="name of your network", default='N2V3D')
parser.add_argument("--dataPath", help="The path to your data")
parser.add_argument("--fileName", help="name of your data file", default="*.tif")
parser.add_argument("--output", help="The path to your data to be saved", default='predictions.tif')
parser.add_argument("--dims", help="dimensions of your data", default='YX')
parser.add_argument("--tile", help="will cut your image [TILE] times in every dimension to make it fit GPU memory", default=1, type=int)

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

assert (not 'T' in args.dims) or (args.dims[0]=='T')

# We import all our dependencies.
from n2v.models import N2V
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator
import numpy as np
from matplotlib import pyplot as plt
from tifffile import imread
from tifffile import imwrite


# A previously trained model is loaded by creating a new N2V-object without providing a 'config'.
model_name = args.name
basedir = args.baseDir
model = N2V(config=None, name=model_name, basedir=basedir)


tiles = (args.tile, args.tile)

if 'Z' in args.dims or 'C' in args.dims:
    tiles = (1, args.tile, args.tile)

if 'Z' in args.dims and 'C' in args.dims:
    tiles = (1, args.tile, args.tile, 1)

datagen = N2V_DataGenerator()
imgs = datagen.load_imgs_from_directory(directory = args.dataPath, dims=args.dims, filter=args.fileName)

for i, img in enumerate(imgs):
    print("img.shape",img.shape)

    if len(img.shape)>len(args.dims):
        img_=img[...,0]
    else:
        img_=img

    # if we have a time dimension we process the images one by one
    if args.dims[0]=='T':
        pred=img_.copy()
        myDims=args.dims[1:]	


        for j in range(img_.shape[0]):
            print("img_[j].shape", img_[j].shape)
            pred[j] = model.predict( img_[j], axes=myDims, n_tiles=tiles)
    else:

        print("denoising image "+str(i) +" of "+str(len(imgs)))
        # Denoise the image.
        pred = model.predict( img_, axes=args.dims, n_tiles=tiles)
    
    print(pred.shape)
    filename=args.output
    if len(imgs) > 1:
        filename=filename+'_'+str(i).zfill(4) +'.tif'
    imwrite(filename,pred.astype(np.float32))

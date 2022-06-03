import librosa
import librosa.display
from librosa.feature import *

import pandas as pd
import numpy as np
from datetime import datetime

import os
import pathlib
import csv
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt

extract = 'FEATURES'
#extract = 'IMAGES'
#extract = 'ALL'

##########################################################################################
# EXTRACT FEATURES FUNCTION
##########################################################################################
'''
def extract_features (x, sr):
    feat_dic={}
        
# Power Based total Means
    for func in [rms, chroma_stft, spectral_centroid, spectral_bandwidth, spectral_rolloff, zero_crossing_rate]:
        feat_name=str(func).split()[1]
        feature = np.mean(func(y=x))
        feat_dic[f'{feat_name}_mean']=feature
        
# Power Based Multiple Means
    for func in [ mfcc]:
        feat_lst = np.mean(func(y=x, sr=sr), axis=1)

        feat_name=str(func).split()[1]

        for num, feature in enumerate(feat_lst):
            feat_dic[f'{feat_name}_{num}']=feature
# Energy Based:
    for func in [spectral_contrast ]:

        feat_lst = np.mean(func(S=np.abs(librosa.stft(x)), sr=sr), axis=1)
        feat_name=str(func).split()[1]
        for num, feature in enumerate(feat_lst):
            feat_dic[f'{feat_name}_{num}']=feature
    return feat_dic

def extract_features (x, sr):
    feat_dic={}
    x_harm, x_perc = librosa.effects.hpss(x)
'''

def extract_features (x, sr):
    feat_dic={}
    x_harm, x_perc = librosa.effects.hpss(x)

# Power Based total Means
    for num, series in enumerate([x, x_harm, x_perc]):
        label={0:'full',1:'harm',2:'perc'}
        for func in [rms, chroma_stft, spectral_centroid, spectral_bandwidth, spectral_rolloff, zero_crossing_rate]:
            feat_name=str(func).split()[1]
            if func == rms:
                s=librosa.stft(series)
                S, phase = librosa.magphase(s)
                feature = np.mean(func(S=S))
            else:
                feature = np.mean(func(y=series))
            feat_dic[f'{feat_name}_{label[num]}_mean']=feature

# Power Based Multiple Means
    for func in [ mfcc]:
        feat_lst = np.mean(func(y=x, sr=sr), axis=1)

        feat_name=str(func).split()[1]

        for num, feature in enumerate(feat_lst):
            feat_dic[f'{feat_name}_{num}']=feature
# Energy Based:
    for func in [spectral_contrast ]:
        s=librosa.stft(x)
        feat_lst = np.mean(func(S=np.abs(s), sr=sr), axis=1)
        feat_name=str(func).split()[1]
        for num, feature in enumerate(feat_lst):
            feat_dic[f'{feat_name}_{num}']=feature
    return feat_dic


##########################################################################################
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

##########################################################################################

music_dir='../music_data/preprocessed'
image_dir='../image_data/spectrograms_6sec'
csv_file='../features/features_6sec_14genres.csv'

#mkdir(image_dir)
#mkdir(music_dir)

##########################################################################################
# Genres
##########################################################################################

for base,(dirpath, dirnames, filenames) in enumerate(os.walk(music_dir)):
    if base == 0:
        genres=dirnames

plt.figure(figsize=(8,8))


##########################################################################################

sr = 22050
total_samples = 30 * sr
num_slices = 5 
samples_per_slice = int(total_samples / num_slices)


##########################################################################################
# Main Loop
##########################################################################################
temp_csv='temp1.csv'
with open(temp_csv, 'w') as f:
    pass

track_time=datetime.now()

feat_data_lst=[]

for genre in genres:
    genre_path=music_dir +'/'+genre
    image_path=image_dir+'/' + genre
    mkdir(image_path)
    for num,(dirpath, dirnames, filenames) in enumerate(os.walk(genre_path)):
        for filename in tqdm(filenames): 
            song_file=genre_path + '/' + filename
            file_base=filename.split('.')[0]

            y, sr = librosa.load(song_file, mono=True, duration=30)

            for chunk in range(num_slices):
                start=chunk*samples_per_slice
                end=start+samples_per_slice
                ch=y[start:end]
                sample_name=file_base + '-' + str(start) + '.wav'
                image_chunk_name = image_path+ '/' + file_base + '-'+ str(chunk) + '.png'

                if extract in ['IMAGES','ALL']:
                    generate_image(ch,image_chunk_name)
                
                if extract in ['FEATURES','ALL']:
                   feat_dic=extract_features(ch , sr)
                    
                   feat_dic["file_name"]=sample_name
                   feat_dic["genre"]=genre

                   feat_data_lst.append(feat_dic)
                   
                   if (len(feat_data_lst) % 50 == 0):
                       pd.DataFrame(feat_data_lst).to_csv(temp_csv, mode='a', index=False, header=False)
                       feat_data_lst=[]

if extract in ['FEATURES','ALL']:           
    # appending the remainer of raws (less than 50) 
    pd.DataFrame(feat_data_lst).to_csv(temp_csv, mode='a', index=False, header=False)

    df=pd.read_csv(temp_csv, header=None)
    df.columns=list(feat_dic.keys())
    df.to_csv(csv_file, mode='w', index=False)
os.remove(temp_csv)

print('---------------------------------')
print(datetime.now()-track_time)
print('---------------------------------')


import pandas as pd
import numpy as np
import math
import torch
from tqdm import tqdm
import matplotlib.pyplot as plt

# сюда вставить таблицу из postgres
coords = pd.read_csv('/home/kamil/proga/digitdep_hack/geodata/buyer.csv')
coords['lat'] = pd.to_numeric(coords.geo.apply(lambda x: str(x).split(',')[0]), errors='coerce')
coords['lon'] = pd.to_numeric(coords.geo.apply(lambda x: str(x).split(',')[1] if len(str(x).split(',')) > 1 else np.nan), errors='coerce')
coords.dropna(inplace=True)

def dist(a, b):
    R = 6371.0
    a = torch.deg2rad(a)
    b = torch.deg2rad(b)
    dlat = (b - a)[:, 0]
    dlon = (b - a)[:, 1]
    if a.dim() == 1:
        a1 = torch.sin(dlat / 2)**2 + torch.cos(a[0]) * torch.cos(b[:, 0]) * torch.sin(dlon / 2)**2
    else:
        a1 = torch.sin(dlat / 2)**2 + torch.cos(a[:, 0]) * torch.cos(b[0]) * torch.sin(dlon / 2)**2
    c = 2 * torch.atan2(torch.sqrt(a1), torch.sqrt(1 - a1))
    distance = R * c
    return distance

def get_neighbours(data, dist_func, point, eps):
    dist = dist_func(data, point)
    return torch.nonzero(dist <= eps).flatten()

def expand(data, dist_func, i, c, eps, min_pts, labels, neighbours):
    labels[i] = c
    k = 0

    while k < len(neighbours):
        if labels[neighbours[k]] != -1:
            k += 1
            continue
        labels[neighbours[k]] = c
        n_k = get_neighbours(data, dist_func, data[neighbours[k]], eps)
        if len(n_k) >= min_pts:
            neighbours = torch.unique(torch.cat((neighbours, n_k)))
        k += 1 

def dbscan(data, dist_func, eps, min_pts):
    c = 0
    labels = torch.full((data.shape[0],), -1)
    for i in tqdm(range(data.shape[0])):
        if labels[i] != -1:
            continue # already visited
        neighbours = get_neighbours(data, dist_func, data[i], eps)
        if len(neighbours) < min_pts:
            labels[i] = -2 # label the point as noise
            continue
        c += 1
        expand(data, dist_func, i, c, eps, min_pts, labels, neighbours)
    return labels   
                

X = torch.tensor(coords[['lat', 'lon']].values, dtype=torch.int32)
labels = dbscan(X, dist, 1200, 3)
Q = np.vstack((np.array(X)[:, 0], np.array(X)[:, 1], np.array(labels))).swapaxes(0, 1)
lab = np.array(labels)
unique, counts = np.unique(lab, return_counts=True)
labels_dict = dict(zip(unique, counts))
labels_dict
coords['label'] = labels
second_stage = coords[coords.label== max(labels_dict, key=labels_dict.get)]
second_x = torch.tensor(second_stage[['lat', 'lon']].values, dtype=torch.int32)
second_labels = dbscan(second_x, dist, 250, 30)
second_Q = np.vstack((np.array(second_x)[:, 0], np.array(second_x)[:, 1], np.array(second_labels))).swapaxes(0, 1)
second_lab = np.array(second_labels)
second_unique, second_counts = np.unique(second_lab, return_counts=True)
dict(zip(second_unique, second_counts))

second_stage['label'] = second_labels
second_stage.head()

third_stage = second_stage[second_stage.label == min(second_stage.label)]
third_x = torch.tensor(third_stage[['lat', 'lon']].values, dtype=torch.int32)
third_labels = dbscan(third_x, dist, 700, 5)
third_Q = np.vstack((np.array(third_x)[:, 0], np.array(third_x)[:, 1], np.array(third_labels))).swapaxes(0, 1)
third_lab = np.array(third_labels)
third_unique, third_counts = np.unique(third_lab, return_counts=True)
dict(zip(third_unique, third_counts))
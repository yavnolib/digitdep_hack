import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

import sys

# sys.path.append("/mnt")


from src.db_iface import PostgreIface


class GeoClassificator:
    def __init__(self, use_postgre=True):
        """
        Initiates DataFrame with coordinates

        Args:
            csv_path: path to csv with coordinates.
        """
        self.use_postgre = use_postgre
        if self.use_postgre:
            self.postgre = PostgreIface()

    def fetch_known_buyer(self):
        """Read `buyer` database"""
        if self.use_postgre:
            known = self.postgre.read_table("buyer")
            known.code = known.code.astype(int)
        else:
            known = pd.read_csv('cache/buyer.csv')
        return known

    @staticmethod
    def dist(a: np.ndarray, b: np.ndarray):
        """
        Counts distances between points

        Arguments:
            a: first point. Could be multidimensional.
            b: second point. Could be multidimensional.

        Returns:
            distance: distance to points
        """
        R = 6371.0

        a = np.deg2rad(a)
        b = np.deg2rad(b)

        # Если входные данные одномерные, приводим их к двумерной форме
        if a.ndim == 1:
            a = a[np.newaxis, :]
        if b.ndim == 1:
            b = b[np.newaxis, :]

        dlat = b[:, 0] - a[:, 0]
        dlon = b[:, 1] - a[:, 1]

        a1 = (
            np.sin(dlat / 2) ** 2
            + np.cos(a[:, 0]) * np.cos(b[:, 0]) * np.sin(dlon / 2) ** 2
        )
        c = 2 * np.arctan2(np.sqrt(a1), np.sqrt(1 - a1))

        distance = R * c
        return distance

    @staticmethod
    def get_neighbours(
        data: np.ndarray, dist_func, point: np.ndarray, eps: int
    ):
        """
        Finds all neighbours

        Arguments:
            data: points ndarray.
            dist_func: function to count distance.
            point: point ndarray.
            eps: neighbourhood

        Returns:
            neighbour points

        """
        dist = dist_func(data, point)
        return np.where(dist <= eps)[0]

    @staticmethod
    def expand(
        data: np.ndarray,
        dist_func,
        i: int,
        c: int,
        eps: int,
        min_pts: int,
        labels: np.ndarray,
        neighbours: np.ndarray,
    ):
        """
        Expands results of dbscan

        Arguments:

        """
        labels[i] = c

        k = 0
        while k < len(neighbours):
            if labels[neighbours[k]] != -1:
                k += 1
                continue
            labels[neighbours[k]] = c
            n_k = GeoClassificator.get_neighbours(
                data, dist_func, data[neighbours[k]], eps
            )
            if len(n_k) >= min_pts:
                neighbours = np.unique(np.concatenate((neighbours, n_k)))

            k += 1

    @staticmethod
    def dbscan(data: np.ndarray, dist_func, eps: int, min_pts: int):
        c = 0
        labels = np.full(data.shape[0], -1)
        for i in tqdm(range(data.shape[0])):
            if labels[i] != -1:
                continue
            neighbours = GeoClassificator.get_neighbours(
                data, dist_func, data[i], eps
            )
            if len(neighbours) < min_pts:
                labels[i] = -2
                continue

            c += 1
            GeoClassificator.expand(
                data, dist_func, i, c, eps, min_pts, labels, neighbours
            )
        return labels


    def fit(self):
        self.geo_inf = self.fetch_known_buyer()
        self.geo_inf["lat"] = pd.to_numeric(
            self.geo_inf.geo.apply(lambda x: str(x).split(",")[0]),
            errors="coerce",
        )
        self.geo_inf["lon"] = pd.to_numeric(
            self.geo_inf.geo.apply(
                lambda x: (
                    str(x).split(",")[1]
                    if len(str(x).split(",")) > 1
                    else np.nan
                )
            ),
            errors="coerce",
        )
        self.geo_inf["geo_cluster"] = np.where(
            self.geo_inf[["lat", "lon"]].isna().any(axis=1), -1, 0
        )
        X = self.geo_inf[self.geo_inf.geo_cluster != -1][["lat", "lon"]].values
        labels = self.dbscan(X, self.dist, 1200, 3)
        self.geo_inf.loc[self.geo_inf["geo_cluster"] != -1, "geo_cluster"] = (
            labels
        )

        unique_values, counts = np.unique(labels, return_counts=True)
        second_stage = self.geo_inf[
            self.geo_inf.geo_cluster == int(unique_values[np.argmax(counts)])
        ]
        second_x = second_stage[["lat", "lon"]].values
        second_labels = self.dbscan(second_x, self.dist, 310, 30)
        second_stage["geo_cluster"] = second_labels

        third_stage = second_stage[second_stage.geo_cluster == -2]
        third_x = third_stage[["lat", "lon"]].values
        third_labels = self.dbscan(third_x, self.dist, 700, 0)
        second_stage.loc[second_stage["geo_cluster"] == -2, "geo_cluster"] = (
            third_labels + second_stage.geo_cluster.max()
        )
        self.geo_inf.loc[
            self.geo_inf["geo_cluster"] == int(unique_values[np.argmax(counts)]),
            "geo_cluster",
        ] = (
            second_stage.geo_cluster + self.geo_inf.geo_cluster.max()
        )

    def save(self, path: str = "/mnt/geodata/buyer_coordinates.csv"):
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"An error occurred while creating the directory: {e}")

        self.fit()
        self.geo_inf.to_csv(path, index=False, encoding='UTF-8')

    def transform(
        self,
        data: pd.DataFrame,
        columns: tuple = ("Грузополучатель", ),
        path: str = "/mnt/geodata/buyer_coordinates.csv",
    ):
        """
        Возвращает датафрейм с лейблами:
            -1: NaNы
            -2: Слишком далекие точки
            >0: Метки класса
        """
        names = {"code": columns[0]}

        if not Path(path).is_file():
            self.save(path)
        coordinates = pd.read_csv(path)

        coordinates.rename(columns=names, inplace=True)

        merged_df = data.merge(
            coordinates[[columns[0], "geo_cluster"]], on=columns, how="left"
        ).fillna(-1.)
        return merged_df
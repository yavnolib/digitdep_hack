from copy import deepcopy

import numpy as np
import pandas as pd


class DeliveryTimeClassificator:
    def __init__(self, df, sprav, mtr, problem_data, max_dif=30):
        """
        Принимает на вход xlsx Загрузочного файла.
        Дополнительно инициализирует excel-таблицы с данными про МТР-кабели + нормативные сроки
        Получаем таблицу MTR при merge, которая содержат id товара MTR и его нормативные сроки поставки
        """
        self.drop_cols = ["level_0", "срок", "Проблемная заявка"]

        self.df = deepcopy(df)
        self.sprav = deepcopy(sprav)
        self.mtr = deepcopy(mtr)
        self.problem_data = problem_data
        self.dates = []
        self.max_dif = max_dif  # (30 days)

    def __str__(self):
        return f"time classificator for delivery dates"

    def preprocessing(self):
        self.time_clust_2 = np.zeros_like(self.df["Дата заказа"], dtype=int)
        self.df.reset_index(inplace=True)

    def fit(self):
        """
        Выполняем кластеризацию с ограничением на разницу в днях между датами доставки
        """
        n_apps = self.df.shape[0]
        n_cluster = 0

        for i in range(n_apps):
            delivery_date = self.df.iloc[i]["Срок поставки"]
            assigned = False
            cluster_index = 0

            # Пробуем добавить точку в существующие кластеры

            for j in range(n_cluster):
                # if на условие по времени доставки

                if self.max_date_dif(j, delivery_date) <= self.max_dif:
                    cluster_index = j
                    assigned = True
                    break

            if assigned:
                # добавляем в кластер по индексу
                self.time_clust_2[i] = cluster_index
                # self.clusters[cluster_index].append(application)

                # пересчитываем самую раннюю и самую позднюю даты доставки
                if self.dates[cluster_index][0] > delivery_date:
                    self.dates[cluster_index][0] = delivery_date
                elif self.dates[cluster_index][1] < delivery_date:
                    self.dates[cluster_index][1] = delivery_date

            # создаем новый кластер
            else:
                # self.clusters.append([application])
                self.time_clust_2[i] = n_cluster
                n_cluster += 1
                self.dates.append([delivery_date, delivery_date])
        self.df["time_cluster_2"] = self.time_clust_2

    def max_date_dif(self, date_index, delivery_date):
        """
        Вычисление наибольшей разницы между датами в возможном кластере
        """
        days_from_min = abs((delivery_date - self.dates[date_index][0]).days)
        days_from_max = abs((delivery_date - self.dates[date_index][1]).days)
        return max(days_from_max, days_from_min)

    def transform(self):
        """
        Возвращает DataFrame с колонкой time_cluster_2 - результатом кластеризации по дате ДОСТАВКИ
        """
        self.preprocessing()
        self.fit()

        exist_cols = self.df.columns.tolist()
        res = self.df
        problems = self.problem_data.reset_index()
        return (
            pd.concat([res, problems])
            .drop(columns=list(set(self.drop_cols) & set(exist_cols)))
            .sort_values("index")
            .set_index("index")
            .reset_index(drop=True)
        )

    def fit_2(self):
        """
        Выполняем кластеризацию с ограничением на разницу в днях между датами доставки
        """
        self.df["Срок поставки"] = pd.to_datetime(
            self.df["Срок поставки"]
        )  # Преобразуем в даты, если это еще не сделано
        delivery_dates = self.df["Срок поставки"].values
        n_apps = delivery_dates.shape[0]

        # Инициализация массива для кластеров
        self.time_clust_2 = -np.ones(
            n_apps, dtype=int
        )  # -1 для обозначения нераспределенных точек
        self.dates = []

        # Преобразуем max_dif в timedelta64 для корректного сравнения
        max_diff_timedelta = np.timedelta64(self.max_dif, "D")

        for i in range(n_apps):
            delivery_date = delivery_dates[i]

            # Если кластеры уже существуют, проверяем их
            if self.dates:
                min_dates = np.array([cluster[0] for cluster in self.dates])
                max_dates = np.array([cluster[1] for cluster in self.dates])

                # Вычисляем разницу для всех кластеров
                diffs_to_min = np.abs(delivery_date - min_dates)
                diffs_to_max = np.abs(delivery_date - max_dates)
                cluster_differences = np.maximum(diffs_to_min, diffs_to_max)

                # Ищем подходящие кластеры
                valid_clusters = np.where(cluster_differences <= max_diff_timedelta)[0]

                if valid_clusters.size > 0:
                    cluster_index = valid_clusters[0]
                    self.time_clust_2[i] = cluster_index

                    # Обновляем даты кластера
                    self.dates[cluster_index][0] = min(
                        self.dates[cluster_index][0], delivery_date
                    )
                    self.dates[cluster_index][1] = max(
                        self.dates[cluster_index][1], delivery_date
                    )
                else:
                    # Создаем новый кластер
                    cluster_index = len(self.dates)
                    self.time_clust_2[i] = cluster_index
                    self.dates.append(
                        [delivery_date, delivery_date]
                    )  # Начальная дата одного кластера - это дата самой первой заявки
            else:
                # Если кластеров нет, создаем первый кластер
                cluster_index = 0
                self.time_clust_2[i] = cluster_index
                self.dates.append(
                    [delivery_date, delivery_date]
                )  # Начальная дата одного кластера

        self.df["time_cluster_2"] = self.time_clust_2

    def transform_2(self):
        """
        Возвращает DataFrame с колонкой time_cluster_2 - результатом кластеризации по дате ДОСТАВКИ
        """
        self.preprocessing()
        self.fit_2()

        exist_cols = self.df.columns.tolist()
        res = self.df
        problems = self.problem_data.reset_index()
        return (
            pd.concat([res, problems])
            .drop(columns=list(set(self.drop_cols) & set(exist_cols)))
            .sort_values("index")
            .set_index("index")
            .reset_index(drop=True)
        )

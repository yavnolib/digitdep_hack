import numpy as np
import pandas as pd


class DeliveryTimeClassificator:
    def __init__(self, max_dif=30):
        """
        Инициализируем алгоритм с заданной макcимальной разницей между датами доставки
        """
        self.max_dif = max_dif  # (30 days)
        self.clusters = []
        self.dates = []

    def __str__(self):
        return f'time classificator for delivery dates'

    def fit(self, df):
        """
        Выполняем кластеризацию с ограничением на разницу в днях между датами доставки
        """
        n_apps = df.shape[0]

        for i in range(n_apps):
            application = df.iloc[i]
            assigned = False
            cluster_index = 0

            # Пробуем добавить точку в существующие кластеры

            for j in range(len(self.clusters)):

                # if на условие по времени доставки

                if self.max_date_dif(j,application['Срок поставки']) <= self.max_dif:
                    cluster_index = j
                    assigned = True

            if assigned:

                # добавляем в кластер по индексу
                self.clusters[cluster_index].append(application)

                # пересчитываем самую раннюю и самую позднюю даты доставки
                if self.dates[cluster_index][0] > application['Срок поставки']:
                    self.dates[cluster_index][0] = application['Срок поставки']
                elif self.dates[cluster_index][1] < application['Срок поставки']:
                    self.dates[cluster_index][1] = application['Срок поставки']

            # создаем новый кластер
            else:
                self.clusters.append([application])
                self.dates.append([application['Срок поставки'],application['Срок поставки']])

    def max_date_dif(self, date_index, delivery_date):
        """
        Вычисление наибольшей разницы между датами в возможном кластере
        """
        days_from_min = abs((delivery_date - self.dates[date_index][0]).days)
        days_from_max = abs((delivery_date - self.dates[date_index][1]).days)
        return max(days_from_max,days_from_min)

    def get_clusters(self):
        """
        Возвращает список кластеров в виде list[DataFrame].
        """
        df_clusters = []
        for cluster in self.clusters:
            df_clusters.append(pd.concat(cluster, axis=1).T)
        return df_clusters


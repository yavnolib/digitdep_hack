"""
# Инициализация + "обучение":
* Прочитать `Справочник грузополучателей.xlsx` из postgres в buyer=pd.DataFrame
* Прочитать `Исторические данные по офертам поставщиков на лот.csv` в all_df=pd.DataFrame
1. Кластеризовать всё, что в `Справочник грузополучателей.xlsx` и сохранить метки
2. Кластеризовать все материалы, что в `Исторические данные по офертам поставщиков на лот.csv` и сохранить метки

# Инференс
* Прочитать df = Загрузочный файл.xlsx
1.1. Передать df в первый time кластеризатор Эмира #1
1.2. Передать df в кластеризатор Камиля #2. 
    Если увидит, что не у всех покупателей из df есть координаты, то присвоит нанам отдельный кластер 
    и напишет варнинг с просьбой обновления файла: `Справочник грузополучателей.xlsx`
1.3. (Один "первый" класс - ~500мб оперативы, 2сек)
    Передать df в кластеризатор Льва #3.
    Если увидит, что не все материалы из df есть в графе, то присвоит нанам отдельный кластер
    и напишет варнинг с просьбой обновления файла: `Исторические данные по офертам поставщиков на лот.csv`
1.4. Передать df во второй time кластеризатор Эмира #4
2. Объединить все предсказания и сохранить в формате который дали нам.
3. Подать игоряну
"""

import pandas as pd
from src.cluster.date.app_time import ApplicationTimeClassificator
from src.cluster.date.del_time import DeliveryTimeClassificator
from src.cluster.geo.geocl import GeoClassificator
from concurrent.futures import ThreadPoolExecutor
from src.cluster.materials.matclust import MaterialCluster
import numpy as np
from copy import deepcopy


class Clustering:
    def __init__(self, input_df, data_folder='data', use_postgre=False):
        self.df_geo = input_df
        self.df = deepcopy(self.df_geo).astype(str)

        self.vedom = pd.read_excel(f'{data_folder}/kt_516.xlsx').astype(str).dropna()
        self.sprav = pd.read_excel(f'{data_folder}/sprav.xlsx').astype(str)
        self.mtr = pd.merge(self.sprav, self.vedom, how='inner', left_on='Класс', right_on='Класс в ЕСМ').drop(columns=['Класс в ЕСМ']).astype(str).set_index('Материал')
        self.preproc_time()
        
        self.tech_cols = ['time_cluster_1', 'time_cluster_2', 'geo_cluster', 'material_cluster']

        self.clustering_1 = ApplicationTimeClassificator(self.df, self.vedom, self.sprav, self.mtr, self.problem_data)
        self.clustering_2 = DeliveryTimeClassificator(self.df, self.vedom, self.sprav, self.mtr, self.problem_data, max_dif=30)
        self.clustering_3 = GeoClassificator(use_postgre=use_postgre)
        self.clustering_4 = MaterialCluster()

    
    def preproc_time(self):
        self.df.replace(['nan', 'NaT'], np.nan, inplace=True)
        self.df['Проблемная заявка'] = False

        self.df.loc[self.df[['Клиент', 'Материал', 'Срок поставки', 'Грузополучатель', '№ заказа', '№ позиции',
                       'Дата заказа']].isna().any(axis=1), 'Проблемная заявка'] = True

        self.df['Дата заказа'] = pd.to_datetime(self.df['Дата заказа'])
        self.df['Срок поставки'] = pd.to_datetime(self.df['Срок поставки'])
        self.df['срок'] = self.df['Срок поставки'] - self.df['Дата заказа']
        self.df['срок'] = self.df['срок'].apply(lambda x: x.days)

        self.df.loc[self.df['срок'] <= self.df['Материал'].apply(
            lambda x: int(self.mtr.loc[x, 'Нормативный срок поставки МТР']) if self.mtr.loc[x, 'Нормативный срок поставки МТР'].isnumeric() else 99999999
            ), 'Проблемная заявка'] = True

        self.problem_data = self.df[self.df['Проблемная заявка'] == True]
        self.df = self.df[self.df['Проблемная заявка'] == False]
        self.df.reset_index(inplace=True)
    
    def apply_first(self):
        clusters_1 = self.clustering_1.transform()
        clusters_1.time_cluster_1 = clusters_1.time_cluster_1.apply(lambda x: x if not pd.isna(x) else -1)
        return clusters_1
    
    def apply_second(self):
        clusters_2 = self.clustering_2.transform()
        clusters_2.time_cluster_2 = clusters_2.time_cluster_2.apply(lambda x: x if not pd.isna(x) else -1)
        return clusters_2
    
    def apply_third(self):
        clusters_3 = self.clustering_3.transform(data=self.df_geo, path='data/buyer_clusters.csv')
        return clusters_3

    def apply_fourth(self):
        clusters_4 = self.clustering_4.transform(data=self.df_geo, path='data/material_cluster.csv')
        return clusters_4
    
    def jsonify(self, df):
        valid_popularity = df.groupby('cluster_num').apply(lambda x: x['cluster_num'].count()).drop(-1) # 2
        v_df = (valid_popularity / valid_popularity.sum()).reset_index()
        v_df.columns = ['cluster_num', 'rate']
        v_df.rate *= 100
        top_clusters = v_df[v_df.rate.sort_values(ascending=False) > v_df.rate.mean() + 3*v_df.rate.std()].cluster_num.values.tolist()
        unique_mats = df.groupby('cluster_num').apply(lambda x: x['Материал'].unique().shape[0]).reset_index(name='unique_mats') # 1
        unique_buyers = df.groupby('cluster_num').apply(lambda x: x['Грузополучатель'].unique().shape[0]).reset_index(name='unique_buyers') # 4
        n_members = df.groupby('cluster_num').apply(lambda x: x['cluster_num'].count()).reset_index(name='n_members') # 2
        lot_sum = df.groupby('cluster_num').apply(lambda x: x['Цена'].sum()).reset_index(name='lot_sum') # 3
        metric_df = unique_mats.merge(unique_buyers).merge(n_members).merge(lot_sum)
        metric_df['is_top'] = metric_df.cluster_num.isin(top_clusters)
        return metric_df.set_index('cluster_num').to_json(orient='index')
    
    def transform(self):
        clusters_1 = self.apply_first()
        clusters_2 = self.apply_second()
        clusters_3 = self.apply_third()
        clusters_4 = self.apply_fourth()

        # Result df
        res_df = self.df_geo
        res_df['time_cluster_1'] = clusters_1['time_cluster_1']
        res_df['time_cluster_2'] = clusters_2['time_cluster_2']
        if clusters_3 is not None:
            res_df['geo_cluster'] = clusters_3['geo_cluster']
        if clusters_4 is not None:
            res_df['material_cluster'] = clusters_4['material_cluster']

        # Get result cluster
        cols_to_drop = list(set(res_df.columns.tolist()) & set(self.tech_cols))
        cluster_mapping = {tuple(k):v for v, k in enumerate(np.unique(res_df[cols_to_drop].values, axis=0).tolist())}
        for k in cluster_mapping:
            if (-1. in k):
                cluster_mapping.update({k: -1})
        # res_df['cluster_num'] = res_df[cols_to_drop].apply(lambda x: tuple(x[i] for i in cols_to_drop), axis=1).map(cluster_mapping)
        res_df['cluster_num'] = res_df[cols_to_drop].apply(lambda x: tuple(x[i] for i in cols_to_drop), axis=1).map(cluster_mapping)

        self.res_df = res_df
        returned_value = res_df.drop(columns=cols_to_drop)
        return returned_value, cl.jsonify(returned_value)


if __name__ == '__main__':
    input_df = pd.read_excel('data/Загрузочный файл.xlsx')
    cl = Clustering(input_df, data_folder='data', use_postgre=False)
    df, result_json = cl.transform()

    print(f"{df['cluster_num'].unique().shape=}")
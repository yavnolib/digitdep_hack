
import pandas as pd
import numpy as np
from copy import deepcopy


class ApplicationTimeClassificator:

    def __init__(self, df, vedom, sprav, mtr, problem_data):
        """
            Принимает на вход xlsx Загрузочного файла.
            Дополнительно инициализирует excel-таблицы с данными про МТР-кабели + нормативные сроки
            Получаем таблицу MTR при merge, которая содержат id товара MTR и его нормативные сроки поставки
        """
        self.drop_cols = ['level_0', 'срок', 'Проблемная заявка']

        self.df = deepcopy(df)
        self.vedom = deepcopy(vedom)
        self.sprav = deepcopy(sprav)
        self.mtr = deepcopy(mtr)
        self.problem_data = problem_data
    

    def preprocessing(self):
        """
        Преобработка полученных данных, формирование проблемных заявок из заявок с пропусками и заявок
        с не проходящими по нормам сроками доставок
        Сортировка данных по возрастанию даты заказа
        """
        
        self.time_clust_1 = np.zeros_like(self.df['Дата заказа'], dtype=int)
        self.df.sort_values(by='Дата заказа', inplace=True)
        self.df.reset_index(inplace=True)

    def __str__(self):
        return f'time classificator for application dates'

    def fit(self):
        """
        Сортировка в кластеры по датам ЗАЯВКИ с одинаковым календарным месяцем
        """

        try:
            month = self.df['Дата заказа'].iloc[0].month
            year = self.df['Дата заказа'].iloc[0].year
            self.time_clust_1[0] = 0

        except Exception as e:
            print(e)

        for i, el in self.df['Дата заказа'].items():

            if i == 0:
                continue
            if el.month == month and el.year == year:
                self.time_clust_1[i] = self.time_clust_1[i-1]
            else:
                month = el.month
                year = el.year
                self.time_clust_1[i] = self.time_clust_1[i-1] + 1

        self.df['time_cluster_1'] = pd.Series(self.time_clust_1)

    def transform(self):
        """
        Возвращает DataFrame с со столбцом time_cluster_1, являющимся результатом кластеризации по дате ЗАЯВКИ
        """
        self.preprocessing()
        self.fit()

        exist_cols = self.df.columns.tolist()
        res = self.df
        problems = self.problem_data.reset_index()
        return pd.concat([res, problems]).drop(columns=list(set(self.drop_cols) & set(exist_cols))).sort_values('index').set_index('index').reset_index(drop=True)
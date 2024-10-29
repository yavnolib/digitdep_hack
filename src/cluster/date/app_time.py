
import pandas as pd
import numpy as np


class ApplicationTimeClassificator:

    def __init__(self, xlsx_filename='/mnt/data/Загрузочный файл.xlsx'):
        """
            Принимает на вход xlsx Загрузочного файла.
            Дополнительно инициализирует excel-таблицы с данными про МТР-кабели + нормативные сроки
            Получаем таблицу MTR при merge, которая содержат id товара MTR и его нормативные сроки поставки
        """
        self.df = pd.read_excel(xlsx_filename)
        self.vedom = pd.read_excel('/mnt/data/kt_516.xlsx')
        self.sprav = pd.read_excel('/mnt/data/sprav.xlsx')

        self.df = self.df.astype(str)
        self.vedom = self.vedom.astype(str)
        self.sprav = self.sprav.astype(str)

        self.vedom.dropna(inplace=True)
        self.mtr = pd.merge(self.sprav, self.vedom, how='inner', left_on='Класс', right_on='Класс в ЕСМ')
        self.mtr.drop(columns=['Класс в ЕСМ'], inplace=True)
        self.mtr = self.mtr.astype(str)
        self.mtr.set_index('Краткий текст материала', inplace=True)

    def preprocessing(self):
        """
        Преобработка полученных данных, формирование проблемных заявок из заявок с пропусками и заявок
        с не проходящими по нормам сроками доставок
        Сортировка данных по возрастанию даты заказа
        """
        self.df.replace(['nan', 'NaT'], np.nan, inplace=True)
        self.df['Проблемная заявка'] = False

        self.df.loc[self.df[['Клиент', 'Материал', 'Срок поставки', 'Грузополучатель', '№ заказа', '№ позиции',
                       'Дата заказа']].isna().any(axis=1), 'Проблемная заявка'] = True

        self.df['Дата заказа'] = pd.to_datetime(self.df['Дата заказа'])
        self.df['Срок поставки'] = pd.to_datetime(self.df['Срок поставки'])
        self.df['срок'] = self.df['Срок поставки'] - self.df['Дата заказа']
        self.df['срок'] = self.df['срок'].apply(lambda x: x.days)

        self.df.loc[self.df['срок'] <= self.df['Материал'].apply(
            lambda x: int(self.mtr.loc[x, 'Нормативный срок поставки МТР'])), 'Проблемная заявка'] = True

        self.problem_data = self.df[self.df['Проблемная заявка'] == True]
        self.df = self.df[self.df['Проблемная заявка'] == False]
        self.df.reset_index(inplace=True)
        
        self.app_clust = np.zeros_like(self.df['Дата заказа'], dtype=int)
        self.df.sort_values(by='Дата заказа', inplace=True)
        self.df.reset_index(inplace=True)

    def __str__(self):
        return f'time classificator for application dates'

    def fit(self):
        """
        Сортировка заявок в кластеры по датам с одинаковым календарным месяцем
        """

        try:
            month = self.df['Дата заказа'].iloc[0].month
            year = self.df['Дата заказа'].iloc[0].year
            self.app_clust[0] = 0

        except Exception as e:
            print(e)

        for i, el in self.df['Дата заказа'].items():

            if i == 0:
                continue
            if el.month == month and el.year == year:
                self.app_clust[i] = self.app_clust[i-1]
            else:
                month = el.month
                year = el.year
                self.app_clust[i] = self.app_clust[i-1] + 1

        self.df['cluster'] = pd.Series(self.app_clust)
        return self.app_clust

    def get_clusters(self):
        """
        Возвращает массив кластеров в виде: list[DataFrame]
        """
        clusters = []
        for i in range(self.app_clust[-1]+1):
            clusters.append(self.df[self.df['cluster'] == i])
        return clusters


















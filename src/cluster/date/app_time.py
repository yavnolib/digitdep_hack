from copy import deepcopy

import numpy as np
import pandas as pd


class ApplicationTimeClassificator:
    def __init__(
        self,
        df: pd.DataFrame,
        sprav: pd.DataFrame,
        mtr: pd.DataFrame,
        problem_data: pd.DataFrame,
    ):
        """
        Инициализация кластеризатора

        :param: df - Загрузочный файл
        :param: sprav - Таблица с номером материала, кратким описанием и номером класса МТР
        :param: mtr - Таблица со всеми колонками по МТР
        :param: problem_data - pd.DataFrame проблемных заявок (невозможно провести кластеризацию, т.к. изначально не удовлетворяют ограничениям)
        """
        self.drop_cols = ["level_0", "срок", "Проблемная заявка"]

        self.df = deepcopy(df)
        self.sprav = deepcopy(sprav)
        self.mtr = deepcopy(mtr)
        self.problem_data = problem_data

    def preprocessing(self):
        """
        Преобработка полученных данных, формирование проблемных заявок из заявок с пропусками и заявок
        с не проходящими по нормам сроками доставок
        Сортировка данных по возрастанию даты заказа
        """

        self.time_clust_1 = np.zeros_like(self.df["Дата заказа"], dtype=int)
        self.df.sort_values(by="Дата заказа", inplace=True)
        self.df.reset_index(inplace=True)

    def __str__(self):
        return f"time classificator for application dates"

    def fit(self):
        """
        Кластеризует даты заявок в DataFrame, присваивая каждой уникальной комбинации
        месяц-год идентификатор кластера. Каждый кластер представляет собой непрерывный
        период в рамках одного месяца и года.
        """
        try:
            # Извлекаем период месяц-год из столбца 'Дата заказа' и вычисляем идентификаторы кластеров
            self.df["month_year"] = self.df["Дата заказа"].dt.to_period("M")
            self.df["time_cluster_1"] = (
                self.df["month_year"] != self.df["month_year"].shift()
            ).cumsum() - 1
            self.df.drop(columns="month_year", inplace=True)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def transform(self):
        """
        Возвращает DataFrame с со столбцом time_cluster_1, являющимся результатом кластеризации по дате ЗАЯВКИ
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

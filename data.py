import pandas as pd
import numpy as np
from datetime import datetime

'''
data preprocessing
'''

# normal view of df for Pycharm
pd.reset_option('display.max_rows')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# read xlsx
data = pd.read_excel('xlsx data/Загрузочный файл.xlsx')
vedom = pd.read_excel('xlsx data/КТ-516 Разделительная ведомость на поставку МТР с учетом нормативных сроков поставки.xlsx')
sprav = pd.read_excel('xlsx data/Кабель справочник МТР.xlsx')

# to str type
data = data.astype(str)
vedom = vedom.astype(str)
sprav = sprav.astype(str)

# general df with MTR info
vedom.dropna(inplace=True)
mtr = pd.merge(sprav,vedom, how='inner',left_on='Класс', right_on='Класс в ЕСМ')
mtr.drop(columns=['Класс в ЕСМ'],inplace=True)
mtr = mtr.astype(str)
mtr.set_index('Краткий текст материала',inplace=True)


# adding delivery time and problem application flag
data.replace('nan',np.nan,inplace=True)
data['Проблемная заявка'] = False

data.loc[data[['Клиент','Материал','Срок поставки','Грузополучатель','№ заказа','№ позиции','Дата заказа']].isna().any(axis=1),'Проблемная заявка'] = True

data['срок'] = (pd.to_datetime(data['Срок поставки']) - pd.to_datetime(data['Дата заказа']))
data['срок'] = data['срок'].apply(lambda x: x.days)

data.loc[data['срок'] <= data['Материал'].apply(lambda x: int(mtr.loc[x,'Нормативный срок поставки МТР'])),'Проблемная заявка'] = True

print(data)








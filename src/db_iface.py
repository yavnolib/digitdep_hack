import pandas as pd
import psycopg2
from psycopg2 import sql
from tqdm import tqdm
from pathlib import Path

class PostgreIface:
    def __init__(self):
        self.db_params = {
            'dbname': 'lotdb',
            'user': 'admin',
            'password': '12345678',
            'host': 'gpn_postgres_db',
            'port': 5432
        }
    
    def create_database(self, path_to_cache='/mnt/cache/'):
        for csv_file_path in tqdm([str(i) for i in Path(path_to_cache).glob('*.csv')]):
            df = pd.read_csv(csv_file_path)
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    create_table_query = sql.SQL("""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            {columns}
                        );
                    """).format(
                        table_name=sql.Identifier(Path(csv_file_path).stem),
                        columns=sql.SQL(', ').join([
                            sql.SQL("{} {}").format(sql.Identifier(col), sql.SQL("TEXT"))
                            for col in df.columns
                        ])
                    )
                    cur.execute(create_table_query)

                    for index, row in df.iterrows():
                        insert_query = sql.SQL("""
                            INSERT INTO {table_name} ({columns})
                            VALUES ({values});
                        """).format(
                            table_name=sql.Identifier(Path(csv_file_path).stem),
                            columns=sql.SQL(', ').join(map(sql.Identifier, df.columns)),
                            values=sql.SQL(', ').join(sql.Placeholder() * len(row))
                        )
                        cur.execute(insert_query, tuple(row))
                conn.commit()
            print("Таблица создана и данные успешно добавлены!")

            
    def read_table(self, table_name, columns=None):
        with psycopg2.connect(**self.db_params) as conn:
            df = pd.read_sql(f'select * from {table_name};', con=conn)
            df.replace("NaN", None, inplace=True)
            if columns is not None:
                df.columns = columns
        return df
    
    def upd_buyers(self, df, known):
        tmp_df = df[~df.geo.isna()]
        code_difference = list(set(df.code.values.tolist()) - set(known.code.values.tolist()))
        tmp_df = tmp_df[tmp_df.code.isin(code_difference)]
        print(f'table: {tmp_df.shape} WILL BE ADDED.')
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                for index, row in tmp_df.iterrows():
                    insert_query = sql.SQL("""
                        INSERT INTO {table_name} ({columns})
                        VALUES ({values});
                    """).format(
                        table_name=sql.Identifier('buyer'),
                        columns=sql.SQL(', ').join(map(sql.Identifier, tmp_df.columns)),
                        values=sql.SQL(', ').join(sql.Placeholder() * len(row))
                    )
                    cur.execute(insert_query, tuple(row))
            conn.commit()
        print("Таблица обновлена!")
    
    def upd_buyers_mode_2(self, buyer_path):
        if (Path(buyer_path).suffix == '.xlsx') or (Path(buyer_path).suffix == '.xls'):
            buyer_df = pd.read_excel(buyer_path)
        elif Path(buyer_path).suffix == '.csv':
            buyer_df = pd.read_csv(buyer_path)
        else:
            raise ValueError("Extension of buyer's file must be in ['.xlsx', '.xls', '.csv']")
        
        buyer_df.columns = ['code', 'addr', 'geo']
        buyer_df.code = buyer_df.code.astype(int)

        exist_df = self.read_table('buyer')
        exist_df.code = exist_df.code.astype(int)

        tmp_df = buyer_df[~buyer_df.geo.isna()]
        code_difference = list(set(buyer_df.code.values.tolist()) - set(exist_df.code.values.tolist()))
        tmp_df = tmp_df[tmp_df.code.isin(code_difference)]
        print(f'table: {tmp_df.shape} WILL BE ADDED.')
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                for index, row in tmp_df.iterrows():
                    insert_query = sql.SQL("""
                        INSERT INTO {table_name} ({columns})
                        VALUES ({values});
                    """).format(
                        table_name=sql.Identifier('buyer'),
                        columns=sql.SQL(', ').join(map(sql.Identifier, tmp_df.columns)),
                        values=sql.SQL(', ').join(sql.Placeholder() * len(row))
                    )
                    cur.execute(insert_query, tuple(row))
            conn.commit()
        print("Таблица обновлена!")

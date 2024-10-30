import pandas as pd
import numpy as np
import networkx as nx
import random
import os
import warnings

class MaterialCluster:
    def __init__(self) -> None:
        self.comm = []
        self.G = nx.Graph()

        self.total = {'material': [],
                      'cluster': []}

    def __create_links_from_cell(self, cell_list: np.ndarray) -> list[tuple]:
        edge_list = []

        for i in range(len(cell_list)):
            for j in range(i+1, len(cell_list)):
                edge_list.append((cell_list[i], cell_list[j], round(random.random(), 1)))

        return edge_list
    
    def __graph_parse(self, path: str, cols: list[str]) -> None:
        try:
            cols.index('creditor')
            cols.index('material')
        except ValueError as err:
            print(f"Error: {err}")
            return -1

        try:
            data = pd.read_csv(path)
        except FileNotFoundError as err:
            print(f"Error: {str(err)[10:]}")
            return -1
        
        data.columns = cols

        materials_by_creditor = pd.DataFrame(data.groupby(['creditor'])['material'].apply(lambda x: x.unique())).reset_index()
        
        tmp_materials = materials_by_creditor[:100]
        all_materials_list = []

        for materials_list in tmp_materials.material:
            all_materials_list.extend(materials_list)

        nodes = np.unique(all_materials_list)            
        edges_with_weights = []

        for materials_list in tmp_materials.material.values:
            edges_with_weights.extend(self.__create_links_from_cell(materials_list))

        self.G.add_nodes_from(nodes)

        for edge in edges_with_weights:
            self.G.add_edge(edge[0], edge[1], weight=edge[2])

    def get_num_clusters(self) -> int:
        return len(self.comm)
    
    def get_num_each(self) -> list[int]:
        each = [len(_) for _ in self.comm]
        
        return each
    
    def fit(self, path: str = 'data/all.csv',
            cols: list[str] = ['lot_id', 'creditor', 'sum', 'material', 'short_text', 'currency', 
                               'scale', 'short_material_text', 'mat_class', 'name_text']) -> None:
        self.__graph_parse(path, cols)

        self.comm = list(nx.algorithms.community.label_propagation_communities(self.G)) 

        for node in self.G:
            for i in range(len(self.comm)):
                if node in self.comm[i]:
                    self.total['material'].append(node)
                    self.total['cluster'].append(i+1)
        
    def save(self, path: str = 'out/material_cluster.csv') -> None:
        directory = '/'.join(path.split('/')[:-1])
        os.makedirs(directory, exist_ok=True)

        pd.DataFrame(self.total).to_csv(path, index=False)
        print(f"Clusterization result is saved in \"{path}\"")
        
    def transform(self, data: pd.DataFrame, mat_col: str, from_csv: bool = False, 
                  path: str = 'out/material_cluster.csv') -> pd.DataFrame:
        if not from_csv:
            total_df = pd.DataFrame(self.total)
        else:
            try:
                total_df = pd.read_csv(path)
            except FileNotFoundError as err:
                print(f"Error: {str(err)[10:]}")
                return -1

            try:
                total_df.material
                total_df.cluster
            except AttributeError as err:
                print(f"Error: {err}")
                return -1

        data_cluster = data.rename(columns={mat_col: 'material'})
        data_cluster = pd.merge(data_cluster, total_df, on='material', how='left')

        if data_cluster.cluster.isna().sum() > 0:
            warnings.warn(f"Update the file \"Исторические данные по офертам поставщиков на лот.csv\", not all materials have a cluster")

        data_cluster.fillna(self.get_num_clusters()+1, inplace=True)
        data_cluster.rename(columns={'material': mat_col, 'cluster': 'material_cluster'}, inplace=True)
        data_cluster['material_cluster'] = data_cluster['material_cluster'].astype(int) 

        return data_cluster
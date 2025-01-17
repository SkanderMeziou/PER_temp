# coding=utf-8
import os
import pandas as pd
import numpy as np
from jaccard_impl import get_authors_by_issn, jaccard_distance

# Dossier contenant les fichiers clean_*.csv
data_folder = './data/cleanScopus'

# Lister les fichiers commençant par 'clean_'
files = [f for f in os.listdir(data_folder) if f.startswith('clean_') and f.endswith('.csv')]

# Fonction pour calculer la matrice de Jaccard
def compute_jaccard_matrix(file_path):
    # Charger le fichier CSV
    df = pd.read_csv(file_path)

    # Créer la carte ISSN -> auteurs
    issn_authors_map = get_authors_by_issn(df)
    issn_list = list(issn_authors_map.keys())

    # Initialiser une matrice vide
    num_issn = len(issn_list)
    distance_matrix = np.zeros((num_issn, num_issn))

    # Remplir la matrice avec les distances de Jaccard
    for i in range(num_issn):
        for j in range(i, num_issn):  # On calcule uniquement la moitié supérieure (matrice symétrique)
            if i == j:
                distance_matrix[i][j] = 0  # Distance à soi-même est toujours 0
            else:
                set1 = issn_authors_map[issn_list[i]]
                set2 = issn_authors_map[issn_list[j]]
                distance = jaccard_distance(set1, set2)
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance  # Matrice symétrique

    # Convertir en DataFrame pour faciliter l'analyse
    distance_df = pd.DataFrame(distance_matrix, index=issn_list, columns=issn_list)
    return distance_df

# Calculer la matrice de Jaccard pour chaque fichier
output_folder = './jaccardIndex'
os.makedirs(output_folder, exist_ok=True)

overall_issn_authors_map = {}

for file in files:
    file_path = os.path.join(data_folder, file)
    print(f"Calcul de la matrice pour {file} ...")

    # Calculer la matrice pour le fichier
    distance_df = compute_jaccard_matrix(file_path)

    # Sauvegarder dans un fichier CSV
    output_file = os.path.join(output_folder, f'jaccard_{file}')
    distance_df.to_csv(output_file)
    print(f"Matrice sauvegardée dans : {output_file}")

    # Ajouter les auteurs pour l'overall
    df = pd.read_csv(file_path)
    issn_authors_map = get_authors_by_issn(df)
    for issn, authors in issn_authors_map.items():
        if issn not in overall_issn_authors_map:
            overall_issn_authors_map[issn] = set()
        overall_issn_authors_map[issn].update(authors)

# Calculer la matrice "overall" (tous les fichiers combinés)
print("Calcul de la matrice globale (overall)...")
overall_issn_list = list(overall_issn_authors_map.keys())
num_issn_overall = len(overall_issn_list)
overall_distance_matrix = np.zeros((num_issn_overall, num_issn_overall))

for i in range(num_issn_overall):
    for j in range(i, num_issn_overall):
        if i == j:
            overall_distance_matrix[i][j] = 0  # Distance à soi-même
        else:
            set1 = overall_issn_authors_map[overall_issn_list[i]]
            set2 = overall_issn_authors_map[overall_issn_list[j]]
            distance = jaccard_distance(set1, set2)
            overall_distance_matrix[i][j] = distance
            overall_distance_matrix[j][i] = distance  # Matrice symétrique

# Convertir et sauvegarder la matrice "overall"
overall_distance_df = pd.DataFrame(overall_distance_matrix, index=overall_issn_list, columns=overall_issn_list)
overall_output_file = os.path.join(output_folder, 'jaccard_overall.csv')
overall_distance_df.to_csv(overall_output_file)
print(f"Matrice globale sauvegardée dans : {overall_output_file}")

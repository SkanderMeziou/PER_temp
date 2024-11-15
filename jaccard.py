import pandas as pd
import random
from sklearn.metrics import jaccard_score
from sklearn.preprocessing import MultiLabelBinarizer

# Charger le CSV
df = pd.read_csv('./data/scopus/COMP.csv')  # Remplace par ton fichier réel
print("initializing..")

# Fonction pour obtenir la liste des auteurs pour chaque ISSN
def get_authors_by_issn(dataframe):
    dataframe['author_list'] = dataframe['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    dataframe['authors'] = dataframe['author_list'].apply(lambda x: {d['authname'] for d in x})
    issn_authors_map = dataframe.groupby('prism:issn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    return issn_authors_map

# Fonction pour encoder les ensembles d'auteurs en vecteurs binaires
def encode_authors(issn_authors_map):
    mlb = MultiLabelBinarizer()
    print("Encodage des ensembles d'auteurs en vecteurs binaires...")
    encoded_matrix = mlb.fit_transform(issn_authors_map.values())
    print("Encodage terminé.")
    return encoded_matrix, list(issn_authors_map.keys()), mlb.classes_

# Fonction pour traiter les scores et afficher les statistiques
def process_scores(scores):
    scores.sort(key=lambda x: x[2])
    closest_pair = scores[0]
    farthest_pair = scores[-1]
    print(f"Les deux journaux les plus proches : {closest_pair[0]} et {closest_pair[1]} avec une distance de {closest_pair[2]:.4f}")
    print(f"Les deux journaux les plus éloignés : {farthest_pair[0]} et {farthest_pair[1]} avec une distance de {farthest_pair[2]:.4f}")
    avg_distance = sum(d[2] for d in scores) / len(scores)
    print(f"Distance moyenne entre les journaux : {avg_distance:.4f}")
    return scores

# Fonction pour analyser tous les ISSN
def analyze_every_issn(dataframe):
    issn_authors_map = get_authors_by_issn(dataframe)
    encoded_matrix, issn_list, _ = encode_authors(issn_authors_map)
    
    scores = []
    total_comparisons = len(issn_list) * (len(issn_list) - 1) // 2
    print(f"Nombre total de comparaisons à effectuer : {total_comparisons}")
    
    count = 0
    for i in range(len(issn_list)):
        if i % 10 == 0:  # Afficher un log toutes les 10 itérations
            print(f"Progression : {i} / {len(issn_list)}")
        
        for j in range(i + 1, len(issn_list)):
            vector1 = encoded_matrix[i]
            vector2 = encoded_matrix[j]
            distance = jaccard_score(vector1, vector2)
            scores.append((issn_list[i], issn_list[j], distance))
            
            count += 1
            if count % 1000 == 0:  # Afficher un log toutes les 1000 comparaisons
                print(f"Comparaisons effectuées : {count} / {total_comparisons}")
    
    print("Comparaisons terminées.")
    return process_scores(scores)

# Exemple d'appel de la fonction
print("c'est parti pour le calcul !")
distances = analyze_every_issn(df)

import pandas as pd
import random
from sklearn.metrics import jaccard_score

# Charger le CSV
df = pd.read_csv('./data/scopus/COMP.csv')  # Remplace par ton fichier réel
print("initializing..")

# Fonction pour obtenir la liste des auteurs pour chaque ISSN
def get_authors_by_issn(dataframe):
    dataframe['author_list'] = dataframe['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    dataframe['authors'] = dataframe['author_list'].apply(lambda x: {d['authname'] for d in x})
    issn_authors_map = dataframe.groupby('prism:issn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    return issn_authors_map

# Fonction pour traiter les scores et afficher les statistiques
def process_scores(scores):
    scores.sort(key=lambda x: x[2])
    # Les deux auteurs les plus proches et les deux plus loin
    closest_pair = scores[0]
    farthest_pair = scores[-1]
    print(
        f"Les deux journaux les plus proches : {closest_pair[0]} et {closest_pair[1]} avec une distance de {closest_pair[2]:.4f}")
    print(
        f"Les deux journaux les plus éloignés : {farthest_pair[0]} et {farthest_pair[1]} avec une distance de {farthest_pair[2]:.4f}")
    # Statistiques supplémentaires
    avg_distance = sum(d[2] for d in scores) / len(scores)
    print(f"Distance moyenne entre les journaux : {avg_distance:.4f}")
    return scores

# Fonction pour analyser 100 ISSN aléatoires et extraire des statistiques
def analyze_random_issn(dataframe, num_issn=300):
    issn_authors_map = get_authors_by_issn(dataframe)
    issn_list = list(issn_authors_map.keys())
    
    if len(issn_list) < num_issn:
        num_issn = len(issn_list)
    
    sampled_issn = random.sample(issn_list, num_issn)
    scores = []
    
    for i in range(len(sampled_issn)):
        for j in range(i + 1, len(sampled_issn)):
            issn1 = sampled_issn[i]
            issn2 = sampled_issn[j]
            distance = jaccard_score(issn_authors_map[issn1], issn_authors_map[issn2])
            scores.append((issn1, issn2, distance))

    return process_scores(scores)

def analyze_every_issn(dataframe):
    issn_authors_map = get_authors_by_issn(dataframe)
    issn_list = list(issn_authors_map.keys())
    
    scores = []
    
    for i in range(len(issn_list)):
        print(i,"/",len(issn_list))
        for j in range(i + 1, len(issn_list)):
            issn1 = issn_list[i]
            issn2 = issn_list[j]
            distance = jaccard_score(issn_authors_map[issn1], issn_authors_map[issn2])
            scores.append((issn1, issn2, distance))
    
    return process_scores(scores)

# Exemple d'appel de la fonction
print("c'est parti pour le calcul !")
distances = analyze_every_issn(df)
import random

import pandas as pd

# Charger le CSV
#df = pd.read_csv('./data/scopus/PHYS.csv')  # Remplace par ton fichier réel
print("initializing..")
# Fonction pour obtenir la liste des auteurs pour chaque ISSN
def get_authors_by_issn(df):
    df['author_list'] = df['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    df['authors'] = df['author_list'].apply(lambda x: {d['authid'] for d in x})
    issn_authors_map = df.groupby('prism:issn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    return issn_authors_map

def get_authors_by_eissn(df):
    df['author_list'] = df['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    df['authors'] = df['author_list'].apply(lambda x: {d['authid'] for d in x})
    eissn_authors_map = df.groupby('prism:eIssn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    return eissn_authors_map


def get_authors_map_with_validation(df):
    # Étape 1 : Extraire les informations sur les auteurs
    df['author_list'] = df['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    df['authors'] = df['author_list'].apply(lambda x: {d['authid'] for d in x})
    
    # Étape 2 : Construire les mappages ISSN et eISSN
    issn_authors_map = df.groupby('prism:issn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    eissn_authors_map = df.groupby('prism:eIssn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    
    # Étape 3 : Construire une map combinée (couples ISSN/eISSN)
    combined_map = {}
    for _, row in df.iterrows():
        issn = row['prism:issn']
        eissn = row['prism:eIssn']
        authors = row['authors']
        
        if (issn, eissn) not in combined_map:
            combined_map[(issn, eissn)] = set()
        combined_map[(issn, eissn)].update(authors)
    
    # Étape 4 : Vérification des conflits entre ISSN et eISSN
    conflicts = []
    grouped_by_issn = df.groupby('prism:issn')['prism:eIssn'].unique()
    for issn, eissns in grouped_by_issn.items():
        if len(eissns) > 1:
            conflicts.append((issn, eissns))
    
    # Étape 5 : Afficher les conflits
    if conflicts:
        print("Conflits détectés (même ISSN avec plusieurs eISSN) :")
        for issn, eissns in conflicts:
            print(f"ISSN: {issn} a plusieurs eISSN associés : {list(eissns)}")
    else:
        print("Aucun conflit détecté entre ISSN et eISSN.")
    
    return combined_map

# Fonction pour calculer la distance de Jaccard
def jaccard_distance(set1, set2):
    if not set1 or not set2:
        return 1.0  # Distance maximale si l'un des ensembles est vide
    union_size = len(set1.union(set2))
    intersection_size = len(set1.intersection(set2))
    jaccard_index = intersection_size / union_size
    return 1 - jaccard_index  # Distance de Jaccard

# Fonction pour analyser 100 ISSN aléatoires et extraire des statistiques
def analyze_random_issn(df, num_issn=300):
    issn_authors_map = get_authors_by_issn(df)
    issn_list = list(issn_authors_map.keys())
    
    if len(issn_list) < num_issn:
        num_issn = len(issn_list)
    
    sampled_issn = random.sample(issn_list, num_issn)
    distances = []
    
    for i in range(len(sampled_issn)):
        for j in range(i + 1, len(sampled_issn)):
            issn1 = sampled_issn[i]
            issn2 = sampled_issn[j]
            distance = jaccard_distance(issn_authors_map[issn1], issn_authors_map[issn2])
            distances.append((issn1, issn2, distance))
    
    distances.sort(key=lambda x: x[2])
    
    # Les deux auteurs les plus proches et les deux plus loin
    closest_pair = distances[0]
    farthest_pair = distances[-1]
    
    print(f"Les deux journaux les plus proches : {closest_pair[0]} et {closest_pair[1]} avec une distance de {closest_pair[2]:.4f}")
    print(f"Les deux journaux les plus éloignés : {farthest_pair[0]} et {farthest_pair[1]} avec une distance de {farthest_pair[2]:.4f}")
    
    # Statistiques supplémentaires
    avg_distance = sum(d[2] for d in distances) / len(distances)
    print(f"Distance moyenne entre les journaux : {avg_distance:.4f}")
    
    return distances


def analyze_every_issn(df):
    issn_authors_map = get_authors_by_issn(df)
    issn_list = list(issn_authors_map.keys())
    
    
    distances = []
    
    for i in range(len(issn_list)):
        print(i,"/",len(issn_list))
        for j in range(i + 1, len(issn_list)):
            issn1 = issn_list[i]
            issn2 = issn_list[j]
            distance = jaccard_distance(issn_authors_map[issn1], issn_authors_map[issn2])
            distances.append((issn1, issn2, distance))
    
    distances.sort(key=lambda x: x[2])
    
    # Les deux auteurs les plus proches et les deux plus loin
    closest_pair = distances[0]
    farthest_pair = distances[-1]
    
    print(f"Les deux journaux les plus proches : {closest_pair[0]} et {closest_pair[1]} avec une distance de {closest_pair[2]:.4f}")
    print(f"Les deux journaux les plus éloignés : {farthest_pair[0]} et {farthest_pair[1]} avec une distance de {farthest_pair[2]:.4f}")
    
    # Statistiques supplémentaires
    avg_distance = sum(d[2] for d in distances) / len(distances)
    print(f"Distance moyenne entre les journaux : {avg_distance:.4f}")
    
    return distances


"""# Exemple d'appel de la fonction
print("c'est parti pour le calcul !")
distances = analyze_every_issn(df)"""
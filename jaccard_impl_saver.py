import os
import pandas as pd

# Fonction pour obtenir la liste des auteurs pour chaque ISSN
def get_authors_by_issn(dataframe):
    dataframe['author_list'] = dataframe['author_info'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    dataframe['authors'] = dataframe['author_list'].apply(lambda x: {d['authname'] for d in x})
    issn_authors_map = dataframe.groupby('prism:issn')['authors'].apply(lambda x: set.union(*x)).to_dict()
    return issn_authors_map

# Fonction pour calculer la distance de Jaccard manuellement
def jaccard_distance(set1, set2):
    if not set1 or not set2:
        return 1.0  # Distance maximale si l'un des ensembles est vide
    union_size = len(set1.union(set2))
    intersection_size = len(set1.intersection(set2))
    jaccard_index = intersection_size / union_size
    return 1 - jaccard_index  # Distance de Jaccard

# Fonction pour traiter les scores et sauvegarder dans un fichier avec des détails supplémentaires
def process_and_save_scores(scores, output_path, csv_filename, num_journals):
    scores.sort(key=lambda x: x[2])
    closest_pair = scores[0]
    farthest_pair = scores[-1]
    avg_distance = sum(d[2] for d in scores) / len(scores)
    
    with open(output_path, 'a', encoding="utf8") as f:
        f.write(f"Fichier CSV traité : {csv_filename}\n")
        f.write(f"Nombre de journaux : {num_journals}\n")
        f.write(f"Les deux journaux les plus proches : {closest_pair[0]} et {closest_pair[1]} avec une distance de {closest_pair[2]:.4f}\n")
        f.write(f"Les deux journaux les plus éloignés : {farthest_pair[0]} et {farthest_pair[1]} avec une distance de {farthest_pair[2]:.4f}\n")
        f.write(f"Distance moyenne entre les journaux : {avg_distance:.4f}\n")
        f.write(f"Nombre total de comparaisons : {len(scores)}\n")
        f.write("\n")

# Fonction pour analyser tous les ISSN et sauvegarder les résultats
def analyze_and_save_results(directory, output_path):
    if not os.path.exists(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        open(output_path, 'w').close()  # Créer le fichier s'il n'existe pas
    
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            print(f"Traitement du fichier : {filename}")
            df = pd.read_csv(os.path.join(directory, filename))
            
            issn_authors_map = get_authors_by_issn(df)
            issn_list = list(issn_authors_map.keys())
            num_journals = len(issn_list)
            
            scores = []
            total_comparisons = num_journals * (num_journals - 1) // 2
            print(f"Nombre total de comparaisons à effectuer : {total_comparisons}")
            
            count = 0
            for i in range(num_journals):
                if i % 10 == 0:  # Afficher un log toutes les 10 itérations
                    print(f"Progression : {i} / {num_journals}")
                
                for j in range(i + 1, num_journals):
                    issn1 = issn_list[i]
                    issn2 = issn_list[j]
                    distance = jaccard_distance(issn_authors_map[issn1], issn_authors_map[issn2])
                    scores.append((issn1, issn2, distance))
                    
                    count += 1
                    if count % 50000 == 0:  # Afficher un log toutes les 50 000 comparaisons
                        print(f"Comparaisons effectuées : {count} / {total_comparisons}")
            
            print("Comparaisons terminées.")
            process_and_save_scores(scores, output_path, filename, num_journals)

# Appel de la fonction pour traiter tous les fichiers CSV dans le dossier spécifié
directory = './data/cleanScopus'
output_path = './detailed_counts/jaccard_distances.txt'
analyze_and_save_results(directory, output_path)


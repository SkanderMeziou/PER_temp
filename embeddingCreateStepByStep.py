import os
import time
import numpy as np
import pandas as pd
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
print("creating necessary folders...")

# Creer les dossiers necessaires pour sauvegarder les resultats
base_dir = "embedding_results_stats_progressive"
os.makedirs(base_dir, exist_ok=True)
embedding_dir = os.path.join(base_dir, "embeddings")
plots_dir = os.path.join(base_dir, "plots")
os.makedirs(embedding_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)
print("loading distances matrix...")

# Charger la matrice de distances
distance_matrix_path = 'jaccardIndex/jaccard_overall.csv'
distance_matrix = pd.read_csv(distance_matrix_path, low_memory=False)
distance_matrix.set_index('Unnamed: 0', inplace=True)
distance_matrix = distance_matrix.astype(float)

print("verifications...")

# Verification si la matrice est carree et symetrique
assert distance_matrix.shape[0] == distance_matrix.shape[1], "La matrice doit etre carree."
assert np.allclose(distance_matrix, distance_matrix.T), "La matrice doit etre symetrique."
print("defining sizes...")


# Definir les tailles progressives (10, 100, 1000, etc.)
sizes = [10, 100, 1000, 10000]
if distance_matrix.shape[0] > 10000:
    sizes += list(range(20000, distance_matrix.shape[0] + 1, 20000))
else:
    sizes.append(distance_matrix.shape[0])  # Ajouter la taille totale si elle est inferieure a 1000

# Liste pour sauvegarder les temps d'execution
execution_times = []

# Fonction pour mesurer et sauvegarder les resultats
def compute_mds_for_subset(size):
    print("computing for",size,"publications")
    print("Processing with",size," journals")
    subset_matrix = distance_matrix.iloc[:size, :size]  # Sous-matrice carree
    start_time = time.time()

    # Calculer l'embedding MDS
    mds = MDS(n_components=2, dissimilarity='precomputed', metric=False, random_state=42)
    embedding = mds.fit_transform(subset_matrix.values)
    elapsed_time = time.time() - start_time

    # Sauvegarder les resultats
    embedding_df = pd.DataFrame(embedding, index=subset_matrix.index, columns=["Dim_1", "Dim_2"])
    embedding_path = os.path.join(embedding_dir, f"embedding_MDS_{size}journals.csv")
    embedding_df.to_csv(embedding_path)
    
    print(f"Finished {size} journals in {elapsed_time:.2f} seconds.")
    return size, elapsed_time

print("starting...")

# Calculer MDS pour chaque taille definie
for size in sizes:
    size, elapsed_time = compute_mds_for_subset(size)
    print(elapsed_time)
    execution_times.append((size, elapsed_time))

# Convertir les resultats en DataFrame
times_df = pd.DataFrame(execution_times, columns=["Number of Journals", "Execution Time (s)"])

# Sauvegarder les temps d'execution
times_path = os.path.join(base_dir, "execution_times.csv")
times_df.to_csv(times_path, index=False)

def plot_stress_vs_dimensions(distance_matrix, max_dimensions=300, step=10):
    dimensions = list(range(10, max_dimensions + 1, step))
    stress_values = []

    for dim in dimensions:
        print("Processing MDS for ",dim," dimensions...")
        mds = MDS(n_components=dim, dissimilarity='precomputed', metric=False, random_state=42)
        embedding = mds.fit_transform(distance_matrix.values)
        stress = mds.stress_

        # Sauvegarder les vecteurs d'embedding pour chaque dimension
        embedding_df = pd.DataFrame(embedding, index=distance_matrix.index, columns=[f"Dim_{i+1}" for i in range(dim)])
        embedding_path = os.path.join(embedding_dir, f"embedding_MDS_{dim}D.csv")
        embedding_df.to_csv(embedding_path)

        # Enregistrer le stress
        stress_values.append(stress)

    # Tracer et sauvegarder le graphique
    plt.figure(figsize=(10, 6))
    plt.plot(dimensions, stress_values, marker='o', linestyle='-', color='b')
    plt.title("Stress en fonction du nombre de dimensions (MDS)")
    plt.xlabel("Nombre de dimensions")
    plt.ylabel("Stress")
    plt.grid(True)
    stress_plot_path = os.path.join(plots_dir, "stress_vs_dimensions.png")
    plt.savefig(stress_plot_path)
    plt.close()


# Generer un graphique des temps d'execution
plt.figure(figsize=(10, 6))
plt.plot(times_df["Number of Journals"], times_df["Execution Time (s)"], marker='o', linestyle='-')
plt.title("Temps d'execution en fonction du nombre de journaux")
plt.xlabel("Nombre de journaux")
plt.ylabel("Temps d'execution (secondes)")
plt.grid(True)

# Sauvegarder et afficher le graphique
graph_path = os.path.join(plots_dir, "execution_time_graph.png")
plt.savefig(graph_path)
plt.show()

print(f"Resultats sauvegardes dans {base_dir}.")

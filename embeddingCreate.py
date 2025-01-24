import os
import time
import numpy as np
import pandas as pd
from sklearn.manifold import MDS, TSNE
import plotly.express as px
import matplotlib.pyplot as plt
import json

# Créer les dossiers nécessaires pour sauvegarder les résultats
base_dir = "embedding_results_stats"
os.makedirs(base_dir, exist_ok=True)
embedding_dir = os.path.join(base_dir, "embeddings")
plots_dir = os.path.join(base_dir, "plots")
os.makedirs(embedding_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

# Charger la matrice de distances
distance_matrix_path = 'jaccardIndex/jaccard_overall.csv'
distance_matrix = pd.read_csv(distance_matrix_path, low_memory=False)
distance_matrix.set_index('Unnamed: 0', inplace=True)
distance_matrix = distance_matrix.astype(float)

# Vérification si la matrice est carrée et symétrique
assert distance_matrix.shape[0] == distance_matrix.shape[1], "La matrice doit être carrée."
assert np.allclose(distance_matrix, distance_matrix.T), "La matrice doit être symétrique."

# Fonction pour mesurer le temps et sauvegarder les résultats
def time_and_save(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed_time = time.time() - start_time
    with open(os.path.join(base_dir, "execution_times.txt"), "a") as f:
        f.write(f"{func.__name__}: {elapsed_time:.2f} seconds\n")
    return result

# Fonction pour effectuer l'embedding et sauvegarder les résultats
def visualize_embedding(distance_matrix, n_dimensions=2, method="MDS"):
    print(f"Running {method} for {n_dimensions} dimensions...")
    mds = MDS(n_components=n_dimensions, dissimilarity='precomputed', metric=False, random_state=42)
    embedding = mds.fit_transform(distance_matrix.values)
    stress = mds.stress_

    # Sauvegarder l'embedding
    embedding_df = pd.DataFrame(embedding, index=distance_matrix.index, columns=[f"Dim_{i+1}" for i in range(n_dimensions)])
    embedding_path = os.path.join(embedding_dir, f"embedding_{method}_{n_dimensions}D.csv")
    embedding_df.to_csv(embedding_path)

    # Si 2D, générer et sauvegarder une visualisation
    if n_dimensions == 2:
        title = f"Projection en 2D avec {method} (Stress: {stress:.2f})"
        fig = px.scatter(
            x=embedding[:, 0],
            y=embedding[:, 1],
            text=distance_matrix.index,
            labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
            title=title
        )
        fig.update_traces(textposition='top center')
        plot_path = os.path.join(plots_dir, f"{method}_2D_plot.html")
        fig.write_html(plot_path)

    return embedding, stress

# Fonction pour calculer le stress et sauvegarder le graphique
def plot_stress_vs_dimensions(distance_matrix, max_dimensions=300, step=10):
    dimensions = list(range(10, max_dimensions + 1, step))
    stress_values = []

    for dim in dimensions:
        print(f"Processing MDS for {dim} dimensions...")
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

# Fonction pour appliquer t-SNE après MDS et sauvegarder les résultats
def tsne_from_mds(embedding_mds, n_dimensions=2):
    print(f"Running t-SNE for {n_dimensions} dimensions...")
    tsne = TSNE(n_components=n_dimensions, random_state=42, init="random")
    embedding_tsne = tsne.fit_transform(embedding_mds)

    # Sauvegarder l'embedding t-SNE
    tsne_df = pd.DataFrame(embedding_tsne, columns=[f"Dim_{i+1}" for i in range(n_dimensions)])
    tsne_path = os.path.join(embedding_dir, f"tsne_embedding_{n_dimensions}D.csv")
    tsne_df.to_csv(tsne_path)

    # Générer et sauvegarder une visualisation
    if n_dimensions == 2:
        fig = px.scatter(
            x=embedding_tsne[:, 0],
            y=embedding_tsne[:, 1],
            title="Projection en 2D avec t-SNE (à partir de MDS)",
            labels={"x": "Dimension 1", "y": "Dimension 2"}
        )
        tsne_plot_path = os.path.join(plots_dir, "tsne_2D_plot.html")
        fig.write_html(tsne_plot_path)

    return embedding_tsne

# Exécution des étapes et sauvegarde des résultats
embedding_mds, stress_mds_2d = time_and_save(visualize_embedding, distance_matrix, n_dimensions=2, method="MDS")
time_and_save(plot_stress_vs_dimensions, distance_matrix, max_dimensions=600, step=10)
time_and_save(tsne_from_mds, embedding_mds, n_dimensions=2)

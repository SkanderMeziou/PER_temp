# Ouvre un fichier en mode écriture (ou le crée s'il n'existe pas)
with open("hello_world.txt", "w") as file:
    # Écrit le message dans le fichier
    file.write("Hello World")

print("Fichier 'hello_world.txt' créé avec succès.")
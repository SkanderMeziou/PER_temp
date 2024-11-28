import os
import pandas as pd

with open("journals_count.csv", 'w') as f:
    f.write('discipline,nb_journals\n')
nb_journals = 0
for filename in os.listdir("../"):
    if filename.endswith('.csv') and filename != "journals_count.csv":
        df = pd.read_csv(filename)
        discipline = filename.split('.')[0].split('_')[1]
        nb_journals += len(df)
        with open("journals_count.csv", 'a') as f:
            f.write(f'{discipline},{len(df)}\n')

with open("journals_count.csv", 'a') as f:
    f.write(f'overall,{nb_journals}\n')

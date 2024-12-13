from pathlib import Path
import pandas as pd

input_dir = Path('../../../data/cleanScopus/')
#create empty df
overall = pd.DataFrame(columns=["prism:issn", "prism:eIssn"])

with open("journals_count2.csv", 'w') as f:
    f.write('discipline,nb_journals\n')
nb_journals = 0
for filename in input_dir.glob('*.csv'):
    df = pd.read_csv(filename)
    df = df[df["prism:aggregationType"] == "Journal"][["prism:issn", "prism:eIssn"]].drop_duplicates()
    overall = pd.concat([overall, df], ignore_index=True)
    discipline = filename.stem
    with open("journals_count2.csv", 'a') as f:
        f.write(f'{discipline},{len(df)}\n')

overall = overall.drop_duplicates()
with open("journals_count2.csv", 'a') as f:
    f.write(f'overall,{len(overall)}\n')

from pathlib import Path

import pandas as pd

# Dossiers
input_dir = Path('./data/scopus')
output_dir = Path('./detailed_counts/csvs')
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / 'detailed_stats.csv'
with open(output_file, 'w') as f:
    f.write("filename,nb pub,"
            "nb pubs in journals,nb clean pubs in j,% clean pubJ / pubJ,% clean pubJ / pub,"
            "nb_articles in journals,nb clean articles in j,% clean artJ / artJ,% clean artJ / pub\n")

overall_nb_pub = 0
overall_nb_journals_pub = 0
overall_nb_article = 0
overall_nb_clean_article = 0
overall_journals = {"clean": 0, "unclean": 0}
overall_dict = {"clean": pd.Series(dtype=int), "unclean": pd.Series(dtype=int)}

for filename in input_dir.glob('*.csv'):
    print(filename)
    input_path = filename

    df = pd.read_csv(input_path)

    nb_pub = len(df)
    journals = df[df["prism:aggregationType"] == "Journal"]
    nb_journals_pub = len(journals)
    is_clean = journals["prism:issn"].notnull() | journals["prism:eIssn"].notnull()
    nb_clean = is_clean.sum()
    articles = journals["subtypeDescription"] == "Article"
    nb_articles = articles.sum()
    nb_clean_articles = (is_clean & articles).sum()

    for name, pred in (("clean", is_clean), ("unclean", ~is_clean)):
        subset = journals[pred]
        subtype_count = subset["subtypeDescription"].value_counts()
        nb_current_journals = len(subset)
        overall_journals[name] += nb_current_journals
        overall_dict[name] = overall_dict[name].add(subtype_count, fill_value=0)

    with open(output_file, 'a') as f:
        f.write(f"{filename.name},{nb_pub},"
                f"{nb_journals_pub},{nb_clean},{nb_clean / nb_journals_pub:.2%},{nb_clean / nb_pub:.2%},"
                f"{nb_articles},{nb_clean_articles},{nb_clean_articles / nb_articles:.2%},{nb_clean_articles / nb_pub:.2%}\n")

    overall_nb_pub += nb_pub
    overall_nb_journals_pub += nb_journals_pub
    overall_nb_article += nb_articles
    overall_nb_clean_article += nb_clean_articles

with open(output_file, 'a') as f:
    f.write(f"Overall,{overall_nb_pub},"
            f"{overall_nb_journals_pub},{overall_journals['clean']},{overall_journals['clean'] / overall_nb_journals_pub:.2%},"
            f"{overall_journals['clean'] / overall_nb_pub:.2%},"
            f"{overall_nb_article},{overall_nb_clean_article},{overall_nb_clean_article / overall_nb_article:.2%},"
            f"{overall_nb_clean_article / overall_nb_pub:.2%}\n")

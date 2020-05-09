import pandas as pd


def upsert_author_df(new_entries_list, df=None):
    if df is None:
        df = pd.DataFrame(
            columns=[
                "name",
                "affiliation",
                "email",
                "paper_id",
                "paper_title",
                "paper_published_date",
                "num_publications",
            ]
        )

    for new in new_entries_list:

        if len(df[df["name"] == new["name"]].index) == 0:
            new.update({"num_publications": 1})
            df = df.append(pd.Series(new), ignore_index=True)
        elif len(df[df["name"] == new["name"]].index) == 1:
            row = df[df["name"] == new["name"]].index
            if new["affiliation"]:
                df.loc[row]["affiliation"] += "; " + new["affiliation"]
            for col in ["paper_id", "paper_title", "paper_published_date"]:
                df.loc[row][col] += "; " + new[col]
            df.loc[row]["num_publications"] += 1
        else:
            raise ValueError

    return df

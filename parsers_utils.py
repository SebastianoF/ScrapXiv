from pprint import pprint

import pandas as pd
import requests
import xmltodict


def get_paper_dict(index=0, query=None, max_result=10):

    query = ":" + query if query else ""
    a_url = f'http://export.arxiv.org/api/query?search_query=all{query}&start={index}&max_results={max_result}'
    r = requests.get(a_url)
    if int(r.status_code / 100) != 2:
        raise ValueError(f"Error {r.status_code} parsing data from url {a_url}")
    dd = xmltodict.parse(r.content)

    return dd


def paper_dict_to_author_list(paper_dict):
    output_authors = []
    
    entries = paper_dict.get("feed").get("entry")
    if entries is None:
        print("No entries found")
        return output_authors
    if not isinstance(entries, list):
        # there is a single paper in the query
        entries = [entries]

    for entry in entries:
        paper_id = entry.get("id")
        paper_title = entry.get("title").replace("\n", "").replace("  ", "").strip()
        paper_published_date = entry.get("published")

        authors = entry.get("author")
        if isinstance(authors, list):
            for au in authors:
                name = au.get("name")
                try:
                    affiliation = au.get("arxiv:affiliation").get("#text")
                except:
                    affiliation = ""
                output_authors.append(
                    dict(
                        name=name, 
                        affiliation=affiliation, 
                        paper_id=paper_id,
                        paper_title=paper_title, 
                        paper_published_date=paper_published_date
                    )
                )

        else:
            name = authors.get("name")
            try:
                affiliation = authors.get("arxiv:affiliation").get("#text")
            except:
                affiliation = ""
            output_authors.append(
                dict(
                    name=name, 
                    affiliation=affiliation, 
                    paper_id=paper_id,
                    paper_title=paper_title, 
                    paper_published_date=paper_published_date
                )
            )

    return output_authors


def add_new_entries_to_df(new_entries_list, df=None):
    if df is None:
        df = pd.DataFrame(columns=['name', 'affiliation', 'paper_id', 'paper_title', 'paper_published_date', 'num_publications'])

    for new in new_entries_list:
        
        if len(df[df['name'] == new['name']].index) == 0:
            new.update({'num_publications': 1})
            df = df.append(pd.Series(new), ignore_index=True)
        elif len(df[df['name'] == new['name']].index) == 1:
            row = df[df['name'] == new['name']].index
            if new['affiliation']:
                df.loc[row]['affiliation'] += '; ' + new['affiliation']
            for col in ['paper_id', 'paper_title', 'paper_published_date']:
                df.loc[row][col] += '; ' + new[col]
            df.loc[row]['num_publications'] += 1
        else: 
            raise ValueError

    return df

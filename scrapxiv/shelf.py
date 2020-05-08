from pprint import pprint

import pandas as pd
import requests
import xmltodict

from scrapxiv import pandas_utils
from scrapxiv import download
from scrapxiv import path_manager


class Shelf:
    def __init__(self):
        """
        Shelf data structure where the queried results are stored.
        Start with Shelf.query?
        """
        self.parsed_dict = None

    def query(self, keywords=None, index=1, max_result=10):
        """
        Fill the shelf with papers form arxiv API, with given keword, index and max number of papers found.
        To see the output type self.parsed_dict .
        """
        keywords = ":" + keywords if keywords else ""
        a_url = f'http://export.arxiv.org/api/query?search_query=all{keywords}&start={index}&max_results={max_result}'
        r = requests.get(a_url)
        if int(r.status_code / 100) != 2:
            raise ValueError(f"Error {r.status_code} parsing data from url {a_url}")
        dd = xmltodict.parse(r.content)

        self.parsed_dict = dd

    def papers_ids(self):
        if self.parsed_dict is None:
            print("No papers in the shelf. Get some papers with Shelf.query before.")
        output_papers_id = []
        
        entries = self.parsed_dict.get("feed").get("entry")
        if entries is None:
            print("No entries found")
            return []

        if not isinstance(entries, list):
            # there is a single paper in the query
            entries = [entries]

        for entry in entries:
            paper_id = entry.get("id")
            output_papers_id.append(paper_id)
        return output_papers_id

    def authors(self, as_dataframe=False):

        output_authors = []
        
        entries = self.parsed_dict.get("feed").get("entry")
        if entries is None:
            print("No entries found")
            return
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
        if as_dataframe:
            return pandas_utils.upsert_author_df(output_authors)
        else:
            return output_authors

    def download_papers(self, destination_folder=path_manager.folder_for_pdfs):
        download.papers_list(self.papers_ids)


    def authors_via_paper(self):
        pass
        
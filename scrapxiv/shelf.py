import os

import pdftotext
import requests
import xmltodict

from scrapxiv import download, pandas_utils, path_manager


def parse_authors_and_affiliation(authors: dict) -> list:
    names_affiliations = []
    if isinstance(authors, list):
        for au in authors:
            name = au.get("name")
            try:
                affiliation = au.get("arxiv:affiliation").get("#text")
            except:
                affiliation = ""
            names_affiliations.append((name, affiliation))

    else:
        name = authors.get("name")
        try:
            affiliation = au.get("arxiv:affiliation").get("#text")
        except:
            affiliation = ""
        names_affiliations.append((name, affiliation))

    return names_affiliations


def email_from_text_and_author(text, author_name):
    emails_in_the_first_page = [
        t for t in text.replace("\n", " ").split(" ") if "@" in t
    ]
    for n in [a for a in author_name.replace(".", "").split(" ") if len(a) > 2]:
        for e in emails_in_the_first_page:
            if n.lower().strip() in e:
                return e

    return ""


def pdf_path_to_text(path_to_pdf):
    if not os.path.exists(path_to_pdf):
        raise ValueError(f"Pdf not found in {path_to_pdf}.")
    with open(path_to_pdf, "rb") as f:
        try:
            text = pdftotext.PDF(f)
        except:
            print(f"Could not parse {path_to_pdf} to text")
            text = ""
    return text


class Shelf:
    def __init__(self, download_folder=None):
        """
        Shelf data structure where the queried results are stored.
        Start with Shelf.query?
        """
        self.parsed_dict = None
        self.download_folder = (
            download_folder if download_folder else path_manager.download_folder
        )

    def query(self, keywords=None, index=1, max_results=10):
        """
        Fill the shelf with papers form arxiv API, with given keword, index and max number of papers found.
        To see the output type self.parsed_dict.
        """
        keywords = ":" + keywords if keywords else ""
        a_url = f"http://export.arxiv.org/api/query?search_query=all{keywords}&start={index}&max_results={max_results}"
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

    def authors(self, as_dataframe=False, get_email=False):

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

            if get_email:
                paper_url, filename = download.paper(paper_id, self.download_folder)
                pdf_path = os.path.join(self.download_folder, filename)
                paper_text = pdf_path_to_text(pdf_path)

            for name, affiliation in parse_authors_and_affiliation(entry.get("author")):

                if get_email and paper_text:
                    email = email_from_text_and_author(paper_text[0], name)
                else:
                    email = ""

                output_authors.append(
                    dict(
                        name=name,
                        affiliation=affiliation,
                        email=email,
                        paper_id=paper_id,
                        paper_title=paper_title,
                        paper_published_date=paper_published_date,
                    )
                )

        if as_dataframe:
            return pandas_utils.upsert_author_df(output_authors)
        else:
            return output_authors

    def papers_info(self):

        output_info = dict()

        entries = self.parsed_dict.get("feed").get("entry")
        if entries is None:
            print("No entries found")
            return
        if not isinstance(entries, list):
            # there is a single paper in the query
            entries = [entries]

        for entry in entries:
            paper_id = entry.get("id").split("/")[-1]
            paper_title = entry.get("title").replace("\n", "").replace("  ", "").strip()
            paper_published_date = entry.get("published")
            authors = [a[0] for a in parse_authors_and_affiliation(entry.get("author"))]

            output_info.update(
                {
                    paper_id: {
                        "title": paper_title,
                        "date": paper_published_date,
                        "authors": authors,
                    }
                }
            )

        return output_info

    def download_papers(self, verbose=1):
        download.papers_from_list(
            self.papers_ids(),
            destination_folder=self.download_folder,
            keep_all_downloaded=True,
            verbose=verbose,
        )

    def fetch_texts(self):
        self.download_papers(verbose=0)
        texts = {}
        for pdf_file in [
            file for file in os.listdir(self.download_folder) if file.endswith("pdf")
        ]:
            pdf_path = os.path.join(self.download_folder, pdf_file)
            texts.update({pdf_file.replace(".pdf", ""): pdf_path_to_text(pdf_path)})
        return texts

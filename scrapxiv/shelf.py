import os
import glob
import concurrent.futures
import urllib.request

import time

import pdftotext
import requests
import xmltodict

from scrapxiv import pandas_utils, path_manager


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
                if "}" in e:
                    tail = e.split("}")[1]
                    heads = e.split("}")[0].replace("{", "").split(",")
                    for head in heads:
                        if n in head:
                            return head + tail
                        else:
                            return ""

                return e

    return ""


def pdf_path_to_text(path_to_pdf):
    if not os.path.exists(path_to_pdf):
        print(f"Pdf not found in {path_to_pdf}.")
        return ""
    with open(path_to_pdf, "rb") as f:
        try:
            text = pdftotext.PDF(f)
        except:
            print(f"Could not parse {path_to_pdf} to text.")
            text = ""
    return text


def _download_a_paper(paper_url, path_destination):
    try:
        with urllib.request.urlopen(paper_url, timeout=60) as conn:
            urllib.request.urlretrieve(paper_url, path_destination)
            print(f"Download paper {paper_url} finished.")
            return len(conn.read())  # number of bytes in downloaded image

    except urllib.error.HTTPError:
        print(f"Http can not retrieve the paper {paper_url}")
    except Exception as e:
        print(e)


class Shelf:
    def __init__(self, download_folder=None):
        """
        Shelf data structure where the queried results are stored.
        Start with Shelf.query?
        """
        self.papers = None
        self.download_folder = (
            download_folder if download_folder else path_manager.download_folder
        )

    def query(self, keywords=None, start_index=1, max_results=10):
        """
        Main method of the class, to fill the shelf with papers.
        Fill the shelf with papers form arxiv API, with given keword, index and max number of papers found.
        To see the output type self.papers.
        """
        keywords = ":" + keywords if keywords else ""
        a_url = f"http://export.arxiv.org/api/query?search_query=all{keywords}&start={start_index}&max_results={max_results}"
        r = requests.get(a_url)
        if int(r.status_code / 100) != 2:
            raise ValueError(f"Error {r.status_code} parsing data from url {a_url}")
        dd = xmltodict.parse(r.content)

        self.papers = dd

    def get_papers_ids(self):
        """
        Get the list of papers's ids from the shelf.
        If the paper url is 'http://arxiv.org/abs/1801.07883v2', the paper id is '1801.07883v2'.
        """
        if self.papers is None:
            print("No papers found in the shelf. Get the intended papers with `Shelf.query`.")
        output_papers_id = []

        entries = self.papers.get("feed").get("entry")
        if entries is None:
            print("No entries found")
            return []

        if not isinstance(entries, list):
            # there is a single paper in the query
            entries = [entries]

        for entry in entries:
            paper_id = entry.get("id").split('/')[-1]
            output_papers_id.append(paper_id)

        return output_papers_id

    def get_papers_info(self):

        output_info = dict()

        entries = self.papers.get("feed").get("entry")
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

    def download_papers(self, verbose=0):
        """ Idempotent function to download the data from the Shelf to the designated local folder """
        if not os.path.exists(self.download_folder):
            raise ValueError(f"Destination folder {self.download_folder} does not exists.")
        
        ids_already_have = [
            os.path.basename(file).replace('.pdf', '')
            for file in glob.glob(os.path.join(self.download_folder, '*.pdf'))
        ]

        ids_to_download = set(self.get_papers_ids()) - set(ids_already_have)

        list_urls = [f"http://arxiv.org/pdf/{i}.pdf" for i in ids_to_download]
        list_paths_destination = [
            os.path.join(self.download_folder, os.path.basename(url)) for url in list_urls
        ]

        if verbose > 0:
            print("Downloading papers (in multi-threading...)")

        total_bytes = 0
        parallel_time = seq_time = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(_download_a_paper, url, dest)
                for url, dest in zip(list_urls, list_paths_destination)
            ]
            for f in concurrent.futures.as_completed(futures):
                total_bytes += f.result() or 0

        if verbose > 0:
            print("\nPapers already in the download folder: ")
            for p in ids_already_have:
                print(p)
            print(f"\nApprox total bytes downloaded {total_bytes}")

    def clean_download_folder(self):
        """ Delete all the downloaded files in the destination folder"""
        files = glob.glob(os.path.join(self.download_folder, "*.pdf"))
        for f in files:
            os.remove(f)


    def get_authors_dataframe(self, get_emails=False):
        """ 
        Creates a dataframe with the authors list of the papers in the shelf.
        If get_email is True, the papers are downloaded and the first page is parsed.
        """

        if get_emails:
            self.download_papers(verbose=0)

        entries = self.papers.get("feed").get("entry")

        if entries is None:
            print("No entries found")
            return
        if not isinstance(entries, list):
            # there is a single paper in the query
            entries = [entries]
        
        output_authors = []

        for entry in entries:
            paper_id = entry.get("id").split('/')[-1]
            paper_title = entry.get("title").replace("\n", "").replace("  ", "").strip()
            paper_published_date = entry.get("published")

            if get_emails:
                
                pdf_path = os.path.join(self.download_folder, paper_id + '.pdf')
                paper_text = pdf_path_to_text(pdf_path)

            for name, affiliation in parse_authors_and_affiliation(entry.get("author")):

                if get_emails and paper_text:
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

        return pandas_utils.upsert_author_df(output_authors)

    def fetch_texts(self):
        self.download_papers(verbose=0)
        texts = {}
        for pdf_file in [
            file for file in os.listdir(self.download_folder) if file.endswith("pdf")
        ]:
            pdf_path = os.path.join(self.download_folder, pdf_file)
            texts.update({pdf_file.replace(".pdf", ""): pdf_path_to_text(pdf_path)})
        return texts

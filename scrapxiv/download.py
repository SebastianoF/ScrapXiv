import os
import urllib
import shutil

from scrapxiv.path_manager import here, folder_for_pdfs


def paper(paper_id, destination_folder, keep_all_downloaded=True, timeout_secs=10):
    if not os.path.exists(destination_folder):
        raise ValueError(f"Destination folder {destination_folder} does not exists.")

    already_have = set(os.listdir(destination_folder))

    paper_url = "{}.pdf".format(paper_id.replace('abs', 'pdf'))
    filename = os.path.basename(paper_url)
    destination_path = os.path.join(destination_folder, filename)

    if filename in already_have:
        print(f"paper {filename} already downloaded. Skipping!")
        return
    
    try:
        req = urllib.request.urlopen(paper_url, None, timeout_secs)
        with open(destination_path, 'wb') as f:
            shutil.copyfileobj(req, f)
    except Exception as e:
        raise Exception(f"Exception {e} raised downloading {paper_url}")
        
    else:
        print(f"Paper {paper_url} downloaded to {destination_path}.")


def papers_from_id(list_of_papers_id, destination_folder, keep_all_downloaded=True):

    for paper in list_of_papers_id:
        paper(paper, destination_folder, keep_all_downloaded=True)
# ScrapXiv: Arxiv scraper

Helper to scrape [Arxiv](arxiv.org).

## CLI example

To collect the names of the authors of the first 200 papers queried with the keyword "particle physics" and to save them in two separate .csv file, one for each batch, run:
```
scrapxiv authors --key-words "particle physics" --output-file ~/Desktop/papers1.csv --max 100 --start 1 --emails
scrapxiv authors --key-words "particle physics" --output-file ~/Desktop/papers2.csv --max 100 --start 100 --emails
```

## install

Clone the repo to a folder, cd to the cloned folder scrapxiv, then with a python 3.8 interpreter run:
```
pip install -e .
```
Installing in a virtualenv is recommended.

To prepare the environment for the library pdftotext you may need to:

```bash
sudo apt-get update
sudo apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev
```
beforehand if on Ubuntu or

```bash
export MACOSX_DEPLOYMENT_TARGET=10.9
```
if on MAC.

### Examples

Please check the `examples` folder for some basic usages.

### Resources

+ [Papers with code](https://medium.com/paperswithcode/a-home-for-results-in-ml-e25681c598dc)
+ [Arxiv sanity](http://www.arxiv-sanity.com/)


### Limitations
1. Not all the authors publishing on arxiv have added their affiliationa.
2. Authors on Arxiv do not come with a UID, which means that if the same author has signed 3 papers with "J. Smith", "John Smith" and "John A. Smith", these publications will be attributed to three different authors.
3. For the same reason as above, two different researchers called John Smith will be identified as a single researcher.
4. To subsample the papers, we allowed to add a query string when accessing the API.

### Licence

This repository is open-sourced under MIT licence.

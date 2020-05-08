# ScrapXiv: Arxiv parser

Parse "all" the authors name and affiliations to a google spreadsheet.

## Usage

```
scrapxiv --key-words "particle physics" --batch-size 10 --num-batches 3 --output-file ~/Desktop/papers.csv
```

## install

Clone the repo to a folder, cd to scrapxiv, then with a python 3.8 interpreter run:
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

### Results

See the file `parser.ipynb` for an initial example.

### WIP
+ Exploratory analysis of arxiv API and data in progress, to understand the limitations.
+ CLI to parse name + affiliations in a .csv file.
+ Connection to google spreadsheet is in progress.

### Limitations
1. Not all the authors publishing on arxiv have added their affiliation.
2. Authors on Arxiv do not come with a UID, which means that if the same author has signed 3 papers with "J. Smith", "John Smith" and "John A. Smith", these publications will be attributed to three different authors.
3. For the same reason as above, two different researchers called John Smith will be identified as a single researcher.
4. To subsample the papers, we allowed to add a query string when accessing the API.
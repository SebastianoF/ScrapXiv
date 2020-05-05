# Arxiv parser

Parse "all" the authors name and affiliations to a google spreadsheet.


### Results

See the file `parser.ipynb` for an initial example.

### WIP
+ Exploratory analysis of arxiv API and data in progress, to understand the limitations.
+ Connection to google spreadsheet is in progress.
+ Consideration towards a NoSQL DB to host the intermediate data structure, and to select the subset of data to send to google spreadsheet in progress.

### Limitations
1. Not all the authors publishing on arxiv have added their affiliation.
2. Authors on Arxiv do not come with a UID, which means that if the same author has signed 3 papers with "J. Smith", "John Smith" and "John A. Smith", these publications will be attributed to three different authors.
3. For the same reason as above, two different researchers called John Smith will be identified as a single researcher.
4. To subsample the papers, we allowed to add a query string when accessing the API.
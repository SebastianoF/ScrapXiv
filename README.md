# Arxiv parser

Parse "all" the authors name and affiliations to a google spreadsheet.



### Results

See the file `parser.ipynb` for an example about how to use.

### Limitations
1. Authors on Arxiv do not come with a UID, which means that if the same author has signed 3 papers with "J. Smith", "John Smith" and "John A. Smith", these publications will be attributed to three different authors.
2. For the same reason as above, two different researchers called John Smith will be identified as a single researcher.
3. To subsample the papers, we allowed to add a query string when accessing the API.
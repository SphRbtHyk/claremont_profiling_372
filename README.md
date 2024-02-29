# Results of the Claremont profiling for MS 372

Repository is organized as follows:

- data/ contains:
    - The XML transcription of MS_372 (`ms_372.xml`)
    - The list of Claremont readings and their alternative as a CSV file (`readings.csv`)
    - The manuscripts downloaded from NTVMR (`manuscripts.json`)
    - The values of the computed profiles (`profiles.csv`) and the evaluted readings (`readings.csv`)

- The py files `get_manuscripts.py` downloads the manuscripts from the NTVMR, the `get_claremont_rules.py` generates the Claremont profiling rules from the Wikipedia page, and the `compute_analysis.py` generates the profiles and analyzes the readings.
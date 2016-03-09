"""
    Convert thousand genomes samples csv (converted from excel)
    into json documents
    Headers:
    Sample,Family ID,Population,Population Description,Gender,
    Relationship,Unexpected Parent/Child ,Non Paternity,
    Siblings,Grandparents,Avuncular,Half Siblings,
    Unknown Second Order,Third Order,Other Comments
"""

import csv
import json
import datetime


def main():
    with open('20130606_sample_info.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            with open(
                    "biosamples/" + row['Sample'] + ".json", 'w') as outfile:
                description = "{} {} {}".format(
                    row['Population'],
                    row['Population Description'],
                    row['Gender'])
                biosample = {
                    "name": row['Sample'],
                    "description": description,
                    "disease": None,  # Ontology term
                    "createDateTime": datetime.datetime.now().isoformat(),
                    "updateDateTime": datetime.datetime.now().isoformat(),
                    "info": row
                }
                json.dump(biosample, outfile)

if __name__ == "__main__":
    main()

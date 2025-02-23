import pandas as pd
from pathlib import Path

def main():
    file_path = Path("BAWE.xls").resolve()

    bawe = pd.read_excel(file_path, sheet_name="Sheet1")
    topics = extract_topics_efcamdat(bawe)
    write_topics_to_file(topics)


def extract_topics_efcamdat(bawe):
    # Extract the topics from the BAWE database
    topics = bawe["title"].unique()
    return topics

def write_topics_to_file(topics):
    # Write the topics to a file
    with open("bawe_topics.txt", "w") as f:
        for topic in topics:
            f.write(topic + "\n")

if __name__ == "__main__":
    main()
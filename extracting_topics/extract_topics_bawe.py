import pandas as pd
from pathlib import Path

def main():
    file_path = Path("BAWE.xls").resolve()

    bawe = pd.read_excel(file_path, sheet_name="Sheet1")
    topics = extract_topics_bawe(bawe)
    essay_topics = extract_topics_essay_only_bawe(bawe)
    write_topics_to_file(topics, "bawe_topics.txt")
    write_topics_to_file(essay_topics, "bawe_essay_topics.txt")


def extract_topics_bawe(bawe):
    """Extract the topics from the BAWE database"""
    topics = bawe["title"].unique()
    return topics

def extract_topics_essay_only_bawe(bawe):
    """Extract the essay only topics from the BAWE database"""
    topics = bawe[bawe["genre family"] == "essay"]["title"].unique()
    return topics

def write_topics_to_file(topics, filename):
    with open(filename, "w") as f:
        for topic in topics:
            f.write(topic + "\n")

if __name__ == "__main__":
    main()
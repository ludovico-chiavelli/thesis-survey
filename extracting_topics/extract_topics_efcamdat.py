import pandas as pd
from pathlib import Path

def main():
    file_path = Path("Final database (main prompts).xlsx").resolve()

    efcd = pd.read_excel(file_path, sheet_name="Sheet 1")
    topics = extract_topics_efcamdat(efcd)
    write_topics_to_file(topics, "efcamdat_topics.txt")

    b1_and_above_topics = extract_b1_and_above_topics(efcd)
    write_topics_to_file(b1_and_above_topics, "b1_and_above_topics.txt")


def extract_topics_efcamdat(efcd):
    # Extract the topics from the EFCAMDAT database
    topics = efcd["topic"].unique()
    return topics

def extract_b1_and_above_topics(efcd):
    # Extract the B1 and above topics from the EFCAMDAT database
    topics = efcd[efcd["cefr_numeric"] >= 3]["topic"].unique()
    return topics

def write_topics_to_file(topics, filename):
    # Write the topics to a file
    with open(filename, "w") as f:
        for topic in topics:
            f.write(topic + "\n")

if __name__ == "__main__":
    main()
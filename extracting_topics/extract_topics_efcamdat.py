import pandas as pd
from pathlib import Path

def main():
    file_path = Path("Final database (main prompts).xlsx").resolve()

    efcd = pd.read_excel(file_path, sheet_name="Sheet 1")
    topics = extract_topics_efcamdat(efcd)
    write_topics_to_file(topics)


def extract_topics_efcamdat(efcd):
    # Extract the topics from the EFCAMDAT database
    topics = efcd["topic"].unique()
    return topics

def write_topics_to_file(topics):
    # Write the topics to a file
    with open("efcamdat_topics.txt", "w") as f:
        for topic in topics:
            f.write(topic + "\n")

if __name__ == "__main__":
    main()
# Check any LDNOOBW words are present in the final_corpus_survey_questions.txt
from pathlib import Path
curr_dir = Path(__file__).parent
with open(curr_dir / 'Human_Performance_Evaluation_Human_vs_AILLM_Generated_Text_Survey.qsf', 'r') as file:
    wordlist = [line.strip() for line in file.readlines()]
    with open('final_corpus_survey_questions.txt', 'r') as file:
        lines = file.readlines()
        for word in wordlist:
            for index, line in enumerate(lines):
                print("Checking index: ", index)
                if word in line.strip().split():
                    print(f"Found: {word} at index: {index}. Original line: {line}")
        print("Done checking LDNOOBW words in the file.")

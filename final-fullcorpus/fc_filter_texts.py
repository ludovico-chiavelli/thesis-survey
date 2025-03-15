from pathlib import Path
import pandas as pd
import tqdm

unfilterd_corpus = Path('/home/nuvolari/GitHub/thesis-llm-corpus/combine-partials/final_corpus.csv').resolve()
corpus_df = pd.read_csv(unfilterd_corpus, dtype=str)

wordlist_filepath = Path('/home/nuvolari/GitHub/thesis-survey/final-fullcorpus/LDNOOBW-en.txt').resolve()
with open(wordlist_filepath, 'r') as file:
    # Strip newline characters from the words.
    wordlist = [line.strip() for line in file.readlines()]

# Filter out texts with bad words in them.
indeces_to_drop = []
for index, row in tqdm.tqdm(corpus_df.iterrows(), total=corpus_df.shape[0]):
    if pd.notnull(row["MODEL_TEXT"]) and pd.notnull(row["HUMAN_TEXT"]):        
        for word in wordlist:
            human_text = row['HUMAN_TEXT'].lower()
            model_text = row['MODEL_TEXT'].lower()
            if word in human_text.split() or word in model_text.split():
                print(f"Found bad word {word} in text at index {index}. Dropping row.")
                indeces_to_drop.append(index)
                break
    else:
        print(f"Found empty text at index {index}. Dropping row.")
        indeces_to_drop.append(index)

for index in indeces_to_drop:
    corpus_df.drop(index, inplace=True)

# Save the filtered dataframe to a new file.
file_name = 'final_corpus_filtered_texts.csv'
corpus_df.to_csv(file_name, index=False)
print(f"Filtered corpus saved to {file}")
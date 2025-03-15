from pathlib import Path
import pandas as pd
import tqdm

unfilterd_corpus = Path('/home/nuvolari/GitHub/thesis-llm-corpus/combine-partials/final_corpus.csv').resolve()
corpus_df = pd.read_csv(unfilterd_corpus)

wordlist_filepath = Path('/home/nuvolari/GitHub/thesis-survey/final-fullcorpus/LDNOOBW-en.txt').resolve()
with open(wordlist_filepath, 'r') as file:
    # Strip newline characters from the words.
    wordlist = [line.strip() for line in file.readlines()]

# Filter out texts with bad words in them.
indeces_to_drop = []
for index, row in tqdm.tqdm(corpus_df.iterrows(), total=corpus_df.shape[0]):
    for word in wordlist:
        if word in row['HUMAN_TEXT'].lower().split() or word in row['MODEL_TEXT'].lower().split():
            print(f"Found bad word {word} in text at index {index}. Dropping row.")
            indeces_to_drop.append(index)
            break

for index in indeces_to_drop:
    corpus_df.drop(index, inplace=True)

# Save the filtered dataframe to a new file.
file_name = 'final_corpus_filtered_texts.csv'
corpus_df.to_csv(file_name, index=False)
print(f"Filtered corpus saved to {file}")
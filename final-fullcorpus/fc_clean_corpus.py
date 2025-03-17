## This file cleans the corpus by removing rows with empty MODEL_TEXT or HUMAN_TEXT columns.
## It also removes markup and html tags from the text.

from pathlib import Path
import pandas as pd
import re
import tqdm

unfilterd_corpus = Path('/home/nuvolari/GitHub/thesis-llm-corpus/combine-partials/final_corpus.csv').resolve()
corpus_df = pd.read_csv(unfilterd_corpus, dtype=str)

# Remove rows with empty MODEL_TEXT or HUMAN_TEXT columns.
corpus_df.dropna(subset=['MODEL_TEXT', 'HUMAN_TEXT'], inplace=True)

# Remove markup and html tags from the text.
corpus_df['MODEL_TEXT'] = corpus_df['MODEL_TEXT'].apply(lambda x: re.sub(r'<[^>]*>', '', x))
corpus_df['HUMAN_TEXT'] = corpus_df['HUMAN_TEXT'].apply(lambda x: re.sub(r'<[^>]*>', '', x))

# Remove The first sentence of MODEL_TEXT. If the text is at least 2 sentences long.
# This is done to remove an intrsuction sentence that is present in all texts due to model misbehaviour.

def remove_first_sentence(text):
    sentences = text.split('.')
    if len(sentences) > 1:
        return '.'.join(sentences[1:])
    else:
        return text

corpus_df['MODEL_TEXT'] = corpus_df['MODEL_TEXT'].apply(remove_first_sentence)

# Remove double asterisks from the text.
corpus_df['MODEL_TEXT'] = corpus_df['MODEL_TEXT'].apply(lambda x: x.replace('**', ''))
corpus_df['HUMAN_TEXT'] = corpus_df['HUMAN_TEXT'].apply(lambda x: x.replace('**', ''))

# Remove leading and trailing whitespace from the text.
corpus_df['MODEL_TEXT'] = corpus_df['MODEL_TEXT'].apply(lambda x: x.strip())
corpus_df['HUMAN_TEXT'] = corpus_df['HUMAN_TEXT'].apply(lambda x: x.strip())


# Save the cleaned dataframe to a new file.
file_name = 'final_corpus_cleaned_first_sentence_removed.csv'
corpus_df.to_csv(file_name, index=False)
print(f"Cleaned corpus saved to {file_name}")

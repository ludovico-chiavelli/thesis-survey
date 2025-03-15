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

# Save the cleaned dataframe to a new file.
file_name = 'final_corpus_cleaned.csv'
corpus_df.to_csv(file_name, index=False)
print(f"Cleaned corpus saved to {file_name}")

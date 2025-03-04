import pandas as pd
from pathlib import Path
from tqdm import tqdm

def main():
    
    llama_file = Path('corpus-partials/human_llm_corpus_with_generate_text_llama_full.csv').resolve()
    gemma_file = Path('corpus-partials/human_llm_corpus_with_generate_text_gemma_full.csv').resolve()
    mistral_file =Path('corpus-partials/human_llm_corpus_with_generate_text_mistral_full.csv').resolve()
    
    corpus_file = Path('llm_corpus.csv').resolve()
    human_text_file = Path('extracting_topics/Final database (main prompts).xlsx').resolve()
    bawe_excel = Path('extracting_topics/BAWE.xls').resolve()

    # zip_files(llama_file, gemma_file, mistral_file)
    # add_efcamdat_human_text(corpus_file, human_text_file)
    add_bawe_human_text(corpus_file, bawe_excel)

def zip_files(llam_file, gemma_file, mistral_file):
    pd_llam = pd.read_csv(llam_file)
    pd_gemma = pd.read_csv(gemma_file)
    pd_mistral = pd.read_csv(mistral_file)

    # Write all to one big file
    combined_df = pd.concat([pd_llam, pd_gemma, pd_mistral], ignore_index=True)
    combined_df.to_csv('llm_corpus.csv', index=False)


def add_efcamdat_human_text(corpus_path, human_text_path):
    pd_corpus = pd.read_csv(corpus_path)
    pd_efcamdat = pd.read_excel(human_text_path, sheet_name='Sheet 1')

    # For each row in the corpus, choose one random human text from the human text file with the same topic.
    for i, row in pd_corpus.iterrows():
        if row['CORPUS'] == 'EFCAMDAT':
            human_text = pd_efcamdat[pd_efcamdat['topic'] == row['TOPIC']].sample(1)['text_corrected'].values[0]
            pd_corpus.at[i, 'HUMAN_TEXT'] = human_text
    
    pd_corpus.to_csv('llm_corpus.csv', index=False)

def add_bawe_human_text(corpus_path, index_path):
    pd_corpus = pd.read_csv(corpus_path)
    pd_bawe = pd.read_excel(index_path, sheet_name='Sheet1')

    # Extract all BAWE topics in corpus file
    bawe_topics = pd_corpus[pd_corpus['CORPUS'] == 'BAWE']['TOPIC'].unique()

    # For each topic in in the BAWE topics, find the relevant file in the txt folder and extract the first 200 words.
    for topic in tqdm(bawe_topics):
        # Find the relevant file in pd_bawe
        relevant_file = pd_bawe[pd_bawe['title'] == topic]['id'].values[0]
        relevant_file_path = Path(f'CORPUS_TXT/{relevant_file}.txt').resolve()
        with open(relevant_file_path, 'r') as f:
            text = f.read()
            first_200_words = ' '.join(text.split()[:200])
            # Update the corpus file with the human text
            pd_corpus.loc[pd_corpus['TOPIC'] == topic, 'HUMAN_TEXT'] = first_200_words
    pd_corpus.to_csv('llm_corpus.csv', index=False)

if __name__ == '__main__':
    main()
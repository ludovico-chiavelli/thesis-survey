# This script generates a CSV file that will fill in the following categories:
# - CORPUS
# - TOPIC_ID
# - TOPIC
# - HUMAN_TEXT
# - PROMPT
# - LLAMA_TEXT
# - GEMMA_NAME
# - MISTRAL_TEXT

# In the thesis_llm repo, the additional category of LLM_NAME and generated text will be added to the CSV file, in their respective columns.

from pathlib import Path
import pandas as pd
import tqdm
import random

def main():
    # Load all B1 and above topics from EFCAMDAT and all essay topics from BAWE.
    extracting_topics_dir = Path(__file__).parent.parent / 'extracting_topics'
    ef_topics_file = Path(extracting_topics_dir / 'b1_and_above_topics.txt').resolve()
    bawe_topics_file = Path(extracting_topics_dir / 'bawe_essay_topics.txt').resolve()

    with open(ef_topics_file, 'r') as file:
        ef_topics = [line.strip() for line in file.readlines()]
    with open(bawe_topics_file, 'r') as file:
        bawe_topics = [line.strip() for line in file.readlines()]


    # These are the proompts for EFCAMDAT and BAWE topics.
    efcamdat_context = "You are an English learner.Your native language is not English. You are currently at B1 level."
    bawe_context = "You are a university student."

    efcamdat_topic_prompt_items = generate_topic_prompt_items(ef_topics, efcamdat_context, crps_name='EFCAMDAT')
    bawe_topic_prompt_items = generate_topic_prompt_items(bawe_topics, bawe_context, crps_name='BAWE')

    # Save prompts to a file for potential later use.
    with open('final_corpus_prompts.txt', 'w') as file:
        for item in efcamdat_topic_prompt_items:
            file.write(item['prompt_text'] + '\n')
        for prompt in bawe_topic_prompt_items:
            file.write(prompt['prompt_text'] + '\n')
    
    # Create final corpus pandas dataframe.
    corpus_df = pd.DataFrame(columns=['CORPUS', 'TOPIC_ID', 'TOPIC', 'HUMAN_TEXT', 'PROMPT', 'LLAMA_TEXT', 'GEMMA_TEXT', 'MISTRAL_TEXT'])
    
    # Add human text from efcamdat
    print('Opening EFCAMDAT corpus...')
    ef_corpus = Path('human-corpora/efcamdat.csv').resolve()
    efcd_df = pd.read_csv(ef_corpus)
    for item in tqdm.tqdm(efcamdat_topic_prompt_items):
        topic_human_texts = efcd_df[efcd_df['topic'] == item['topic']]['text_corrected'].values

        # Sample 10 random texts if there are more than 10 texts available
        if len(topic_human_texts) > 10:
            topic_human_texts = random.sample(list(topic_human_texts), 10)

        # Add all these text samples to the dataframe as a new entry with the same corpus, topic_id, topic, human_text and prompt
        for text in topic_human_texts:
            new_row_df = pd.DataFrame({'CORPUS': 'EFCAMDAT', 'TOPIC_ID': item['topic_id'], 'TOPIC': item['topic'], 'HUMAN_TEXT': text, 'PROMPT': item['prompt_text']}, index=[0])
            corpus_df = pd.concat([corpus_df, new_row_df], ignore_index=True)
    
    # Do the same for BAWE
    bawe_dir = Path(__file__).parent.parent / 'extracting_topics' 
    bawe_corpus = Path(bawe_dir / 'BAWE.xls').resolve()
    bawe_df = pd.read_excel(bawe_corpus, sheet_name='Sheet1')
    corpus_texts_dir = Path('human-corpora/BAWE_CORPUS_TXT').resolve()

    # Look for all corpus items IDs in the bawe_df and extract the first 200 words from each text file. Add them all to the dataframe.
    bawe_entries = []
    for item in tqdm.tqdm(bawe_topic_prompt_items):
        # Find the relevant files in the bawe_df
        relevant_files = bawe_df[bawe_df['title'] == item['topic']]['id'].values
        for file in relevant_files:
            relevant_file_path = Path(f'{corpus_texts_dir}/{file}.txt')
            with open(relevant_file_path, 'r') as f:
                text = f.read()
                first_200_words = ' '.join(text.split()[:200])
                bawe_entries.append({'CORPUS': 'BAWE', 'TOPIC_ID': item['topic_id'], 'TOPIC': item['topic'], 'HUMAN_TEXT': f'{first_200_words}...', 'PROMPT': item['prompt_text']})
    
    # Limit the amount of BAWE entries to match the amount of EFCAMDAT entries.
    bawe_entries = random.sample(bawe_entries, len(corpus_df))
    for entry in bawe_entries:
        new_row_df = pd.DataFrame(entry, index=[0])
        corpus_df = pd.concat([corpus_df, new_row_df], ignore_index=True)
    

    #### Save the final corpus to a CSV file.
    corpus_df.to_csv('final_corpus_unfiltered_hum_texts.csv', index=False)

def generate_topic_prompt_items(topics: list[str], context: str, crps_name: str) -> list[dict]:
    topic_prompt_items = []
    for index, topic in enumerate(topics):
        if crps_name == 'EFCAMDAT':
            prompt = f'{context} Write a piece of text on the topic: {topic}.'
            topic_prompt_items.append({'topic_id': f'EF_{index}', 'topic': topic, 'prompt_text': prompt})
        elif crps_name == 'BAWE':
            prompt = f'{context} Write an essay on the topic {topic}.'
            topic_prompt_items.append({'topic_id': f'BAWE_{index}', 'topic': topic, 'prompt_text': prompt})
    
    return topic_prompt_items


if __name__ == '__main__':
    main()
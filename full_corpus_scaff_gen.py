# This script generates a CSV file that will fill in the following categories:
# - CORPUS
# - TOPIC_ID
# - TOPIC
# - HUMAN_TEXT
# - PROMPT
# - LLM_NAME
# - LLM_TEXT_1
# - LLM_TEXT_2
# - LLM_TEXT_3

# In the thesis_llm repo, the additional category of LLM_NAME and generated text will be added to the CSV file, in their respective columns.

from pathlib import Path
import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description='Generate prompts and choose human text samples for EFCAMDAT and BAWE topics')
    parser.add_argument('--prompts_filename', type=str, default=False, required=False, help='Save the prompts to a file')
    args = parser.parse_args()

    ef_topics_file = Path('extracting_topics/b1_and_above_topics.txt').resolve()
    bawe_topics_file = Path('extracting_topics/bawe_essay_topics.txt').resolve()

    efcamdat_context = "You are an English learner.Your native language is not English. You are currently at B1 level."
    bawe_context = "You are a university student."

    efcamdat_topics = load_topics(ef_topics_file)
    bawe_topics = load_topics(bawe_topics_file)

    efcamdat_prompts = generate_prompts(efcamdat_topics, efcamdat_context, corpus='EFCAMDAT')
    # As opposed to the minicorpus this one will use all the essay topics from BAWE.
    bawe_prompts = generate_prompts(bawe_topics, bawe_context, corpus='BAWE')

    if args.prompts_filename:
        with open(args.prompts_filename, 'w') as file:
            for prompt in efcamdat_prompts:
                file.write(prompt['text'] + '\n')
            for prompt in bawe_prompts:
                file.write(prompt['text'] + '\n')
    
    with open('human_llm_fullcorpus_scaff.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['CORPUS', 'TOPIC_ID', 'TOPIC', 'HUMAN_TEXT', 'PROMPT', 'LLM_NAME', 'LLM_TEXT_1', 'LLM_TEXT_2', 'LLM_TEXT_3'])
        for prompt in efcamdat_prompts:
            # prompt and topic ID are the same.
            writer.writerow(['EFCAMDAT', prompt['prompt_id'], prompt['topic'], '', prompt['text'], '', '', '', ''])
        for prompt in bawe_prompts:
            writer.writerow(['BAWE', prompt['prompt_id'], prompt['topic'], '', prompt['text'], '', '', '', ''])

def generate_prompts(topics: list, context: str, corpus: str) -> list:
    prompts = []
    for topic in topics:
        if corpus == 'EFCAMDAT':
            prompt = f'{context} Write a piece of text on the topic: {topic["topic"]}.'
        elif corpus == 'BAWE':
            prompt = f'{context} Write an essay on the topic {topic["topic"]}.'
        prompts.append({'prompt_id': topic['topic_id'], 'topic': topic['topic'], 'text': prompt})
    
    return prompts

def load_topics(filename) -> list:
    topics = []
    with open(filename, 'r') as file:
        for i, line in enumerate(file):
            topics.append({'topic_id': i + 1, 'topic': line.strip()})
    return topics

if __name__ == '__main__':
    main()
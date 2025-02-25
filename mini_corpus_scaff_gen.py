# This script generates a CSV file that will fill in the following categories:
# - CORPUS
# - TOPIC
# - PROMPT
# - HUMAN_TEXT

# In the thesis_llm repo, the additional category of LLM_NAME and generated text will be added to the CSV file, in their respective columns.

from pathlib import Path
import argparse
import csv
import random

def main():
    parser = argparse.ArgumentParser(description='Generate prompts and choose human text samples for EFCAMDAT and BAWE topics')
    parser.add_argument('--save_prompts', default=False, required=False, help='Save the prompts to a file')
    args = parser.parse_args()

    ef_topics_file = Path('extracting_topics/b1_and_above_topics.txt').resolve()
    bawe_topics_file = Path('extracting_topics/bawe_topics.txt').resolve()

    efcamdat_context = "I want you to imagine you are an English learner from a non-English speaking country. You are currently at B2 level, assigned to do a writing task in English."
    bawe_context = "I want you to imagine you are a university level student in the UK. You have been given the task to write a text piece."

    efcamdat_topics = load_topics(ef_topics_file)
    bawe_topics = load_topics(bawe_topics_file)

    # Pick 72 random topics from bawe, as it has disproportionately more topics than efcamdat. This matches the amount in b1_and_above_topics.txt.
    random.seed(42)
    random_bawe_topics = random.sample(bawe_topics, 72)

    efcamdat_prompts = generate_prompts(efcamdat_topics, efcamdat_context)
    bawe_prompts = generate_prompts(random_bawe_topics, bawe_context)

    if args.save_prompts:
        with open(args.save_prompts, 'w') as file:
            for prompt in efcamdat_prompts:
                file.write(prompt['text'] + '\n')
            for prompt in bawe_prompts:
                file.write(prompt['text'] + '\n')
    
    with open('human_llm_corpus.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['CORPUS', 'TOPIC_ID', 'TOPIC', 'HUMAN_TEXT', 'PROMPT', 'LLM_NAME', 'LLM_GENERATED_TEXT'])
        for prompt in efcamdat_prompts:
            writer.writerow(['EFCAMDAT', prompt['prompt_id'], prompt['topic'], '', prompt['text'], '', '']) # prompt and topic ID are the same.
        for prompt in bawe_prompts:
            writer.writerow(['BAWE', prompt['prompt_id'], prompt['topic'], '', prompt['text'], '', ''])

def generate_prompts(topics: list, context: str) -> list:
    prompts = []
    for topic in topics:
        prompt = f'{context} Your topic is {topic["topic"]}. Please write a text piece on this topic.'
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
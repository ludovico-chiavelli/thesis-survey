# Qualtrics Survey Question Generator
# Create a Qualtrics survey with questions generated from the final corpus.
# This is meant to be a single survey project and then use randomization to present sets of 6 questions to each participant.


import pandas as pd
from pathlib import Path
import random
from typing import Tuple


def main():
    # print(form_rateq_item("This is a test text.", 1))
    # print(form_choiceq_item("This is a human text.", "This is an AI-generated text.", 1))

    # Load the final corpus.
    final_corpus_file = Path('/home/nuvolari/GitHub/thesis-llm-corpus/final_corpus_unf_texts_with_partials.csv').resolve()
    corpus_df = pd.read_csv(final_corpus_file, dtype=str)
    
    # temporary.Check for missing values and fill them with a default string if necessary
    corpus_df['LLAMA_TEXT'].fillna('Missing Text', inplace=True)
    corpus_df['GEMMA_TEXT'].fillna('Missing Text', inplace=True)
    corpus_df['MISTRAL_TEXT'].fillna('Missing Text', inplace=True)

    # Sample rate question pool.
    ef_rateq_pool, bawe_rateq_pool = sample_rateq_pool(corpus_df)

    # Sample choice question pool.
    ef_choiceq_pool, bawe_choiceq_pool = sample_choiceq_pool(corpus_df)

    # Form rate question items.
    rateq_items = []
    for i, text in enumerate(ef_rateq_pool):
        rateq_items.append(form_rateq_item(text, i, source_corp="EF"))
    for i, text in enumerate(bawe_rateq_pool):
        rateq_items.append(form_rateq_item(text, i, source_corp="BA"))

    # Form choice question items.
    choiceq_items = []
    for index, item in enumerate(ef_choiceq_pool):
        choiceq_items.append(form_choiceq_item(item[0], item[1], index, source_corp="EF"))
    for index, item in enumerate(ef_choiceq_pool):
        choiceq_items.append(form_choiceq_item(item[0], item[1], index, source_corp="BA"))
    
    # Save the items to a file. Each Rate and Choice items are in groups of 3 and 3 respectively within one block. So 1 block has 6 questions all separated by a pagebreak.
    with open('final_corpus_survey_questions.txt', 'w') as file:
        file.write("[[AdvancedFormat]]\n\n")
        for i in range(0, len(rateq_items) - 2, 3):
            block_num = int(i/3) + 1
            file.write(f"[[Block: Survey Set {block_num}]]\n\n")
            file.write(rateq_items[i] + "\n\n" + rateq_items[i+1] + "\n\n" + rateq_items[i+2] + "\n\n")
            file.write(choiceq_items[i] + "\n\n" + choiceq_items[i+1] + "\n\n" + choiceq_items[i+2] + "\n\n")
    

def sample_rateq_pool(corpus_df: pd.DataFrame) -> Tuple[list, list]:
    """
    Sample LLM text from the corpus for rate question pool.
    Even split between EFCAMDAT and BAWE. Even split between LLM models.
    """

    # Sample 36 LLM texts from the corpus. 18 from EFCAMDAT and 18 from BAWE. 6 from each LLM model.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT'].sample(n=18)
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE'].sample(n=18)

    # Sample 6 texts from each LLM model for EFCAMDAT entries.
    ef_llama_entries = ef_rows["LLAMA_TEXT"].sample(n=6)
    ef_gemma_entries = ef_rows["GEMMA_TEXT"].sample(n=6)
    ef_mistral_entries = ef_rows["MISTRAL_TEXT"].sample(n=6)

    # Sample 6 texts from each LLM model for BAWE entries.
    bawe_llama_entries = bawe_rows["LLAMA_TEXT"].sample(n=6)
    bawe_gemma_entries = bawe_rows["GEMMA_TEXT"].sample(n=6)
    bawe_mistral_entries = bawe_rows["MISTRAL_TEXT"].sample(n=6)

    # Convert to list. Combine all ef entries into one list.
    ef_entries = list(ef_llama_entries) + list(ef_gemma_entries) + list(ef_mistral_entries)

    # Combine all bawe entries into one list.
    bawe_entries = list(bawe_llama_entries) + list(bawe_gemma_entries) + list(bawe_mistral_entries)

    return ef_entries, bawe_entries




def sample_choiceq_pool(corpus_df: pd.DataFrame) -> Tuple[list[Tuple[str, str]], list[Tuple[str, str]]]:
    """
    Sample LLM text from the corpus for choice question pool.
    Even split between EFCAMDAT and BAWE. Even split between LLM models.
    """

    # Sample 36 human-LLM text pairs from the corpus. 18 from EFCAMDAT and 18 from BAWE. 6 from each LLM model.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT'].sample(n=18)
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE'].sample(n=18)

    # Sample 6 human and LLM text pairs from each LLM model for EFCAMDAT entries.
    ef_llama_entries = ef_rows[["HUMAN_TEXT", "LLAMA_TEXT"]].sample(n=6)
    ef_gemma_entries = ef_rows[["HUMAN_TEXT", "GEMMA_TEXT"]].sample(n=6)
    ef_mistral_entries = ef_rows[["HUMAN_TEXT", "MISTRAL_TEXT"]].sample(n=6)

    # Sample 6 human and LLM text pairs from each LLM model for BAWE entries.
    bawe_llama_entries = bawe_rows[["HUMAN_TEXT", "LLAMA_TEXT"]].sample(n=6)
    bawe_gemma_entries = bawe_rows[["HUMAN_TEXT", "GEMMA_TEXT"]].sample(n=6)
    bawe_mistral_entries = bawe_rows[["HUMAN_TEXT", "MISTRAL_TEXT"]].sample(n=6)

    # Combine all ef entries into one list. Make a list of tuples with (human_text, llama_text) pairs.
    ef_entries = []
    bawe_entries = []
    for index, row in ef_llama_entries.iterrows():
        ef_entries.append((row["HUMAN_TEXT"], row["LLAMA_TEXT"]))
        bawe_entries.append((row["HUMAN_TEXT"], row["LLAMA_TEXT"]))
    for index, row in ef_gemma_entries.iterrows():
        ef_entries.append((row["HUMAN_TEXT"], row["GEMMA_TEXT"]))
        bawe_entries.append((row["HUMAN_TEXT"], row["GEMMA_TEXT"]))
    for index, row in ef_mistral_entries.iterrows():
        ef_entries.append((row["HUMAN_TEXT"], row["MISTRAL_TEXT"]))
        bawe_entries.append((row["HUMAN_TEXT"], row["MISTRAL_TEXT"]))
    

    return ef_entries, bawe_entries

def form_rateq_item(llm_text: str, index: int, source_corp: str) -> str:
    """
    Form a rate question item from an LLM text.
    """

    # Form the rate question item.

    # Form question texts.
    itemq_rate = f"Rate the text between 1 (definitely AI generated) and 4 (definitely human generated).\n\n\"{llm_text}\""
    itemq_why = f"Why does the text sound more or less human-like? Please write at least one sentence. Any and all reasoning is useful."
    itemq_rewrite = f'Please rewrite the text so that it sounds more human-like, if you rated it anything below "4 - Definitely human". You may copy and paste the text and then make your edits.'

    composition = f"""
[[Question:MC:SingleAnswer:Horizontal]]
[[ID: Rate{source_corp}{index}]]
{itemq_rate}
[[Choices]]
1 - Definitely AI
2 - Likely AI
3 - Likely human
4 - Definitely human

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Rate{source_corp}{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Rate{source_corp}{index}rewrite]]
{itemq_rewrite}

[[PageBreak]]
"""

    return composition

def form_choiceq_item(human_text: str, llm_text: str, index: int, source_corp: str) -> str:
    """
    Form a choice question item from a human-LLM text pair.
    """

    # Shuffle the order of the texts.
    options = [human_text, llm_text]
    opt1 = random.choice(options)
    options.remove(opt1)
    opt2 = options[0]

    # Form the choice question item.

    # Form question texts.
    itemq_choice = f"Pick which text sounds more AI-generated."
    itemq_why = f"Why does the text option you chose sound more or less human-like? Please write at least one sentence. Any and all reasoning is useful."
    itemq_rewrite = f"Please rewrite the text you chose as AI-generated so that it sounds more human-like. You may copy and paste your answer from below (the radio buttons cannot be highlighted):"

    composition = f"""
[[Question:MC:SingleAnswer:Vertical]]
[[ID: Choice{source_corp}{index}]]
{itemq_choice}
[[Choices]]
choice 1 - {opt1}
choice 2 - {opt2}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Choice{source_corp}{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Choice{source_corp}{index}rewrite]]
{itemq_rewrite}


- {opt1}

- {opt2}

[[PageBreak]]
"""

    return composition


if __name__ == '__main__':
    main()
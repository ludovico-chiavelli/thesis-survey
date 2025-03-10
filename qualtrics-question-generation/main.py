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
    final_corpus_file = Path('/home/nuvolari/GitHub/thesis-survey/final-fullcorpus/final_corpus.csv').resolve()
    corpus_df = pd.read_csv(final_corpus_file)
    # Temporary, only select rows that have LLM text for LLAMA, GEMMA, MISTRAL
    corpus_df = corpus_df.dropna(subset=['LLAMA_TEXT', 'GEMMA_TEXT', 'MISTRAL_TEXT'])

    # Sample rate question pool.
    ef_rateq_pool, bawe_rateq_pool = sample_rateq_pool(corpus_df)

    # Sample choice question pool.
    ef_choiceq_pool, bawe_choiceq_pool = sample_choiceq_pool(corpus_df)

    # Form rate question items.
    rateq_items = []
    for i, text in enumerate(list(ef_rateq_pool)):
        rateq_items.append(form_rateq_item(text, i))
    for i, text in enumerate(list(bawe_rateq_pool)):
        rateq_items.append(form_rateq_item(text, i))

    # Form choice question items.
    choiceq_items = []
    for index, row in ef_choiceq_pool.iterrows():
        choiceq_items.append(form_choiceq_item(row["HUMAN_TEXT"], row["LLAMA_TEXT"], index))
    for index, row in bawe_choiceq_pool.iterrows():
        choiceq_items.append(form_choiceq_item(row["HUMAN_TEXT"], row["LLAMA_TEXT"], index))
    
    # Save the items to a file. Each Rate and Choice items are in groups of 3 and 3 respectively within one block. So 1 block has 6 questions all separated by a pagebreak.
    with open('final_corpus_questions.txt', 'w') as file:
        file.write("[[AdvancedFormat]]\n\n")
        for i in range(6):
            file.write(f"[[Block: Survey Set {i}]]\n\n")
            # this only works because len(rateq_items) is a multiple of 3
            file.write(rateq_items[i*3] + "\n\n" + rateq_items[i*3+1] + "\n\n" + rateq_items[i*3+2] + "\n\n")
            file.write(choiceq_items[i*3] + "\n\n" + choiceq_items[i*3+1] + "\n\n" + choiceq_items[i*3+2] + "\n\n")
    

def sample_rateq_pool(corpus_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
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

    # Combine all ef entries into one list.
    ef_entries = ef_llama_entries + ef_gemma_entries + ef_mistral_entries

    # Combine all bawe entries into one list.
    bawe_entries = bawe_llama_entries + bawe_gemma_entries + bawe_mistral_entries

    return ef_entries, bawe_entries




def sample_choiceq_pool(corpus_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
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

    # Combine all ef entries into one list.
    ef_entries = ef_llama_entries + ef_gemma_entries + ef_mistral_entries

    # Combine all bawe entries into one list.
    bawe_entries = bawe_llama_entries + bawe_gemma_entries + bawe_mistral_entries

    return ef_entries, bawe_entries

def form_rateq_item(llm_text: str, index: int) -> str:
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
[[ID: Rate{index}]]
{itemq_rate}
[[Choices]]
choice 1 - Definitely AI
choice 2 - Likely AI
choice 3 - Likely human
choice 4 - Definitely human

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Rate{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Rate{index}rewrite]]
{itemq_rewrite}

[[PageBreak]]
"""

    return composition

def form_choiceq_item(human_text: str, llm_text: str, index: int) -> str:
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
[[ID: Choice{index}]]
{itemq_choice}
[[Choices]]
choice 1 - {opt1}
choice 2 - {opt2}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Choice{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:TE:Essay]]
[[ID: Choice{index}rewrite]]
{itemq_rewrite}

- {opt1}

- {opt2}

[[PageBreak]]
"""

    return composition


if __name__ == '__main__':
    main()
# Qualtrics Survey Question Generator
# Create a Qualtrics survey with questions generated from the final corpus.
# This is meant to be a single survey project and then use randomization to present sets of 6 questions to each participant.


import pandas as pd
from pathlib import Path
import random
from typing import Tuple

mn_to_fn = {
        "llama": "meta-llama/Llama-3.1-8B-Instruct",
        "gemma": "google/gemma-2-9b-it",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3"
}


def main():
    # Set the seed for reproducibility
    random.seed(24)
    # print(form_rateq_item("This is a test text.", 1))
    # print(form_choiceq_item("This is a human text.", "This is an AI-generated text.", 1))

    # Load the final corpus.
    final_corpus_file = Path('/home/nuvolari/GitHub/thesis-survey/final-fullcorpus/final_corpus_cleaned_first_sentence_removed.csv').resolve()
    corpus_df = pd.read_csv(final_corpus_file, dtype=str)
    
    # # temporary.Check for missing values and fill them with a default string if necessary
    # corpus_df['LLAMA_TEXT'].fillna('Missing Text', inplace=True)
    # corpus_df['GEMMA_TEXT'].fillna('Missing Text', inplace=True)
    # corpus_df['MISTRAL_TEXT'].fillna('Missing Text', inplace=True)

    # Fixed indeces to select the same texts for all participants. These are taken from the final_corpus by hand, at my discretion.
    # If viewing excel, remember that the row numbers are 0-indexed and that when loading a csv the header is not counted as a row. 
    # So add 2 to the row number in the csv to get the row number in the excel file.
    # Currently not in use.
    # rateq_indeces = {
    #     "ef_llama_entries": [0, 1, 2],
    #     "ef_gemma_entries": [],
    #     "ef_mistral_entries": [],
    #     "ba_llama_entries": [],
    #     "ba_gemma_entries": [],
    #     "ba_mistral_entries": []
    # }

    # choiceq_indeces = {
    #     "ef_llama_entries": [],
    #     "ef_gemma_entries": [],
    #     "ef_mistral_entries": [],
    #     "ba_llama_entries": [],
    #     "ba_gemma_entries": [],
    #     "ba_mistral_entries": []
    # }

    # Sample rate question pool.
    ef_rateq_pool, bawe_rateq_pool = sample_rateq_pool(corpus_df, seed=random.randint(0, 10))

    # Sample choice question pool.
    ef_choiceq_pool, bawe_choiceq_pool = sample_choiceq_pool(corpus_df, seed=random.randint(0, 10))

    # Form rate question items.
    rateq_items = []
    for i in range(len(ef_rateq_pool)): # ef_rateq_pool is same length as bawe_rateq_pool
        rateq_items.append(form_rateq_item(ef_rateq_pool[i], i, source_corp="EF"))
        rateq_items.append(form_rateq_item(bawe_rateq_pool[i], i, source_corp="BA"))

    # Form choice question items.
    choiceq_items = []
    for i in range(len(ef_choiceq_pool)): # ef_choiceq_pool is same length as bawe_choiceq_pool
        choiceq_items.append(form_choiceq_item(ef_choiceq_pool[i][0], ef_choiceq_pool[i][1], i, source_corp="EF"))
        choiceq_items.append(form_choiceq_item(bawe_choiceq_pool[i][0], bawe_choiceq_pool[i][1], i, source_corp="BA"))
    
    # Save the items to a file. Each Rate and Choice items are in groups of 3 and 3 respectively within one block. So 1 block has 6 questions all separated by a pagebreak.
    with open('final_corpus_survey_questions.txt', 'w') as file:
        file.write("[[AdvancedFormat]]\n\n")
        for i in range(0, len(rateq_items) - 2, 3):
            block_num = int(i/3) + 1
            file.write(f"[[Block: Survey Set {block_num}]]\n\n")
            file.write(rateq_items[i] + "\n\n" + rateq_items[i+1] + "\n\n" + rateq_items[i+2] + "\n\n")
            file.write(choiceq_items[i] + "\n\n" + choiceq_items[i+1] + "\n\n" + choiceq_items[i+2] + "\n\n")
    
    # Save the items to individual files.
    for i in range(0, len(rateq_items) - 2, 3):
        with open(f'final_corpus_survey_questions_{int(i/3) + 1}.txt', 'w') as file:
            file.write("[[AdvancedFormat]]\n\n")
            block_num = int(i/3) + 1
            file.write(f"[[Block: Survey Set {block_num}]]\n\n")
            file.write(rateq_items[i] + "\n\n" + rateq_items[i+1] + "\n\n" + rateq_items[i+2] + "\n\n")
            file.write(choiceq_items[i] + "\n\n" + choiceq_items[i+1] + "\n\n" + choiceq_items[i+2] + "\n\n")

def sample_rateq_pool(corpus_df: pd.DataFrame, seed: int) -> Tuple[list, list]:
    """
    Sample LLM text from the corpus for rate question pool.
    Even split between EFCAMDAT and BAWE. Even split between LLM models.
    """

    # Sample 36 LLM texts from the corpus. 18 from EFCAMDAT and 18 from BAWE. 6 from each LLM model.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT']
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE']

    # Sample 6 texts from each LLM model for EFCAMDAT entries. Use column MODEL_NAME to get the LLM text.
    ef_llama_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["llama"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()
    ef_gemma_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["gemma"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()
    ef_mistral_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["mistral"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()

    # Sample 6 texts from each LLM model for BAWE entries. Use column MODEL_NAME to get the LLM text.
    bawe_llama_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["llama"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()
    bawe_gemma_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["gemma"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()
    bawe_mistral_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["mistral"]]["MODEL_TEXT"].sample(n=6, random_state=seed, replace=False).tolist()

    # Combine all ef entries into one list.
    ef_entries = ef_llama_entries + ef_gemma_entries + ef_mistral_entries

    # Combine all bawe entries into one list.
    bawe_entries = bawe_llama_entries + bawe_gemma_entries + bawe_mistral_entries

    return ef_entries, bawe_entries


def sample_choiceq_pool(corpus_df: pd.DataFrame, seed: int) -> Tuple[list[Tuple[str, str]], list[Tuple[str, str]]]:
    """
    Sample LLM text from the corpus for choice question pool.
    Even split between EFCAMDAT and BAWE. Even split between LLM models.
    """

    # Sample 36 human-LLM text pairs from the corpus. 18 from EFCAMDAT and 18 from BAWE. 6 from each LLM model.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT']
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE']

    # Sample 6 human and LLM text pairs from each LLM model for EFCAMDAT entries. Use column MODEL_NAME to get the LLM text.
    ef_llama_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["llama"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)
    ef_gemma_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["gemma"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)
    ef_mistral_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["mistral"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)

    # Sample 6 human and LLM text pairs from each LLM model for BAWE entries. Use column MODEL_NAME to get the LLM text.
    bawe_llama_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["llama"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)
    bawe_gemma_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["gemma"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)
    bawe_mistral_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["mistral"]][["HUMAN_TEXT", "MODEL_TEXT"]].sample(n=6, random_state=seed, replace=False)

    # Combine all ef entries into one list. Make a list of tuples with (human_text, llama_text) pairs.
    ef_model_entries = [ef_llama_entries, ef_gemma_entries, ef_mistral_entries]
    bawe_model_entries = [bawe_llama_entries, bawe_gemma_entries, bawe_mistral_entries]

    ef_entries = []
    bawe_entries = []

    for model_entries in ef_model_entries:
        for index, row in model_entries.iterrows():
            ef_entries.append((row["HUMAN_TEXT"], row["MODEL_TEXT"]))
    for model_entries in bawe_model_entries:
        for index, row in model_entries.iterrows():
            bawe_entries.append((row["HUMAN_TEXT"], row["MODEL_TEXT"]))

    return ef_entries, bawe_entries

def form_rateq_item(llm_text: str, index: int, source_corp: str) -> str:
    """
    Form a rate question item from an LLM text.
    """

    # Clean llm_text. Only first 88 words are used.
    llm_text = llm_text.strip().replace("\n", " ")
    llm_text = " ".join(llm_text.split()[:88]) + "..."

    # Form the rate question item.

    # Form question texts.
    # the new line characters don't affect import. Just make the txt file more readable.
    itemq_rate = f"Rate the text between 1 (definitely AI generated) and 4 (definitely human generated)."
    itemq_why = f"Why does the text sound more or less human-like? Please write at least one sentence. Any and all reasoning is useful."
    itemq_rewrite = f'Please rewrite the text so that it sounds more human-like, if you rated it anything below "4 - Definitely human". You may copy and paste the text and then make your edits.'

    composition = f"""
[[Question:DB]]
[[ID: Read{source_corp}{index}]]
Read the text below.

[[Question:DB]]
[[ID: Rate{source_corp}{index}ratetext]]
"{llm_text}"

[[Question:MC:SingleAnswer:Horizontal]]
[[ID: Rate{source_corp}{index}]]
{itemq_rate}
[[Choices]]
1 - Definitely AI
2 - Likely AI
3 - Likely human
4 - Definitely human

[[PageBreak]]

[[Question:DB]]
[[ID: Rate{source_corp}{index}whytext]]
"{llm_text}"

[[Question:TE:Essay]]
[[ID: Rate{source_corp}{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:DB]]
[[ID: Rate{source_corp}{index}rwtext]]
"{llm_text}"

[[Question:TE:Essay]]
[[ID: Rate{source_corp}{index}rewrite]]
{itemq_rewrite}

[[PageBreak]]"""

    return composition

def form_choiceq_item(human_text: str, llm_text: str, index: int, source_corp: str) -> str:
    """
    Form a choice question item from a human-LLM text pair.
    """

    # Clean llm_text. Only first 56 words are used.
    llm_text = llm_text.strip().replace("\n", " ").replace('"', "")
    llm_text = " ".join(llm_text.split()[:56]) + "..."

    # Clean human_text. Only first 56 words are used, if it even reaches that amount.
    human_text = human_text.strip().replace("\n", " ")
    max_len = min(56, len(human_text.split()))
    human_text = " ".join(human_text.split()[:max_len]) + "..."

    # Shuffle the order of the texts.
    options = [human_text, llm_text]
    opt1 = random.choice(options)
    options.remove(opt1)
    opt2 = options[0]

    # Form the choice question item.

    # Form question texts.
    itemq_choice = f"Pick which text sounds more AI-generated."
    itemq_why = f"Why does the text option you chose sound more or less human-like? Please write at least one sentence. Any and all reasoning is useful."
    itemq_rewrite = f"Please rewrite the text you chose as AI-generated so that it sounds more human-like. You may copy and paste your answer from the text above (make sure you pick the correct one)"

    composition = f"""
[[Question:MC:SingleAnswer:Vertical]]
[[ID: Choice{source_corp}{index}]]
{itemq_choice}
[[Choices]]
1) "{opt1}"
2) "{opt2}"

[[PageBreak]]

[[Question:DB]]
[[ID: Choice{source_corp}{index}opt1whytext]]
Text 1: "{opt1}"

[[Question:DB]]
[[ID: Choice{source_corp}{index}opt2whytext]]
Text 2: "{opt2}"

[[Question:TE:Essay]]
[[ID: Choice{source_corp}{index}why]]
{itemq_why}

[[PageBreak]]

[[Question:DB]]
[[ID: Choice{source_corp}{index}opt1rwtext]]
Text 1: "{opt1}"

[[Question:DB]]
[[ID: Choice{source_corp}{index}opt2rwtext]]
Text 2: "{opt2}"

[[Question:TE:Essay]]
[[ID: Choice{source_corp}{index}rewrite]]
{itemq_rewrite}

[[PageBreak]]"""

    return composition

def select_rateq_pool(corpus_df: pd.DataFrame, indices: list) -> Tuple[list, list]:
    """
    Select LLM text from the corpus for rate question pool based on provided indices.
    """

    # Select texts from the corpus based on provided indices.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT']
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE']

    # Select texts from each LLM model for EFCAMDAT entries using provided indices.
    ef_llama_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["llama"]].iloc[indices]["MODEL_TEXT"].tolist()
    ef_gemma_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["gemma"]].iloc[indices]["MODEL_TEXT"].tolist()
    ef_mistral_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["mistral"]].iloc[indices]["MODEL_TEXT"].tolist()

    # Select texts from each LLM model for BAWE entries using provided indices.
    bawe_llama_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["llama"]].iloc[indices]["MODEL_TEXT"].tolist()
    bawe_gemma_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["gemma"]].iloc[indices]["MODEL_TEXT"].tolist()
    bawe_mistral_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["mistral"]].iloc[indices]["MODEL_TEXT"].tolist()

    # Combine all ef entries into one list.
    ef_entries = ef_llama_entries + ef_gemma_entries + ef_mistral_entries

    # Combine all bawe entries into one list.
    bawe_entries = bawe_llama_entries + bawe_gemma_entries + bawe_mistral_entries

    return ef_entries, bawe_entries


def select_choiceq_pool(corpus_df: pd.DataFrame, indices: list) -> Tuple[list[Tuple[str, str]], list[Tuple[str, str]]]:
    """
    Select LLM text from the corpus for choice question pool based on provided indices.
    """

    # Select human-LLM text pairs from the corpus based on provided indices.
    ef_rows = corpus_df[corpus_df['CORPUS'] == 'EFCAMDAT']
    bawe_rows = corpus_df[corpus_df['CORPUS'] == 'BAWE']

    # Select human and LLM text pairs from each LLM model for EFCAMDAT entries using provided indices.
    ef_llama_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["llama"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]
    ef_gemma_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["gemma"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]
    ef_mistral_entries = ef_rows[ef_rows["MODEL_NAME"] == mn_to_fn["mistral"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]

    # Select human and LLM text pairs from each LLM model for BAWE entries using provided indices.
    bawe_llama_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["llama"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]
    bawe_gemma_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["gemma"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]
    bawe_mistral_entries = bawe_rows[bawe_rows["MODEL_NAME"] == mn_to_fn["mistral"]].iloc[indices][["HUMAN_TEXT", "MODEL_TEXT"]]

    # Combine all ef entries into one list. Make a list of tuples with (human_text, llama_text) pairs.
    ef_model_entries = [ef_llama_entries, ef_gemma_entries, ef_mistral_entries]
    bawe_model_entries = [bawe_llama_entries, bawe_gemma_entries, bawe_mistral_entries]

    ef_entries = []
    bawe_entries = []

    for model_entries in ef_model_entries:
        for index, row in model_entries.iterrows():
            ef_entries.append((row["HUMAN_TEXT"], row["MODEL_TEXT"]))
    for model_entries in bawe_model_entries:
        for index, row in model_entries.iterrows():
            bawe_entries.append((row["HUMAN_TEXT"], row["MODEL_TEXT"]))

    return ef_entries, bawe_entries


if __name__ == '__main__':
    main()
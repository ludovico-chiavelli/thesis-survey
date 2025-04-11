from pathlib import Path
import pandas as pd
from utils import count_ngrams, normalize_text, plot_ngram_bargraph, make_wordcloud_plot

from difflib import SequenceMatcher

def main():
    current_dir = Path(__file__).resolve().parent
    responses_dir = current_dir / Path("../survey-set-responses").resolve()
    ### Create survey set dataframes dict
    ss_dict = {}
    for i in range(1, 13):
        filepath = responses_dir / Path(f"survey_set_{i}.csv")
        
        # Add respective survey set to dictionary
        ss_dict[f"survey_set_{i}"] = pd.read_csv(filepath)
    

    all_text_dict = {}
    regex_mask = r"(Rate|Choice)(EF|BA)\d+rewrite$"
    for ss_name, df in ss_dict.items():
        # Skip the first 2 rows, as they are metadata
        df = df.iloc[2:]
        
        # Get the "rewrite" type questions by selecting the columns that contain "rewrite" in their names
        rewriteq_rows = df.filter(regex=regex_mask)

        for col in rewriteq_rows.columns:
            # Get the text from the "rewrite" type questions
            rewriteq_answers = rewriteq_rows[col].values.flatten()
            # Convert to a list and remove NaN values
            all_text_dict[col] = {}
            all_text_dict[col]["answers"] = [str(answer) for answer in rewriteq_answers if pd.notna(answer)]

    # Because not all participants answering the "rewrite" question actually rewrotwe the text,
    # we need to filter out between "rewrite" and "free form" text.
    # This is done by checking the similarity and length between the two texts and if they are within a certain threshold.

    # We'll need the single RateQ and ChoiceQ DFs created in thesis-detector repo
    project_dir = Path(__file__).parents[1]
    # thesis-detector and thesis-survey sit adjacent to each other
    rateq_csv_path = project_dir / Path("main-file") / Path("survey_set_rateq_main_df.csv")
    rateq_df = pd.read_csv(rateq_csv_path)

    choiceq_csv_path = project_dir / Path("main-file") / Path("survey_set_choiceq_main_df.csv")
    choiceq_df = pd.read_csv(choiceq_csv_path)

    for rewrite_q in all_text_dict.keys():
        # If the rewrite question is for a RateQ, get the corresponding LLM text from rateq_df.
        # Then check the similarity between the rewrite text and the LLM text.
        if "Rate" in rewrite_q:
            # Trim the rewrite question to get the question ID
            search_text = rewrite_q.replace("rewrite", "")
            # Select the corresponding LLM text from the rateq_df
            q_text = rateq_df[rateq_df['question_id'] == search_text]['LLM_text'].values[0]
            all_text_dict[rewrite_q]["reference_text"] = q_text
        else:
            # Trim the rewrite question to get the question ID
            search_text = rewrite_q.replace("rewrite", "")
            # Select the corresponding LLM text from the choiceq_df
            q_text = choiceq_df[choiceq_df['question_id'] == search_text]['chosen_text'].values[0]
            all_text_dict[rewrite_q]["reference_text"] = q_text
    
    # Separate into actual rewrites and non-rewrites
    rewrite_responses = []
    non_rewrite_responses = []

    for rewrite_q, text_dict in all_text_dict.items():
        # Get the rewrite answers and reference text
        reference_text = text_dict["reference_text"]
        rewrite_answers = text_dict["answers"]

        # Check if the rewrite answer is actually rewriting or something else (e.g. instructions on how to rewrite)
        for rewrite_answer in rewrite_answers:
            if determine_if_rewrite(reference_text, rewrite_answer):
                rewrite_responses.append(rewrite_answer)
            else:
                non_rewrite_responses.append(rewrite_answer)
    
    print(f"Number of rewrite answers: {len(rewrite_responses)}")
    print(f"Number of non-rewrite answers: {len(non_rewrite_responses)}")

        



def determine_if_rewrite(question_text: str, rewrite_answer: str) -> bool:
    """
    Determine if the rewrite answer is actually rewriting or something else (e.g. instructions on how to rewrite)
    
    Args:
        question_text (str): The original question text.
        rewrite_answer (str): The rewrite answer text.
    Returns:
        bool: True if the rewrite answer is actually rewriting, False otherwise.
    """

    # Normalize the text
    question_text = normalize_text(question_text, lowercase=True, remove_stopwords=False, remove_punct=False)
    rewrite_answer = normalize_text(rewrite_answer, lowercase=True, remove_stopwords=False, remove_punct=False)
    # Remove any leading or trailing whitespace
    question_text = question_text.strip()
    rewrite_answer = rewrite_answer.strip()
    # Remove newline characters
    question_text = question_text.replace("\n", " ")
    rewrite_answer = rewrite_answer.replace("\n", " ")
    
    # Calculate length diff based on the number of words
    length_diff = abs(len(question_text.split()) - len(rewrite_answer.split())) / len(question_text)
    
    # Calculate similarity ratio
    similarity_ratio = SequenceMatcher(None, question_text, rewrite_answer).ratio()

    if length_diff < 0.5 and similarity_ratio > 0.5:
        return True
    else:
        return False
    

if __name__ == "__main__":
    main()
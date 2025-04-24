from pathlib import Path
import pandas as pd
from utils import count_ngrams, normalize_text, plot_ngram_bargraph, make_wordcloud_plot

from difflib import SequenceMatcher, unified_diff, HtmlDiff

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
    rewrite_responses = {}
    non_rewrite_responses = {}

    for rewrite_q, text_dict in all_text_dict.items():
        rewrite_responses[rewrite_q] = {
            "reference_text": text_dict["reference_text"],
            "rewrite_answer": []
        }
        non_rewrite_responses[rewrite_q] = {
            "reference_text": text_dict["reference_text"],
            "rewrite_answer": []
        }

    for rewrite_q, text_dict in all_text_dict.items():
        # Get the rewrite answers and reference text
        reference_text = text_dict["reference_text"]
        rewrite_answers = text_dict["answers"]

        # Check if the rewrite answer is actually rewriting or something else (e.g. instructions on how to rewrite)
        for rewrite_answer in rewrite_answers:
            if determine_if_rewrite(reference_text, rewrite_answer):
                rewrite_responses[rewrite_q]["rewrite_answer"].append(rewrite_answer)
            else:
                non_rewrite_responses[rewrite_q]["rewrite_answer"].append(rewrite_answer)
    

    # Count tri and bi-grams for all non-rewrite answers
    all_text = " ".join([text for text_dict in non_rewrite_responses.values() for text in text_dict["rewrite_answer"]])

    output_dir = Path("rewriteq-analysis-output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Normalize the text
    all_text = normalize_text(all_text, lowercase=True, remove_stopwords=True, remove_punct=True)
    ##### For loop to count n-grams #####
    for i in [2, 3]:
        # Count n-grams
        n_gram_counts = count_ngrams(all_text, i)
        # Sort by frequency
        sorted_n_grams = sorted(n_gram_counts.items(), key=lambda item: item[1], reverse=True)
        # Save the most common n-grams to a CSV file
        pd.DataFrame(sorted_n_grams, columns=["n-gram", "count"]).to_csv(output_dir / f"{i}_grams.csv", index=False)
        # Save the plot of the n-grams
        plot_ngram_bargraph(pd.DataFrame(sorted_n_grams, columns=["n-gram", "count"]).head(10), i, output_dir)
    
    ############## Word cloud ##############
    make_wordcloud_plot(all_text, output_dir)

    ############## Direct comparison of rewrite answers ##############
    # Save results to file
    output_dir = Path("rewriteq-analysis-output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for rewrite_q, text_dict in rewrite_responses.items():
        # Get the rewrite answers and reference text
        reference_text = text_dict["reference_text"]
        rewrite_answers = text_dict["rewrite_answer"]

        for rewrite_answer in rewrite_answers:
            # Save the diff to a file
            d = HtmlDiff()
            diff = d.make_file(reference_text.splitlines(), rewrite_answer.splitlines(), fromdesc="Reference Text", todesc="Rewrite Answer", context=True, numlines=0)
            with open(output_dir / f"{rewrite_q}_diff.html", "w", encoding="utf-8") as f:
                f.write(diff)
                    

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
    # length_diff = abs(len(question_text.split()) - len(rewrite_answer.split())) / len(question_text)

    # Alternative to length diff pergentage, we can use a fixed amount of words as a threshold
    len_rewrite_answer = len(rewrite_answer.split())
    length_threshold = 10
    
    # Calculate similarity ratio
    similarity_ratio = SequenceMatcher(None, question_text, rewrite_answer).ratio()

    if len_rewrite_answer > length_threshold and similarity_ratio > 0.1:
        return True
    else:
        return False
    
def direct_compare(original_text: str, response_text: str) -> list:
    """
    Compare two texts directly, and show unified diff if they are different.

    Args:
        original_text (str): The original text.
        response_text (str): The response text.
    Returns:
        diff (list): A list of differences between the two texts.
    """
    # Compare the two texts
    diff = unified_diff(original_text.splitlines(), response_text.splitlines(), lineterm='', fromfile='original', tofile='response')

    return diff
    

    

if __name__ == "__main__":
    main()
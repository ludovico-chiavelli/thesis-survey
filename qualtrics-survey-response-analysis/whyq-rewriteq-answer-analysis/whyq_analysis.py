import pandas as pd
from pathlib import Path

from utils import count_ngrams, normalize_text, plot_ngram_bargraph, make_wordcloud_plot

def main():
    current_dir = Path(__file__).resolve().parent
    responses_dir = current_dir / Path("../survey-set-responses").resolve()
    ### Create survey set dataframes dict
    ss_dict = {}
    for i in range(1, 13):
        filepath = responses_dir / Path(f"survey_set_{i}.csv")
        
        # Add respective survey set to dictionary
        ss_dict[f"survey_set_{i}"] = pd.read_csv(filepath)
    
    # Count tri and bi-grams for the entire survey by combining the texts of all "why" type questions

    all_text = []
    regex_mask = r"(Rate|Choice)(EF|BA)\d+why$"
    for ss_name, df in ss_dict.items():
        # Skip the first 2 rows, as they are metadata
        df = df.iloc[2:]
        # Get the "why" type questions by selecting the columns that contain "why" in their names
        whyq_answers = df.filter(regex=regex_mask).values.flatten()
        # Convert to a list and remove NaN values
        all_text.extend([str(answer) for answer in whyq_answers if pd.notna(answer)])
    
    # Combine all text into a single string
    combined_text = " ".join(all_text)

    # Normalize the text
    combined_text = normalize_text(combined_text, lowercase=True, remove_stopwords=True, remove_punct=True)


    output_dir = current_dir / Path("whyq-analysis-output")
    output_dir.mkdir(parents=True, exist_ok=True)

    ##### For loop to count n-grams #####
    for i in range(1, 5):
        # Count n-grams
        n_gram_counts = count_ngrams(combined_text, i)
        # Sort by frequency
        sorted_n_grams = sorted(n_gram_counts.items(), key=lambda item: item[1], reverse=True)
        # Save the most common n-grams to a CSV file
        pd.DataFrame(sorted_n_grams, columns=["n-gram", "count"]).to_csv(output_dir / f"{i}_grams.csv", index=False)
        # Save the plot of the n-grams
        plot_ngram_bargraph(pd.DataFrame(sorted_n_grams, columns=["n-gram", "count"]).head(10), i, output_dir)

    ############## Word cloud ##############
    # Filter out not useful words based on observations
    # Create a list of words to filter out
    filter_words = ["human", "ai", "use", "sound", "sounds"]
    # Filter the combined text
    filtered_text = " ".join([word for word in combined_text.split() if word not in filter_words])

    # Create a word cloud from the combined text
    
    make_wordcloud_plot(filtered_text, output_dir)


if __name__ == "__main__":
    main()

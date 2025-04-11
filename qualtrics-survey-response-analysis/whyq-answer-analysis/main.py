import pandas as pd
from pathlib import Path
from collections import Counter
from nltk import ngrams
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud

plt.rcParams.update({'font.size': 12})

nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])
stops = nlp.Defaults.stop_words
# Add custom stop words
stops.add("text") # The participants refer to their choice with "text" frequently
stops.add("1") # The participants refer to their choice with "1" frequently
stops.add("2") # The participants refer to their choice with "2" frequently

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


    output_dir = current_dir / Path("output")
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
    
    make_wordcloud_plot(filtered_text)



def count_ngrams(text: str, n: int) -> dict:
    """
    Count n-grams in a given text.
    
    Args:
        text (str): The input text.
        n (int): The size of the n-grams.
        
    Returns:
        dict: A dictionary with n-grams as keys and their counts as values.
    """

    # Tokenize the text
    tokens = text.split()
    
    # Generate n-grams
    n_grams = ngrams(tokens, n)
    
    # Count n-grams
    n_gram_counts = Counter(n_grams)
    
    return dict(n_gram_counts)

def normalize_text(text: str, lowercase: bool, remove_stopwords: bool, remove_punct: bool) -> str:
    """
    Normalize text using SpaCy. This lowercases, lemmatizes, and removes stop words.
    Args:
        text (str): The input text. Inspired by https://stackoverflow.com/a/49248776/13940304
    Returns:
        str: The normalized text.
    """

    if lowercase:
        text = text.lower()
    
    doc = nlp(text)
    processed = list()

    for token in doc:
        if remove_punct and token.is_punct or token.text == "-":
            continue
        lemma = token.lemma_.strip()
        if lemma:
            if not remove_stopwords or (remove_stopwords and lemma not in stops):
                processed.append(lemma)
    
    return " ".join(processed)
    
def plot_ngram_bargraph(ngram_df: pd.DataFrame, n: int, output_dir: Path):
    """
    Plot a bar graph of n-grams.
    
    Args:
        ngram_df (pd.DataFrame): DataFrame containing n-grams and their counts.
        n (int): The size of the n-grams.
        output_dir (Path): Directory to save the plot.
    """
    
    # Create a bar graph
    plt.figure(figsize=(10, 10))
    plt.bar(ngram_df["n-gram"].astype(str), ngram_df["count"])
    plt.xlabel(f"{n}-grams")
    plt.ylabel("Frequency")
    plt.title(f"Top {n}-grams")
    plt.xticks(rotation=90)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_dir / f"{n}_grams_bargraph.png")
    plt.close()

def make_wordcloud_plot(text: str):
    """
    Create a word cloud from the text.
    
    Args:
        text (str): The input text.
    """
    
    # Create a word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # Display the word cloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    
    # Save the plot
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "wordcloud.png")
    plt.close()

if __name__ == "__main__":
    main()

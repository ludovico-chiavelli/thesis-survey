import pandas as pd
from collections import Counter
from nltk import ngrams
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud

from pathlib import Path

plt.rcParams.update({'font.size': 12})

nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])
stops = nlp.Defaults.stop_words
# Add custom stop words
stops.add("text") # The participants refer to their choice with "text" frequently
stops.add("1") # The participants refer to their choice with "1" frequently
stops.add("2") # The participants refer to their choice with "2" frequently


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
    Normalize text using SpaCy. This lowercases, lemmatizes, and removes stop words or punctuation.

    Args:
        text (str): The input text.
        lowercase (bool): Whether to convert text to lowercase.
        remove_stopwords (bool): Whether to remove stop words.
        remove_punct (bool): Whether to remove punctuation.

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

def make_wordcloud_plot(text: str, output_dir: Path):
    """
    Create a word cloud from the text.
    
    Args:
        text (str): The input text.
        output_dir (Path): Directory to save the word cloud plot.
    Returns:
        None
    """
    
    # Create a word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # Display the word cloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    
    # Save the plot
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "wordcloud.png")
    plt.close()
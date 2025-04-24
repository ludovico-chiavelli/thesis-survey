## Prerequisites
Before doing anything verify you have the BAWE text files, download the BAWE corpus separately (not indexed by the repo as it's quite large) go and download it from [here](https://llds.ling-phil.ox.ac.uk/llds/xmlui/handle/20.500.14106/2539#). Once downloaded copy the files from the unzipped folder `2539\download\CORPUS_TXT` into `thesis-survey/final-fullcorpus/human-corpora/BAWE_CORPUS_TXT`. Yous should have a long list of txt files starting with `0001a.txt`.

Verify that you also have the `human-corpora/efcamdat.csv`. These files would be included in the code zip file as part of the submission, but if you're reading this from GitHub, you'll have to obtain this file yourself by requesting permission [here](https://ef-lab.mmll.cam.ac.uk/EFCAMDAT.html), to obtain the CSV.

## Instructions for running

In this folder:
1. Run `python fc_clean_corpus.py` first, this will create `final_corpus_cleaned_first_sentence_removed.csv`
2. Run `python fc_filter_text.py` this will create `final_corpus_filtered_texts.csv`

# Explanation of relevant  files

The below files are used before the corpus is generated in `thesis-llm-corpus`
- `final_corpus_scaff_gen.py` Generates the `final_corpus_unfiltered_hum_texts.csv`
- `final_corpus_unfiltered_hum_texts.csv` is copied to `thesis-llm-corpus` repo as the base CSV file, to generate the LLM texts

The below files are used after `thesis-llm-corpus` has generated its output:
- `final_corpus_cleaned_first_sentence_removed.csv` is the first intermediate step after running `python fc_clean_corpus.py` and cleans up some formatting artifacts
- `final_corpus_filtered_texts.csv` is the file meant to be used in generating the survey questions, as it doesn't contain any bad words. Its created by `python fc_filter_text.py`

Other
- `LDNOOBW-en.txt` is used by `fc_filter_text.py` to filter out bad words
- `final_corpus_prompts.txt` byproduct of `final_corpus_scaff_gen.py` for checking prompt texts.
# thesis-survey

This repo is part of a group of three repositories for my thesis.

The purpose of this one is to process survey creation-related files.

## Steps for using

1. You'll use `extracting_topics/extract_topics_bawe.py` and `extracting_topics/extract_topics_efcamdat.py` to extract the topics from the respective corpora.

2. In `final-fullcorpus` the outputs of the previous step are used by `final-fullcorpus/final_corpus_scaff_gen.py` to create `final-fullcorpus/final_corpus_unfiltered_hum_texts.csv`. This is the relevant file that interests us for then proceeding in the `thesis-llm-corpus` repo to create our final corpus with human and LLM text.

3. Then you'll use `qualtrics-question-generation/main.py` to generate the questions to be uploaded into qualtrics. The question pool is split into 12 "subsurveys", with 6 questions each, and need to be uploaded individually, otherwise qualtrics times out. These are the relevant files, other files i the folder are byproducts used to verify the behaviour of `qualtrics-question-generation/main.py`. `qualtrics-question-generation/LDNOOBW-checker.py` can be run to ensure that no bad words made it into the survey just as a double check.

4. Once you have survey results, follow the steps in `qualtrics-survey-response-analysis/README.md` to analyse the data.
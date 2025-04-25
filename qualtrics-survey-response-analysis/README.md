# Analyzing survey responses

## Relevant files and folders

- `survey_response.csv` results download from Qualtrics.
- `survey_scoring.py` correct answers for Choice-type questions. Rate are all AI generated.
- `generate_ss_CSVs.py` diviides `survey_response.csv` into the 12 original subsurveys.
- `analysis.py` this is the main file of interest. This plots the overall view of the scores.
- `main-file` this creates a "main" responses file, for processing in the third repo `thesis-detector`.
- `whyq-rewriteq-answer-analysis` contains analysis for rewrite and why-questions from the survey.

## How to run

1. `Use `python analysis.py` to generate plots.

2. `cd whyq-rewriteq-answer-analysis` and run `python whyq_analysis.py` for generating bi and trigram analysis.
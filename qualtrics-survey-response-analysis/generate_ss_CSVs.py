import pandas as pd
from pathlib import Path

def generate_ss_csvs(filepath: str, output_dir: str):
    """
    Generate CSV files for each unique value survey set (1-12) of the input CSV file with all survey responses.

    Args:
        filepath (str): Path to the input CSV file.
        output_dir (str): Directory where the output CSV files will be saved.
    """

    # Read the input CSV file
    responses_df = pd.read_csv(filepath)

    # Each survey set has a unique set of questions and survey sets are mutually exclusive.
    # So checking the first question of each survey set to determine the survey set number.

    first_question_names = ["RateEF0", "RateBA1", "RateEF3", "RateBA4", "RateEF6", "RateBA7", "RateEF9", "RateBA10", "RateEF12", "RateBA13", "RateEF15", "RateBA16"]
    # Create a dictionary to map the first question name to the survey set number
    survey_set_map = {
        "RateEF0": 1,
        "RateBA1": 2,
        "RateEF3": 3,
        "RateBA4": 4,
        "RateEF6": 5,
        "RateBA7": 6,
        "RateEF9": 7,
        "RateBA10": 8,
        "RateEF12": 9,
        "RateBA13": 10,
        "RateEF15": 11,
        "RateBA16": 12
    }

    # Create a directory for the output CSV files if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Iterate over each unique survey set number, and select all the rows for that have a response in the matching column
    for first_question in first_question_names:
        # Get the survey set number from the map
        survey_set_number = survey_set_map[first_question]

        # Select all the rows for that survey set
        survey_set_df = responses_df[responses_df[first_question].notna()]

        # Select the next 18 columns (each item has 3 questions, so 3 * 6 = 18)
        # Get the column index of the first question
        first_question_index = responses_df.columns.get_loc(first_question)
        # Select the next 18 columns
        survey_set_df = survey_set_df.iloc[:, first_question_index:first_question_index + 18]
        
        # Add the first 17 columns from responses. These contain metadata and demographic information. Select only the rows that exist in the survey set
        # Get the metadata columns (the first 17 columns)
        metadata_columns = responses_df.columns[:17]
        # Get score column
        score_column = responses_df["SC0"].str.strip()
        # Add the score column to the DataFrame
        survey_set_df = responses_df[metadata_columns].join(survey_set_df, how='inner').join(score_column, how='inner')


        
        # Print the number of rows in each survey set
        print(f"Survey set {survey_set_number} has {len(survey_set_df)} responses.")

        # Save the survey set DataFrame to a CSV file
        output_filepath = Path(output_dir) / f"survey_set_{survey_set_number}.csv"
        survey_set_df.to_csv(output_filepath, index=False)
        print(f"Generated CSV for survey set {survey_set_number}: {output_filepath}")

if __name__ == "__main__":
    curr_dir = Path(__file__).parent.resolve()
    input_filepath = curr_dir  / Path("survey_responses.csv")
    output_directory = curr_dir  / Path("survey-set-responses")
    generate_ss_csvs(input_filepath, output_directory)


import pandas as pd
from pathlib import Path

def calculate_average_score(ss_list: dict[pd.DataFrame]) -> float:
    """
    Calculate the average score for a list of DataFrames.

    Args:
        ss_list (list[pd.DataFrame]): List of DataFrames containing survey set responses."
    Returns:
        float: The average score across all DataFrames.
    """

    total_score = 0
    total_count = 0

    for df in ss_list.values():
        # Skip the first 2 rows of each DataFrame. This is where header=None is important.
        df = df.iloc[2:, :]

        # The score column is called "SC0". As these are in text format, they need to be converted to float.
        # Select the score column
        score_column = df["SC0"]
        # Remove any leading or trailing whitespace
        score_column = score_column.str.strip()

        # Convert the score column to numeric, forcing errors to NaN
        score_column = pd.to_numeric(score_column, errors='coerce')
        total_score += score_column.sum()
        total_count += score_column.count()

    if total_count == 0:
        return 0.0

    return total_score / total_count

def calculate_rate_type_q_score(ss_list: dict[pd.DataFrame], mask: str) -> float:
    """
    Calculate the average score for rate type questions in a list of DataFrames. Allows for masking of specific columns (EF or BA)

    Args:
        ss_list (list[pd.DataFrame]): List of DataFrames containing survey set responses."
    Returns:
        float: The average score across all DataFrames.
    """
    total_score = 0
    total_count = 0

    for name, df in ss_list.items():
        # print(f"Processing survey set: {name}")
        # Skip the first 2 rows of each DataFrame.
        df = df.iloc[2:, :]

        # Select only the columns that match the mask
        # This will select all columns that contain the mask string

        # For example, if mask = "EF", this will select all columns that contain "EF"
        # If mask = "BA", this will select all columns that contain "BA"
        # If mask = "Rate", this will select all columns that contain "Rate"

        filtered_df = df.filter(regex=mask)

        # Add the score column to the DataFrame
        filtered_df = filtered_df.assign(SC0=df["SC0"].str.strip())

        # Filter rows with no missing values in the filtered DataFrame
        filtered_df = filtered_df.dropna()

        # For rate types, we'll verify if the answer is either "1 - Definitely AI" or "2 - Likely AI". 
        # In the survey one of these answers gets 1 point exclusively (you can only get 1 point for this question).

        # Iterate over the columns of each row
        for index, row in filtered_df.iterrows():
            # Check if the rate column is either "1 - Definitely AI" or "2 - Likely AI"
            response_row_score = 0
            for _, value in row.items():
                if value == "1 - Definitely AI" or value == "2 - Likely AI":
                    # Add 1 to the score
                    response_row_score += 1
            # Add the score to the total score
            total_score += response_row_score
            # Add 1 to the total count
            total_count += 1

    # If there are no valid scores, return 0

    if total_count == 0:
        return 0.0
    return total_score / total_count



    

    

if __name__ == "__main__":
    
    curr_dir = Path(__file__).parent.resolve()
    responses_dir = curr_dir / Path("survey-set-responses")
    
    # Calculate the average score across all survey sets
    ss_list = {}
    for i in range(1, 13):
        filepath = responses_dir / Path(f"survey_set_{i}.csv")
        
        # Add respective survey set to dictionary
        ss_list[f"survey_set_{i}"] = pd.read_csv(filepath)

    average_score = calculate_average_score(ss_list)
    print(f"The average score across all survey sets is: {average_score}. Max score is 6.")

    #### Calculate the average score for the following categories: ####
    # Only Rate-type questions
    # Only Choice-type questions

    # Only rate BA questions
    # Only rate EF questions

    # Only choice BA questions
    # Only choice EF questions
    
    # Only BAWE (AKA BA) corpus questions
    # Only EFCAMDAT (AKA EF) corpus questions

    ##################

    # Create a df with all the results

    results_df = pd.DataFrame(columns=["Rate Only", "Choice Only", "BA Only", "EF Only", "Rate BA", "Rate EF", "Choice BA", "Choice EF"])

    # Calculate the average score for Rate-type questions
    mask = r"Rate(EF|BA)\d+$"
    rate_only_score = calculate_rate_type_q_score(ss_list, mask)
    percentage_rate_only_score = rate_only_score / 3 * 100
    print(f"The average score for rate type questions is: {percentage_rate_only_score}%. Max score is 3.")


    # Calculate the average score for Rate-type questions, sourced from BA
    mask = r"RateBA\d+$"
    rate_ba_score = calculate_rate_type_q_score(ss_list, mask)
    percentage_rate_ba_score = rate_ba_score / 3 * 100
    print(f"The average score for rate BA questions is: {percentage_rate_ba_score}%. Max score is 3.")

    # Calculate the average score for Rate-type questions, sourced from EF
    mask = r"RateEF\d+$"
    rate_ef_score = calculate_rate_type_q_score(ss_list, mask)
    percentage_rate_ef_score = rate_ef_score / 3 * 100
    print(f"The average score for rate EF questions is: {percentage_rate_ef_score}%. Max score is 3.")
    
    
    
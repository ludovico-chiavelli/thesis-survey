import pandas as pd
from pathlib import Path
from survey_scoring import correct_choiceq_answers
from statistics import mean

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

def calculate_rate_or_choice_q_score_average(ss_list: dict[pd.DataFrame], mask: str, mode: str) -> float:
    """
    Calculate the average score for rate type questions in a list of DataFrames. Allows for masking of specific columns (EF or BA)

    Args:
        ss_list (list[pd.DataFrame]): List of survey set DataFrames."
    Returns:
        float: The average score across all DataFrames.
    """
    total_score = 0
    total_count = 0

    for _, df in ss_list.items():
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
            if mode == "Rate":
                # Add the score to the total score
                total_score += response_row_score
            elif mode == "Choice":
                # The choice score can be calculated by taking the total score for the response
                # and subtracting the rate score

                total_response_score = int(row["SC0"])
                total_score += total_response_score - response_row_score
            
            if mask == r"RateBA\d+$" or r"RateEF\d+$" ==  mask:
                # As the amount of RateBA and RateEF alternates between 1 and 2 in the survey sets
                # this elif statement is necessary so we can calculate the average score for BA and EF questions
                # We'll add the total amount of BA or EF columns filtered to the count instead, so the maximum score becomes 1
                total_count += len(filtered_df.columns) - 1 # -1 because we have the SC0 column
            elif mode == "Rate" or mode == "Choice":    
                # Add 1 to the total count
                total_count += 1

    # If there are no valid scores, return 0

    if total_count == 0:
        return 0.0
    return total_score / total_count

def calculate_choice_q_score_average(ss_list: dict[pd.DataFrame], mask: str) -> float:
    """
    Similar to calculate_rate_or_choice_q_score_average, but for choice questions and uses a correct_choiceq_answers dict.
    """
    total_score = 0
    total_count = 0

    for name, df in ss_list.items():
        # print(f"Processing survey set: {name}")
        # Skip the first 2 rows of each DataFrame.
        df = df.iloc[2:, :]

        # For example, if mask = "ChoiceEF", this will select all columns that contain "ChoiceEF"
        # If mask = "ChoiceBA", this will select all columns that contain "ChoiceBA"

        filtered_df = df.filter(regex=mask)

        for index, row in filtered_df.iterrows():
            # Check if the column contains the correct answer for that question

            response_row_score = 0
            for col_name, value in row.items():
                if value == correct_choiceq_answers[col_name]:
                    response_row_score += 1
                total_count += len(filtered_df.columns) # we are counting average score per question, not response.
            # Add the score to the total score
            total_score += response_row_score
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
    rate_only_score = calculate_rate_or_choice_q_score_average(ss_list, mask, mode="Rate")
    percentage_rate_only_score = rate_only_score / 3 * 100
    print(f"The average score for rate type questions is: {percentage_rate_only_score}%. Max score is 3.")

    # Calculate the average score for Rate-type questions, sourced from BA
    mask = r"RateBA\d+$"
    rate_ba_score = calculate_rate_or_choice_q_score_average(ss_list, mask, mode="Rate")
    print(f"The average score for rate BA questions is: {rate_ba_score}. Max score is 1.")

    # Calculate the average score for Rate-type questions, sourced from EF
    mask = r"RateEF\d+$"
    rate_ef_score = calculate_rate_or_choice_q_score_average(ss_list, mask, mode="Rate")
    print(f"The average score for rate EF questions is: {rate_ef_score}. Max score is 1.")
    
    # Calculate the average score for Choice-type questions
    mask = r"Rate(EF|BA)\d+$" # For mode "Choice", we have to select any Rate question in the response.
    choice_only_score = calculate_rate_or_choice_q_score_average(ss_list, mask, mode="Choice")
    percentage_choice_only_score = choice_only_score / 3 * 100
    print(f"The average score for choice type questions is: {percentage_choice_only_score}%. Max score is 3.")

    # Calculate the average score for Choice-type questions, sourced from BA
    mask = r"ChoiceBA\d+$"
    choice_ba_score = calculate_choice_q_score_average(ss_list, mask)
    print(f"The average score for choice BA questions is: {choice_ba_score}. Max score is 1.")

    # Calculate the average score for Choice-type questions, sourced from EF
    mask = r"ChoiceEF\d+$"
    choice_ef_score = calculate_choice_q_score_average(ss_list, mask)
    print(f"The average score for choice EF questions is: {choice_ef_score}. Max score is 1.")

    # Calculate the average score for BAWE (AKA BA) corpus questions
    average_BA_score = mean([rate_ba_score, choice_ba_score])
    print(f"The average score for BAWE questions is: {average_BA_score}. Max score is 1.")

    # Calculate the average score for EFCAMDAT (AKA EF) corpus questions
    average_EF_score = mean([rate_ef_score, choice_ef_score])
    print(f"The average score for EFCAMDAT questions is: {average_EF_score}. Max score is 1.")
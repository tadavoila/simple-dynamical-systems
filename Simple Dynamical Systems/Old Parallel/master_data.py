import pandas as pd
import numpy as np
import random
import json

def reset_data():
    data = pd.read_json('Data/initial_data_1cat.json')
    
    # Extracting the 'words' data and flattening it
    words_data = pd.json_normalize(data['Category']['words'])

    # Transposing the DataFrame for better readability and structure
    words_data = words_data.transpose()

    # Resetting the index to have a proper DataFrame structure
    words_data.reset_index(inplace=True)

    # Splitting the 'index' column to separate word keys from their properties
    words_data[['word_key', 'property']] = words_data['index'].str.split('.', expand=True)

    # Pivoting the table to have properties as columns
    pivoted_data = words_data.pivot(index='word_key', columns='property', values=0)

    # Resetting index for clarity
    pivoted_data.reset_index(inplace=True)

    # Saving the filtered data to JSON file
    pivoted_data_path = "Data/pivoted_data.json"

    pivoted_data.to_json(pivoted_data_path, orient='records', lines=True)
    
    return "Data/pivoted_data.json"

def master_data():
    # Define strengths dictionary
    strengths = {}

    # Reset data
    pivoted_data_path = reset_data()
    
    # Read master data
    df = pd.read_json(pivoted_data_path, orient='records', lines=True)

    # Expanding the DataFrame to have a row for each exemplar
    expanded_data = []
    for index, row in df.iterrows():
        for exemplar_index, exemplar in enumerate(row['exemplars']):
            expanded_data.append({
                "word_key": row['word_key'],
                "exemplar": exemplar,
                "exemplar_index": exemplar_index,
                "frequency": row['frequency']
            })

    # Creating a new DataFrame with the expanded data
    expanded_df = pd.DataFrame(expanded_data)
    return expanded_df

if __name__ == "__main__":
    master_df = master_data()

    # Save the master dictionary as a csv file        
    master_df.to_csv("Data/master_df.csv")
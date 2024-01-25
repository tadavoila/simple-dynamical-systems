import pandas as pd
import numpy as np
import random
import json
import shutil
import multiprocessing
from multiprocessing import Process

def reset_data(run_number):
    # Duplicate the initial data file for each run
    original_file = 'Data/initial_data_1cat.json'
    duplicated_file = f'Data/initial_data_1cat_run{run_number + 1}.json'
    shutil.copy(original_file, duplicated_file)

    # Read and process the duplicated file
    data = pd.read_json(duplicated_file)
    
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

    # Saving the processed data to a new JSON file
    pivoted_data_path = f"Data/pivoted_data_run{run_number + 1}.json"
    pivoted_data.to_json(pivoted_data_path, orient='records', lines=True)
    
    return pivoted_data_path

def process_model(run_number):
    try:
        # Reset data for this run
        pivoted_data_path = reset_data(run_number)

        # Define mean dictionaries
        means_1_6 = {}
        means_7_12 = {}

        for i in range(20000):  # Increased number of iterations to 20,000
            # Read master data
            df = pd.read_json(pivoted_data_path, orient='records', lines=True)

            # Extract the 'words' dictionary from the DataFrame
            words_data = df['word_key'].tolist()
            frequencies = df['frequency'].astype(int).tolist()

            # Picking a word based on its frequency
            chosen_word = random.choices(words_data, weights=frequencies, k=1)[0]

            # Extract exemplars for the chosen word
            exemplars_list = df[df.word_key == chosen_word]['exemplars'].iloc[0]

            # Choose an exemplar randomly without weighting
            chosen_exemplar = random.choice(exemplars_list)

            # Add 0.1 to chosen exemplar
            new_exemplar = chosen_exemplar + 0.1

            # Choose a random index within the range of indices
            random_index = np.random.choice(len(exemplars_list))

            # Replace the value of the exemplar at the random index with the new exemplar
            exemplars_list[random_index] = new_exemplar

            # Update the dataframe with the new exemplar list
            df.at[df[df.word_key == chosen_word].index[0], 'exemplars'] = exemplars_list
            df.to_json(pivoted_data_path, orient='records', lines=True)

            # Save the mean of the exemplars
            if int(df[df.word_key == chosen_word]['frequency'].iloc[0]) < 7:
                means_1_6[i] = np.mean(exemplars_list)
            else:
                means_7_12[i] = np.mean(exemplars_list)
            
            # Test
            print(i, run_number)

        # Save the mean dictionaries as JSON files
        means_1_6_path = f"Outputs/means_1_6_run{run_number + 1}.json"
        means_7_12_path = f"Outputs/means_7_12_run{run_number + 1}.json"

        with open(means_1_6_path, 'w') as f:
            json.dump(means_1_6, f)

        with open(means_7_12_path, 'w') as f:
            json.dump(means_7_12, f)

        return means_1_6_path, means_7_12_path

    except Exception as e:
        print(f"Error in run {run_number}: {e}")

def parallel_new_model(iterations):
    processes = []

    for iter_num in range(iterations):
        process = Process(target=process_model, args=(iter_num,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    parallel_new_model(iterations=10)
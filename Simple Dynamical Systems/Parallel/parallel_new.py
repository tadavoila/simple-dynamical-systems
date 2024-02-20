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
    # Reset data for this run
    pivoted_data_path = reset_data(run_number)

    # Define mean dictionaries
    means_1_6_new = {}
    means_7_12_new = {}

    df = pd.read_json(pivoted_data_path, orient='records', lines=True)
    
    # Extract the 'words' dictionary from the DataFrame
    words_data = df['word_key'].tolist()
    frequencies = df['frequency'].astype(int).tolist()

    # Initialize the sum of exemplar frequencies
    exemplar_frequency_sum_1_6 = df[df.frequency <= 6]['frequency'].sum()
    exemplar_frequency_sum_7_12 = df[df.frequency > 6]['frequency'].sum()

    # Initialize exemplar means
    filtered_df_1_6 = df[df['frequency'] <= 6]
    filtered_df_7_12 = df[df['frequency'] > 6]
    flattened_exemplars_1_6 = [exemplar for sublist in filtered_df_1_6['exemplars'] for exemplar in sublist] # Flatten the list of exemplar lists into a single list
    flattened_exemplars_7_12 = [exemplar for sublist in filtered_df_7_12['exemplars'] for exemplar in sublist] # Flatten the list of exemplar lists into a single list
    mean_exemplars_1_6 = np.mean(flattened_exemplars_1_6)
    mean_exemplars_7_12 = np.mean(flattened_exemplars_7_12)

    for i in range(20000):  # Increased number of iterations to 20,000

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

        # Store the value of the exemplar at the random index
        storage = exemplars_list[random_index]

        # Replace the value of the exemplar at the random index with the new exemplar
        exemplars_list[random_index] = new_exemplar

        # Update the dataframe with the new exemplar list
        df.at[df[df.word_key == chosen_word].index[0], 'exemplars'] = exemplars_list

        # Calculate frequency of the chosen word
        freq = int(df[df.word_key == chosen_word]['frequency'].iloc[0])

        # Save the mean of the exemplars
        if freq < 7:
            # NEW
            diff = new_exemplar - storage
            if len(means_1_6_new) == 0:
                means_1_6_new[i] = mean_exemplars_1_6 + diff / exemplar_frequency_sum_1_6 
                index_storage_1_6 = i
            else:
                means_1_6_new[i] = means_1_6_new[index_storage_1_6] + diff / exemplar_frequency_sum_1_6 
                index_storage_1_6 = i

        else:
            # NEW
            diff = new_exemplar - storage
            if len(means_7_12_new) == 0:
                means_7_12_new[i] = mean_exemplars_7_12 + diff / exemplar_frequency_sum_7_12 
                index_storage_7_12 = i
            else:
                means_7_12_new[i] = means_7_12_new[index_storage_7_12] + diff / exemplar_frequency_sum_7_12
                index_storage_7_12 = i

    # Save the mean dictionaries as JSON files
    means_1_6_new_path = f"Outputs/means_1_6_new_run{run_number + 1}.json"
    means_7_12_new_path = f"Outputs/means_7_12_new_run{run_number + 1}.json"

    with open(means_1_6_new_path, 'w') as f:
        json.dump(means_1_6_new, f)

    with open(means_7_12_new_path, 'w') as f:
        json.dump(means_7_12_new, f)

    return means_1_6_new_path, means_7_12_new_path

def parallel_new_model(iterations):
    processes = []

    for iter_num in range(iterations):
        process = Process(target=process_model, args=(iter_num,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    parallel_new_model(iterations=50)
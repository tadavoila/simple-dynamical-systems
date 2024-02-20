import pandas as pd
import numpy as np
import random
import json
import shutil
import multiprocessing
from multiprocessing import Process
from collections import defaultdict

def reset_data(run_number, k_str):
    original_file = f"Outputs/strengths_k{k_str}.json"
    duplicated_file = f'Outputs/old_model_data_k{k_str}_run{run_number + 1}.json'
    shutil.copy(original_file, duplicated_file)

    data = pd.read_json(duplicated_file)

    # Initialize defaultdict for holding aggregated data
    aggregated_data = defaultdict(lambda: {"exemplars": [], "exemplar_strengths": [], "frequency": None})

    # Aggregate data by word_key
    for _, row in data.iterrows():
        word_key = row["word_key"]
        exemplar = row["exemplar"]
        exemplar_strength = row["exemplar_strength"]
        frequency = row["frequency"]
        exemplar_index = row["exemplar_index"]

        entry = aggregated_data[word_key]

        # Ensure lists are long enough to hold the current index
        if len(entry["exemplars"]) <= exemplar_index:
            entry["exemplars"].extend([None] * (exemplar_index + 1 - len(entry["exemplars"])))
            entry["exemplar_strengths"].extend([None] * (exemplar_index + 1 - len(entry["exemplar_strengths"])))

        # Update the lists
        entry["exemplars"][exemplar_index] = exemplar
        entry["exemplar_strengths"][exemplar_index] = exemplar_strength
        entry["frequency"] = frequency  # Frequency should be the same for all entries of the same word_key

    # Convert the aggregated data into the desired DataFrame format
    final_data = []
    for word_key, details in aggregated_data.items():
        # Remove None values that were placeholders for missing indices
        exemplars = [exemplar for exemplar in details["exemplars"] if exemplar is not None]
        exemplar_strengths = [strength for strength in details["exemplar_strengths"] if strength is not None]

        final_data.append({
            "word_key": word_key,
            "exemplar": exemplars,
            "frequency": details["frequency"],
            "exemplar_strength": exemplar_strengths
        })

    # Convert the list of dictionaries into a DataFrame
    final_df = pd.DataFrame(final_data)

    # Store the DataFrame
    pivoted_data_path = f"Outputs/old_model_data_k{k_str}_run{run_number + 1}.json"
    final_df.to_json(pivoted_data_path, orient='records', lines=True)
    
    return pivoted_data_path

def contains_small_exemplars(exemplars_list):
    return any(exemplar < 0.0000000001 for exemplar in exemplars_list)

def remove_small_exemplars(row):
    # Threshold for removal
    threshold = 0.0000000001

    # Find indices of exemplar strengths that are below the threshold
    indices_to_remove = [index for index, strength in enumerate(row['exemplar_strength']) if strength < threshold]

    # Remove these indices from both 'exemplar' and 'exemplar_strength'
    row['exemplar'] = [exemplar for index, exemplar in enumerate(row['exemplar']) if index not in indices_to_remove]
    row['exemplar_strength'] = [strength for index, strength in enumerate(row['exemplar_strength']) if index not in indices_to_remove]

    return row

def process_old_model(run_number, k_value, iterations):
    # Define mean dictionaries
    means_1_6 = {}
    means_7_12 = {}
    strengths_1_6 = {}
    strengths_7_12 = {}
    
    # Reset data path
    pivoted_data_path = reset_data(run_number, k_value)
    df = pd.read_json(pivoted_data_path, orient='records', lines=True)
    k = 1 - 1/int(df['frequency'].sum())
    words_data, frequencies = df['word_key'].tolist(), df['frequency'].astype(int).tolist()

    for i in range(20000):
        # Picking a word based on its frequency
        chosen_word = random.choices(words_data, weights=frequencies, k=1)[0]

        # Extract exemplars for the chosen word
        exemplars_list = df[df.word_key == chosen_word]['exemplar'].iloc[0]
        
        # Extract exemplar strengths for the chosen word
        exemplar_strengths = df[df.word_key == chosen_word]['exemplar_strength'].iloc[0]

        # Choose an exemplar weighted by exemplar strength
        chosen_exemplar = random.choices(exemplars_list, weights=exemplar_strengths, k=1)[0]

        # Add the chosen exemplar to the end of the exemplars list
        exemplars_list.append(chosen_exemplar + 0.1)
        new_value = chosen_exemplar + 0.1
        
        # Multiply all the exemplar strengths in the entire dataframe by k
        df['exemplar_strength'] = df['exemplar_strength'].apply(lambda x: [item * float(f"0.{k_value}") for item in x])
        exemplar_strengths = [item * float(f"0.{k_value}") for item in exemplar_strengths]
        
        # Add an exemplar strength of 1 to the end of the exemplar strengths list 
        exemplar_strengths.append(1)

        # Update the dataframe with the new exemplar list and exemplar strength list
        df.at[df[df.word_key == chosen_word].index[0], 'exemplar'] = exemplars_list
        df.at[df[df.word_key == chosen_word].index[0], 'exemplar_strength'] = exemplar_strengths
        
        if len(df[df.word_key == chosen_word]['exemplar']) > 1:
            if df['exemplar_strength'].apply(contains_small_exemplars).any():
                    df = df.apply(remove_small_exemplars, axis=1)

        # # Save the mean of the exemplars
        # if int(df[df.word_key == chosen_word]['frequency']) < 7:
        #     means_1_6[i] = np.mean(exemplars_list)
        #     sw_means_1_6[i] = sw_mean
        # else:
        #     means_7_12[i] = np.mean(exemplars_list)
        #     sw_means_7_12[i] = sw_mean

        # NEW - Initialize the previous strength and mean values         
        if i == 0:
            previous_strength_1_6 = 1
            previous_strength_7_12 = 1
            
            filtered_df_1_6 = df[df['frequency'] <= 6]
            filtered_df_7_12 = df[df['frequency'] > 6]
            flattened_exemplars_1_6 = [exemplar for sublist in filtered_df_1_6['exemplar'] for exemplar in sublist] # Flatten the list of exemplar lists into a single list
            flattened_exemplars_7_12 = [exemplar for sublist in filtered_df_7_12['exemplar'] for exemplar in sublist] # Flatten the list of exemplar lists into a single list
            previous_mean_1_6 = np.mean(flattened_exemplars_1_6)
            previous_mean_7_12 = np.mean(flattened_exemplars_7_12)

        else:
            previous_strength_1_6 = strengths_1_6[i-1]
            previous_strength_7_12 = strengths_7_12[i-1]
            previous_mean_1_6 = means_1_6[i-1]
            previous_mean_7_12 = means_7_12[i-1]

        # NEW - Save the mean of the exemplars
        if df[df.word_key == chosen_word]['frequency'].iloc[0] < 7:
            # Calculate the new total strength
            strengths_1_6[i] = previous_strength_1_6 * float(k_value) + 1
            strengths_7_12[i] = previous_strength_7_12 * float(k_value)

            # Calculate the new mean
            means_1_6[i] = (previous_mean_1_6 * (strengths_1_6[i] - 1) + new_value) / strengths_1_6[i]
            means_7_12[i] = previous_mean_7_12
        else:
            # Calculate the new total strength
            strengths_1_6[i] = previous_strength_1_6 * float(k_value)
            strengths_7_12[i] = previous_strength_7_12 * float(k_value) + 1

            # Calculate the new mean
            means_1_6[i] = previous_mean_1_6
            means_7_12[i] = (previous_mean_7_12 * (strengths_7_12[i] - 1) + new_value) / strengths_7_12[i]

        # Test
        print(i, run_number, k_value)
            
    # Save the mean dictionaries as JSON files        
    means_1_6_path = "Outputs/old_means_1_6_r" + str(run_number) + f"_k{k_value}" + ".json"
    means_7_12_path = "Outputs/old_means_7_12_r" + str(run_number) + f"_k{k_value}" + ".json"

    with open(means_1_6_path, 'w') as f:
        json.dump(means_1_6, f)

    with open(means_7_12_path, 'w') as f:
        json.dump(means_7_12, f)

def parallel_old_model(k_values, iterations):
    processes = []
    for run_number, k_value in enumerate(k_values):
        process = Process(target=process_old_model, args=(run_number, k_value, iterations))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()

if __name__ == '__main__':
    k_values = [str(round(1 - 7/492 + i*0.001, 5))[1:].replace('.', '') for i in range(10)]  # Define 10 different k values
    iterations = 20000  # Number of iterations for each k value
    parallel_old_model(k_values, iterations)
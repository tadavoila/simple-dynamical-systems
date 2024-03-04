import json
import random
import multiprocessing
from multiprocessing import Process

def reset_data():
    # Read the initial data file
    original_file = 'Data/initial_data_1cat.json'
    with open(original_file, 'r') as file:
        data = json.load(file)

    # Process the 'words' data
    words_data = data['Category']['words']
    processed_data = {}
    for word_key, attributes in words_data.items():
        processed_data[word_key] = {
            'frequency': attributes['frequency'],
            'exemplars': attributes['exemplars']
        }

    # Save the processed data to a new JSON file
    pivoted_data_path = "Data/pivoted_data.json"
    with open(pivoted_data_path, 'w') as file:
        json.dump(processed_data, file)

    return pivoted_data_path

def process_model(run_number, pivoted_data_path):
    # Load the processed data
    with open(pivoted_data_path, 'r') as file:
        words_data = json.load(file)

    # Generate a list of frequencies for weighted word selection
    frequencies = [word_info['frequency'] for word_info in words_data.values()]

    # Initialize lists to store mean values
    means_1_6_new = []
    means_7_12_new = []

    # Calculate the total frequency sum for both groups
    exemplar_frequency_sum_1_6 = sum(attributes['frequency'] for attributes in words_data.values() if attributes['frequency'] <= 6)
    exemplar_frequency_sum_7_12 = sum(attributes['frequency'] for attributes in words_data.values() if attributes['frequency'] > 6)

    # Filter words_data to get two groups based on 'frequency'
    group_1_6 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] <= 6}
    group_7_12 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] > 6}

    # Flatten the 'exemplars' lists for both groups
    flattened_exemplars_1_6 = [exemplar for attributes in group_1_6.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_7_12 = [exemplar for attributes in group_7_12.values() for exemplar in attributes['exemplars']]

    # Calculate the mean of 'exemplars' for both groups
    mean_exemplars_1_6 = sum(flattened_exemplars_1_6) / len(flattened_exemplars_1_6)
    mean_exemplars_7_12 = sum(flattened_exemplars_7_12) / len(flattened_exemplars_7_12)

    # Append initial means to the lists
    means_1_6_new.append(mean_exemplars_1_6)
    means_7_12_new.append(mean_exemplars_7_12)

    # Simulation loop
    for _ in range(20000):  
        chosen_word = random.choices(list(words_data.keys()), weights=frequencies, k=1)[0]
        attributes = words_data[chosen_word]
        exemplars_list = attributes['exemplars']
        chosen_exemplar = random.choice(exemplars_list)

        # Modify an exemplar and update the list
        new_exemplar = chosen_exemplar + 0.1
        random_index = random.randrange(len(exemplars_list))
        storage = exemplars_list[random_index]
        exemplars_list[random_index] = new_exemplar

        freq = attributes['frequency']
        if freq <= 6:
            diff = new_exemplar - storage
            updated_mean_1_6 = means_1_6_new[-1] + diff / exemplar_frequency_sum_1_6
            means_1_6_new.append(updated_mean_1_6)
            means_7_12_new.append(means_7_12_new[-1])
        else:
            diff = new_exemplar - storage
            updated_mean_7_12 = means_7_12_new[-1] + diff / exemplar_frequency_sum_7_12
            means_7_12_new.append(updated_mean_7_12)
            means_1_6_new.append(means_1_6_new[-1])

    # Save the mean dictionaries as JSON files
    means_1_6_new_path = f"Outputs/means_1_6_new_run{run_number + 1}.json"
    means_7_12_new_path = f"Outputs/means_7_12_new_run{run_number + 1}.json"

    with open(means_1_6_new_path, 'w') as f:
        json.dump(means_1_6_new, f)
    with open(means_7_12_new_path, 'w') as f:
        json.dump(means_7_12_new, f)

    return means_1_6_new, means_7_12_new

def parallel_new_model(iterations):
    # Prepare the data once
    pivoted_data_path = reset_data()

    processes = []
    for iter_num in range(iterations):
        process = Process(target=process_model, args=(iter_num, pivoted_data_path,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    parallel_new_model(iterations=50)

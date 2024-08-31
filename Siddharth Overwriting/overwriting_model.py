import json
import random
import multiprocessing
from multiprocessing import Process

def reset_data():
    # Read the initial data file
    original_file = 'Siddharth Overwriting/Data/initial_data_1cat.json'
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
    pivoted_data_path = "Siddharth Overwriting/Data/pivoted_data.json"
    with open(pivoted_data_path, 'w') as file:
        json.dump(processed_data, file)

    return pivoted_data_path

def process_model(run_number, pivoted_data_path):
    # Load the processed data
    with open(pivoted_data_path, 'r') as file:
        words_data = json.load(file)

    # Initialize a dictionary to store all means and variances
    data_dict = {
        **{f"means_{i}_new": [] for i in range(1, 13)},
        **{f"squared_means_{i}_new": [] for i in range(1, 13)},
        **{f"variances_{i}_new": [] for i in range(1, 13)},
        **{f"alt_variances_{i}_new": [] for i in range(1, 13)},
    }

    # Calculate the total frequency sum for all groups
    frequency_sums = {i: sum(attributes['frequency'] for attributes in words_data.values() if attributes['frequency'] == i) for i in range(1, 13)}

    # Filter words_data to get groups based on 'frequency'
    groups = {i: {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == i} for i in range(1, 13)}

    # Flatten the 'exemplars' lists for all groups
    flattened_exemplars = {i: [exemplar for attributes in groups[i].values() for exemplar in attributes['exemplars']] for i in range(1, 13)}

    # Calculate the mean of 'exemplars' for all groups
    for i in range(1, 13):
        data_dict[f"means_{i}_new"].append(sum(flattened_exemplars[i]) / len(flattened_exemplars[i]))

    # Calculate the variance of 'exemplars' for all groups
    for i in range(1, 13):
        mean = data_dict[f"means_{i}_new"][-1]
        variance = sum((exemplar - mean) ** 2 for exemplar in flattened_exemplars[i]) / len(flattened_exemplars[i])
        data_dict[f"variances_{i}_new"].append(variance)
        data_dict[f"alt_variances_{i}_new"].append(variance)

    # Create a copy of the dataframe and square all exemplars in one
    squared_exemplars = {i: [exemplar ** 2 for exemplar in flattened_exemplars[i]] for i in range(1, 13)}

    # Calculate the mean of the squared 'exemplars' for all groups
    for i in range(1, 13):
        data_dict[f"squared_means_{i}_new"].append(sum(squared_exemplars[i]) / len(squared_exemplars[i]))

    # Simulation loop
    for _ in range(10000):  
        chosen_word = random.choices(list(words_data.keys()), weights=[word_info['frequency'] for word_info in words_data.values()], k=1)[0]
        attributes = words_data[chosen_word]
        exemplars_list = attributes['exemplars']
        chosen_exemplar = random.choice(exemplars_list)

        # Modify an exemplar and update the list
        new_exemplar = chosen_exemplar + 0.1
        random_index = random.randrange(len(exemplars_list))
        storage = exemplars_list[random_index]
        exemplars_list[random_index] = new_exemplar

        freq = attributes['frequency']
        for i in range(1, 13):
            if i == freq:
                # Means
                diff = new_exemplar - storage
                updated_mean = data_dict[f"means_{i}_new"][-1] + diff / frequency_sums[i]
                data_dict[f"means_{i}_new"].append(updated_mean)
                
                # Squared Means
                squared_diff = new_exemplar**2 - storage**2
                updated_squared_mean = data_dict[f"squared_means_{i}_new"][-1] + squared_diff / frequency_sums[i]
                data_dict[f"squared_means_{i}_new"].append(updated_squared_mean)

                # Variances
                updated_variance = data_dict[f"variances_{i}_new"][-1] - (data_dict[f"means_{i}_new"][-1] - data_dict[f"means_{i}_new"][-2])**2 + ((new_exemplar - data_dict[f"means_{i}_new"][-2])**2 - (storage - data_dict[f"means_{i}_new"][-2])**2) / frequency_sums[i]
                data_dict[f"variances_{i}_new"].append(updated_variance)

                # Alternate Variances
                updated_alt_variance = data_dict[f"squared_means_{i}_new"][-1] - data_dict[f"means_{i}_new"][-1]**2
                data_dict[f"alt_variances_{i}_new"].append(updated_alt_variance)
            else:
                data_dict[f"means_{i}_new"].append(data_dict[f"means_{i}_new"][-1])
                data_dict[f"squared_means_{i}_new"].append(data_dict[f"squared_means_{i}_new"][-1])
                data_dict[f"variances_{i}_new"].append(data_dict[f"variances_{i}_new"][-1])
                data_dict[f"alt_variances_{i}_new"].append(data_dict[f"alt_variances_{i}_new"][-1])

    # Save all means and variances to a single JSON file
    output_path = f"Siddharth Overwriting/Siddharth Overwriting Model/all_data_run{run_number + 1}.json"
    with open(output_path, 'w') as file:
        json.dump(data_dict, file)

    return data_dict

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
    parallel_new_model(iterations=100)

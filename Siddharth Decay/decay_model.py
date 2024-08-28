import json
import random
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
import copy 
from statsmodels.stats.weightstats import DescrStatsW

def reset_data(k_str):
    original_file = f"Siddharth Decay/Outputs/strengths_k{k_str}.json"
    
    # Load data from JSON file into a dictionary
    with open(original_file, 'r') as f:
        data = json.load(f)

    # Group data by word key with frequency, a list of exemplars, and a list of exemplar strengths
    grouped_data = {}
    for item in data:
        word_key = item['word_key']
        if word_key not in grouped_data:
            grouped_data[word_key] = {'frequency': item['frequency'], 'exemplars': [], 'exemplar_strengths': []}

        # Append exemplar and exemplar_strength for each word_key
        grouped_data[word_key]['exemplars'].append(item['exemplar'])
        grouped_data[word_key]['exemplar_strengths'].append(item['exemplar_strength'])
            
    return grouped_data

def contains_small_exemplars(exemplars_list):
    return any(exemplar < 0.000001 for exemplar in exemplars_list)

def remove_small_exemplars(word_data):
    # Threshold for removal
    threshold = 0.000001

    # Create new lists for exemplars and their strengths, omitting small ones
    new_exemplars = []
    new_exemplar_strengths = []
    for exemplar, strength in zip(word_data['exemplars'], word_data['exemplar_strengths']):
        if strength >= threshold:
            new_exemplars.append(exemplar)
            new_exemplar_strengths.append(strength)

    # Update the word data with filtered lists
    word_data['exemplars'] = new_exemplars
    word_data['exemplar_strengths'] = new_exemplar_strengths

def process_old_model(run_number, k_value, iterations):
    words_data = reset_data(k_value)  # Load original data without copying

    # Create a copy of the dataframe and square all exemplars in one
    words_data_squared = copy.deepcopy(words_data) 
    for word, attributes in words_data_squared.items():
        attributes['exemplars'] = [exemplar ** 2 for exemplar in attributes['exemplars']]

    # Calculate k from the sum of frequencies
    frequencies = [word_info['frequency'] for word_info in words_data.values()]
    k = float(f"0.{k_value}")
    words_list = [key for key in words_data.keys()]

   # Initialize lists to store values for 1 - 12 each
    data_dict = {
        **{f"means_{i}_new": [] for i in range(1, 13)},
        **{f"squared_means_{i}_new": [] for i in range(1, 13)},
        **{f"variances_{i}_new": [] for i in range(1, 13)},
        **{f"alt_variances_{i}_new": [] for i in range(1, 13)},
        **{f"strengths_{i}_new": [] for i in range(1, 13)},
        **{f"word_variances_{i}": [] for i in range(1, 13)}
    }

    # Filter words_data to get groups based on 'frequency'
    group_1 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 1}
    group_2 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 2}
    group_3 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 3}
    group_4 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 4}
    group_5 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 5}
    group_6 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 6}
    group_7 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 7}
    group_8 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 8}
    group_9 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 9}
    group_10 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 10}
    group_11 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 11}
    group_12 = {word: attributes for word, attributes in words_data.items() if attributes['frequency'] == 12}

    # Flatten the 'exemplars' lists for groups
    flattened_exemplars_1 = [exemplar for attributes in group_1.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_2 = [exemplar for attributes in group_2.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_3 = [exemplar for attributes in group_3.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_4 = [exemplar for attributes in group_4.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_5 = [exemplar for attributes in group_5.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_6 = [exemplar for attributes in group_6.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_7 = [exemplar for attributes in group_7.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_8 = [exemplar for attributes in group_8.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_9 = [exemplar for attributes in group_9.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_10 = [exemplar for attributes in group_10.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_11 = [exemplar for attributes in group_11.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_12 = [exemplar for attributes in group_12.values() for exemplar in attributes['exemplars']]

    # Flatten the 'exemplar_strengths' lists for groups
    flattened_strengths_1 = [strength for attributes in group_1.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_2 = [strength for attributes in group_2.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_3 = [strength for attributes in group_3.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_4 = [strength for attributes in group_4.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_5 = [strength for attributes in group_5.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_6 = [strength for attributes in group_6.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_7 = [strength for attributes in group_7.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_8 = [strength for attributes in group_8.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_9 = [strength for attributes in group_9.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_10 = [strength for attributes in group_10.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_11 = [strength for attributes in group_11.values() for strength in attributes['exemplar_strengths']]
    flattened_strengths_12 = [strength for attributes in group_12.values() for strength in attributes['exemplar_strengths']]

    # Calculate the total strength for groups
    total_strength_1 = sum(flattened_strengths_1)
    total_strength_2 = sum(flattened_strengths_2)
    total_strength_3 = sum(flattened_strengths_3)
    total_strength_4 = sum(flattened_strengths_4)
    total_strength_5 = sum(flattened_strengths_5)
    total_strength_6 = sum(flattened_strengths_6)
    total_strength_7 = sum(flattened_strengths_7)
    total_strength_8 = sum(flattened_strengths_8)
    total_strength_9 = sum(flattened_strengths_9)
    total_strength_10 = sum(flattened_strengths_10)
    total_strength_11 = sum(flattened_strengths_11)
    total_strength_12 = sum(flattened_strengths_12)

    # Calculate the mean of 'exemplars' weighted by strength for groups
    data_dict["means_1_new"].append(sum(e * s for e, s in zip(flattened_exemplars_1, flattened_strengths_1)) / total_strength_1)
    data_dict["means_2_new"].append(sum(e * s for e, s in zip(flattened_exemplars_2, flattened_strengths_2)) / total_strength_2)
    data_dict["means_3_new"].append(sum(e * s for e, s in zip(flattened_exemplars_3, flattened_strengths_3)) / total_strength_3)
    data_dict["means_4_new"].append(sum(e * s for e, s in zip(flattened_exemplars_4, flattened_strengths_4)) / total_strength_4)
    data_dict["means_5_new"].append(sum(e * s for e, s in zip(flattened_exemplars_5, flattened_strengths_5)) / total_strength_5)
    data_dict["means_6_new"].append(sum(e * s for e, s in zip(flattened_exemplars_6, flattened_strengths_6)) / total_strength_6)
    data_dict["means_7_new"].append(sum(e * s for e, s in zip(flattened_exemplars_7, flattened_strengths_7)) / total_strength_7)
    data_dict["means_8_new"].append(sum(e * s for e, s in zip(flattened_exemplars_8, flattened_strengths_8)) / total_strength_8)
    data_dict["means_9_new"].append(sum(e * s for e, s in zip(flattened_exemplars_9, flattened_strengths_9)) / total_strength_9)
    data_dict["means_10_new"].append(sum(e * s for e, s in zip(flattened_exemplars_10, flattened_strengths_10)) / total_strength_10)
    data_dict["means_11_new"].append(sum(e * s for e, s in zip(flattened_exemplars_11, flattened_strengths_11)) / total_strength_11)
    data_dict["means_12_new"].append(sum(e * s for e, s in zip(flattened_exemplars_12, flattened_strengths_12)) / total_strength_12)

    '''SQUARED'''

    # Filter words_data to get groups based on 'frequency'
    squared_group_1 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 1}
    squared_group_2 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 2}
    squared_group_3 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 3}
    squared_group_4 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 4}
    squared_group_5 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 5}
    squared_group_6 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 6}
    squared_group_7 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 7}
    squared_group_8 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 8}
    squared_group_9 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 9}
    squared_group_10 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 10}
    squared_group_11 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 11}
    squared_group_12 = {word: attributes for word, attributes in words_data_squared.items() if attributes['frequency'] == 12}

    # Flatten the 'exemplars' lists for groups
    squared_flattened_exemplars_1 = [exemplar for attributes in squared_group_1.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_2 = [exemplar for attributes in squared_group_2.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_3 = [exemplar for attributes in squared_group_3.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_4 = [exemplar for attributes in squared_group_4.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_5 = [exemplar for attributes in squared_group_5.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_6 = [exemplar for attributes in squared_group_6.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_7 = [exemplar for attributes in squared_group_7.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_8 = [exemplar for attributes in squared_group_8.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_9 = [exemplar for attributes in squared_group_9.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_10 = [exemplar for attributes in squared_group_10.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_11 = [exemplar for attributes in squared_group_11.values() for exemplar in attributes['exemplars']]
    squared_flattened_exemplars_12 = [exemplar for attributes in squared_group_12.values() for exemplar in attributes['exemplars']]

    for i in range(1, 13):
        squared_exemplars = locals()[f"squared_flattened_exemplars_{i}"]
        strengths = locals()[f"flattened_strengths_{i}"]
        total_strength = locals()[f"total_strength_{i}"]
        exemplars = locals()[f"flattened_exemplars_{i}"]

        # SQUARED
        data_dict[f"squared_means_{i}_new"].append(
            sum(e * s for e, s in zip(squared_exemplars, strengths)) / total_strength
        )

        # STRENGTHS
        data_dict[f"strengths_{i}_new"].append(total_strength)

        # NEW METHOD FOR VARIANCES
        variance = DescrStatsW(exemplars, strengths, ddof=0).var
        data_dict[f"variances_{i}_new"].append(variance)
        data_dict[f"alt_variances_{i}_new"].append(variance)

    '''LOOP'''

    # Simulation loops
    for i in range(iterations):
        chosen_word = random.choices(words_list, weights=frequencies, k=1)[0]

        # Aggregate all exemplars and their strengths for the chosen word
        exemplars_list = words_data[chosen_word]['exemplars']
        exemplar_strengths = words_data[chosen_word]['exemplar_strengths']

        # Choose an exemplar weighted by exemplar strength
        chosen_exemplar = random.choices(exemplars_list, weights=exemplar_strengths, k=1)[0]

        # Add the chosen exemplar to the end of the exemplars list
        new_value = chosen_exemplar + 0.1
        exemplars_list.append(new_value)

        # Multiply all the exemplar strengths in the entire list by k
        for word in words_data:
            words_data[word]['exemplar_strengths'] = [item * k for item in words_data[word]['exemplar_strengths']]
        exemplar_strengths.append(1)

        # Update exemplar and strength lists for the chosen word
        words_data[chosen_word]['exemplars'] = exemplars_list
        words_data[chosen_word]['exemplar_strengths'] = exemplar_strengths

        # Check and remove small exemplars if necessary
        if len(exemplars_list) > 1 and contains_small_exemplars(exemplar_strengths):
            remove_small_exemplars(words_data[chosen_word])
              
        # Store means
        freq = words_data[chosen_word]['frequency']
        k_float = float(f"0.{k_value}")

        for i in range(1, 13):
            if i == freq:
                # Current Frequencies
                strengths = data_dict[f"strengths_{i}_new"][-1] * k_float + 1
                data_dict[f"strengths_{i}_new"].append(strengths)
                means = data_dict[f"means_{i}_new"][-1] + (new_value - data_dict[f"means_{i}_new"][-1]) / strengths
                data_dict[f"means_{i}_new"].append(means)
                
                squared_means = data_dict[f"squared_means_{i}_new"][-1] + (new_value**2 - data_dict[f"squared_means_{i}_new"][-1]) / strengths
                data_dict[f"squared_means_{i}_new"].append(squared_means)
                
                basic = (means - data_dict[f"means_{i}_new"][-2])**2
                variance = data_dict[f"variances_{i}_new"][-1] + basic - (data_dict[f"variances_{i}_new"][-1] + basic) / (k * eval(f'total_strength_{i}') + 1) + (new_value - means)**2 / (k * eval(f'total_strength_{i}') + 1)
                data_dict[f"variances_{i}_new"].append(variance)
                
                alt_variance = squared_means - (means ** 2)
                data_dict[f"alt_variances_{i}_new"].append(alt_variance)
            else:
                # Other Frequencies
                strengths = data_dict[f"strengths_{i}_new"][-1] * k_float
                data_dict[f"strengths_{i}_new"].append(strengths)
                data_dict[f"means_{i}_new"].append(data_dict[f"means_{i}_new"][-1])
                data_dict[f"squared_means_{i}_new"].append(data_dict[f"squared_means_{i}_new"][-1])
                data_dict[f"variances_{i}_new"].append(data_dict[f"variances_{i}_new"][-1])
                data_dict[f"alt_variances_{i}_new"].append(data_dict[f"alt_variances_{i}_new"][-1])

    # Save the data dictionary to a single JSON file
    file_path = f"Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_value}.json"
    with open(file_path, 'w') as f:
        json.dump(data_dict, f)

    return data_dict

def run_task(args):
    run_number, k_value, iterations = args
    process_old_model(run_number, k_value, iterations)

def parallel_old_model(k_values, iterations, num_workers=10):
    tasks = [(run_number, k_value, iterations) for k_value in k_values for run_number in range(100)]
    
    with Pool(processes=num_workers) as pool:
        pool.map(run_task, tasks)

if __name__ == '__main__':
    values = [x*10 for x in range(1, 101, 10)]
    k_value = [1 - 1/value for value in values] 
    k_values = ["{:06.5f}".format(k_value).replace('.', '')[1:] for k_value in k_value]
    iterations = 10000
    parallel_old_model(k_values, iterations)
    print(values)

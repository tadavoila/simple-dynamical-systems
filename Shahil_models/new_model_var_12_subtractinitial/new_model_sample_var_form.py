import random
import json
import csv
import numpy as np
from multiprocessing import Pool
import math
from statsmodels.stats.weightstats import DescrStatsW

STRENGTH_THRESHOLD = 1e-6

def choose_weighted_exemplar(exemplars):
    values, strengths = zip(*exemplars.items())
    value_strengths = [sum(s) for s in strengths]
    selected_value = random.choices(values, weights=value_strengths)[0]
    return selected_value

def process_data(params):
    source_json_file, run_number, iterations, decay_rate, advancement, save_every, burn_in, output_file_suffix = params
    output_json_file_name = f'final_data_run{run_number}{output_file_suffix}.json'
    output_average_file_name = f'averages_run{run_number}{output_file_suffix}.csv'

    category_data = load_data(source_json_file)
    words, word_probabilities = get_word_probabilities(category_data)

    if burn_in:
        burn_in_model(category_data, words, word_probabilities, decay_rate)
        initial_variances = calculate_initial_variances(category_data)
    '''else:
        initial_variances = [0.377, 1.168496732026144, 1.0807471264367816, 0.9758720930232558, 0.9330625, 
                             1.0054890992541594, 1.0681397016637981, 0.9872123015873017, 0.9864949494949495, 
                             0.9858505747126437, 0.8585454545454545, 1.2826515151515152]'''
    
    group_averages, group_variances = run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every, initial_variances)

    save_data(category_data, output_json_file_name)
    save_averages(group_averages, group_variances, output_average_file_name)

def burn_in_model(category_data, words, word_probabilities, decay_rate):
    for iteration in range(math.ceil(math.log(STRENGTH_THRESHOLD) / math.log(decay_rate))):
        iterate_model(category_data, words, word_probabilities, decay_rate)

def run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every, initial_variances):
    average_values, total_strengths = get_group_stats(category_data)
    group_averages = [average_values.copy()]
    group_variances = [initial_variances.copy()]

    for iteration in range(iterations):
        new_exemplar_value, word_group = iterate_model(category_data, words, word_probabilities, decay_rate, advancement)

        average_values, total_strengths = update_group_stats(average_values, total_strengths, word_group, new_exemplar_value, decay_rate)

        if iteration % save_every == 0:
            group_averages.append(average_values.copy())
            current_variances = calculate_variances(category_data, group_variances[-1])
            # Subtract initial variances to see how variance changes over time
            adjusted_variances = [v - initial_v for v, initial_v in zip(current_variances, initial_variances)]
            group_variances.append(adjusted_variances)

    return group_averages, group_variances

def iterate_model(category_data, words, word_probabilities, decay_rate, advancement=0):
    word = random.choices(words, weights=word_probabilities)[0]
    word_group = category_data[word]["frequency"] - 1  # Adjust for zero indexing
    exemplars = category_data[word]["exemplars"]

    remove_weak_exemplars(exemplars)
    new_exemplar_value = round(choose_weighted_exemplar(exemplars) + advancement, 1)
    decay_exemplars(category_data, decay_rate)
    add_exemplar(exemplars, new_exemplar_value)

    return new_exemplar_value, word_group

def load_data(source_json_file):
    with open(source_json_file, "r") as file:
        category_data = json.load(file)
    for word_data in category_data.values():
        word_data["exemplars"] = {float(value): np.array(strengths) for value, strengths in word_data["exemplars"].items()}
    return category_data

def get_word_probabilities(category_data):
    words, frequencies = zip(*[(word, word_data["frequency"]) for word, word_data in category_data.items()])
    total_frequency = sum(frequencies)
    word_probabilities = [freq / total_frequency for freq in frequencies]
    return words, word_probabilities

def get_group_stats(category_data):
    average_values = [0] * 12
    total_strengths = [0] * 12

    for word_data in category_data.values():
        frequency = word_data["frequency"] - 1  # Adjust for zero indexing
        exemplars = word_data["exemplars"]
        values, strengths = zip(*exemplars.items())
        value_strengths = [sum(s) for s in strengths]
        total_strength = sum(value_strengths)
        strength_weighted_value = sum(value * strength for value, strength in zip(values, value_strengths))

        if total_strength > 0:  # Avoid division by zero
            average_values[frequency] += strength_weighted_value
            total_strengths[frequency] += total_strength

    for i in range(len(average_values)):
        if total_strengths[i] > 0:  # Avoid division by zero
            average_values[i] /= total_strengths[i]

    return average_values, total_strengths

def update_group_stats(average_values, total_strengths, word_group, new_exemplar_value, decay_rate):
    total_strengths[word_group] = total_strengths[word_group] * decay_rate + 1
    if total_strengths[word_group] > 0:  # Avoid division by zero
        average_values[word_group] = (average_values[word_group] * (total_strengths[word_group] - 1) + new_exemplar_value) / total_strengths[word_group]

    for i in range(len(average_values)):
        if i != word_group:
            total_strengths[i] *= decay_rate

    return average_values, total_strengths

def calculate_variances(category_data, current_variances):
    variances = current_variances.copy()  # Initialize with current variances
    
    for word_data in category_data.values():
        exemplars = word_data["exemplars"]
        word_group = word_data["frequency"] - 1
        
        values, strengths = zip(*exemplars.items())
        value_strengths = [sum(s) for s in strengths]
        S = sum(value_strengths)
        
        if S == 0:
            continue
        
        m = sum(value * strength for value, strength in zip(values, value_strengths)) / S
        V = variances[word_group] 

        x_new = list(exemplars.keys())[-1]
        
        m_prime = m + (x_new - m) / (S + 1)
        V_prime = V + (m_prime - m)**2 - (V + (m_prime - m)**2) / (S + 1) + (x_new - m_prime)**2 / (S + 1)
        
        variances[word_group] = V_prime
        
    return variances

def calculate_initial_variances(category_data):
    values_dict = {i: [] for i in range(1, 13)}
    weights_dict = {i: [] for i in range(1, 13)}

    # Group exemplars by their frequency
    for word_data in category_data.values():
        frequency = word_data["frequency"]
        exemplars = word_data["exemplars"]
        for exemplar, strengths in exemplars.items():
            exemplar_value = float(exemplar)
            values_dict[frequency].extend([exemplar_value] * len(strengths))
            weights_dict[frequency].extend(strengths)

    # Calculate the strength-weighted variance for each frequency group
    variances = {}
    for i in range(1, 13):
        if len(values_dict[i]) > 1:  # Ensure there's enough data to calculate variance
            descr_stats = DescrStatsW(values_dict[i], weights=weights_dict[i], ddof=0)
            variances[i-1] = descr_stats.var
        else:
            variances[i-1] = 0.0  # Assign a default value if there's insufficient data

    return [variances[i] for i in range(12)]

def remove_weak_exemplars(exemplars):
    # Until an exemplar that is strong enough to survive is encountered,
    # keep track of the value of the strongest exemplar so far
    # (if all exemplars are too weak, this one must be the target)
    strongest_strength = 0
    strongest_value = None

    for value, strengths in list(exemplars.items()):
        strongest_value_here = strengths[-1]
        if strongest_strength == 0 or strongest_value_here > strongest_strength:
            strongest_strength = strongest_value_here
            strongest_value = value

        weak_exemplars = np.searchsorted(strengths, STRENGTH_THRESHOLD, side='right')
        exemplars[value] = strengths[weak_exemplars:]
        if exemplars[value].size == 0:
            del exemplars[value]

    # In case all exemplars have been deleted, restore the strongest one
    if strongest_strength <= STRENGTH_THRESHOLD:
        exemplars[strongest_value] = np.array([strongest_strength])

def decay_exemplars(category_data, decay_rate):
    for word_data in category_data.values():
        for strengths in word_data["exemplars"].values():
            strengths *= decay_rate

def add_exemplar(exemplars, new_exemplar_value):
    if new_exemplar_value not in exemplars:
        exemplars[new_exemplar_value] = np.array([1.0])
    else:
        exemplars[new_exemplar_value] = np.append(exemplars[new_exemplar_value], 1.0)

def save_data(category_data, json_file_name):
    for word_data in category_data.values():
        for value, strengths in word_data["exemplars"].items():
            word_data["exemplars"][value] = list(strengths)

    with open(json_file_name, 'w') as json_file:
        json.dump(category_data, json_file, indent=4)

def save_averages(group_averages, group_variances, output_average_file_name):
    with open(output_average_file_name, 'w', newline="") as out_file:
        writer = csv.writer(out_file)
        # Header for average and variance columns
        headers = ["FREQ_" + str(i + 1) + "_AVG" for i in range(12)] + ["FREQ_" + str(i + 1) + "_VAR" for i in range(12)]
        writer.writerow(headers)
        # Write averages and the adjusted variances (change over time)
        for averages, variances in zip(group_averages, group_variances):
            writer.writerow(averages + variances)

if __name__ == '__main__':
    processes = 6
    runs = 10
    iterations = 20000
    burn_in = True
    save_every = 100
    advancement = 0.1
    source_file = 'initial_data_1cat_decay-start.json'
    decay_points = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800]

    for x in decay_points:  # Use specified decay rates
        decay_rate = 1 - (1 / x)
        output_file_suffix = f'_decay_{x}'
        params = [(source_file, run, iterations, decay_rate, advancement, save_every, burn_in, output_file_suffix) for run in range(runs)]
        with Pool(processes=processes) as pool:
            pool.map(process_data, params)

#subtract the initial variance from burn in for each one -> this then shows how the values increase/decrease in variance over time.
#mean - first value in data

import random
import json
import csv
import numpy as np
from multiprocessing import Pool
import math

STRENGTH_THRESHOLD = 1e-6

def choose_weighted_exemplar(exemplars):
    values, strengths = zip(*exemplars.items())
    value_strengths = [sum(s) for s in strengths]
    selected_value = random.choices(values, weights=value_strengths)[0]
    return selected_value

def process_data(params):
    source_json_file, run_number, iterations, decay_rate, advancement, save_every, burn_in = params
    output_json_file_name = f'final_data_run{run_number}.json'
    output_average_file_name = f'averages_run{run_number}.csv'

    category_data = load_data(source_json_file)
    words, word_probabilities = get_word_probabilities(category_data)

    if burn_in:
        burn_in_model(category_data, words, word_probabilities, decay_rate)
    group_averages, group_variances = run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every)

    save_data(category_data, output_json_file_name)
    save_averages(group_averages, group_variances, output_average_file_name)

def burn_in_model(category_data, words, word_probabilities, decay_rate):
    for iteration in range(math.ceil(math.log(STRENGTH_THRESHOLD) / math.log(decay_rate))):
        iterate_model(category_data, words, word_probabilities, decay_rate)

def run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every):
    average_values, total_strengths = get_group_stats(category_data)
    group_averages = ([average_values[0]], [average_values[1]])
    group_variances = ([0], [0])

    for iteration in range(iterations):
        new_exemplar_value, word_group = iterate_model(category_data, words, word_probabilities, decay_rate, advancement)

        average_values, total_strengths = update_group_stats(average_values, total_strengths, word_group, new_exemplar_value, decay_rate)

        if iteration % save_every == 0:
            group_averages[0].append(average_values[0])
            group_averages[1].append(average_values[1])

            variances = calculate_variances(category_data)
            group_variances[0].append(variances[0])
            group_variances[1].append(variances[1])

    return group_averages, group_variances

def iterate_model(category_data, words, word_probabilities, decay_rate, advancement=0):
    word = random.choices(words, weights=word_probabilities)[0]
    word_group = category_data[word]["frequency"] // 7
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
    word_probabilities = tuple(freq / total_frequency for freq in frequencies)
    return words, word_probabilities

def get_group_stats(category_data):
    average_values = [0, 0]
    total_strengths = [0, 0]

    for word_data in category_data.values():
        frequency = word_data["frequency"]
        exemplars = word_data["exemplars"]
        values, strengths = zip(*exemplars.items())
        value_strengths = [sum(s) for s in strengths]
        total_strength = sum(value_strengths)
        strength_weighted_value = sum(value * strength for value, strength in zip(values, value_strengths))

        average_values[frequency // 7] += strength_weighted_value
        total_strengths[frequency // 7] += total_strength

    for i in range(len(average_values)):
        average_values[i] /= total_strengths[i]

    return average_values, total_strengths

def remove_weak_exemplars(exemplars):
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

def update_group_stats(average_values, total_strengths, word_group, new_exemplar_value, decay_rate):
    total_strengths[word_group] = total_strengths[word_group] * decay_rate + 1
    average_values[word_group] = (average_values[word_group] * (total_strengths[word_group] - 1) + new_exemplar_value) / total_strengths[word_group]

    total_strengths[1 - word_group] *= decay_rate

    return average_values, total_strengths

def calculate_variances(category_data):
    variances = [0, 0]  
    for word_data in category_data.values():
        exemplars = word_data["exemplars"]  
        values, strengths = zip(*exemplars.items())  
        value_strengths = [sum(s) for s in strengths]  # Calculate the total strength for each exemplar
        total_strength = sum(value_strengths)  # Calculate the total strength for the word group
        strength_weighted_value = sum(value * strength for value, strength in zip(values, value_strengths))  # Calculate the strength-weighted value for the word group
        strength_weighted_value_squared = sum(value**2 * strength for value, strength in zip(values, value_strengths))  # Calculate the squared strength-weighted value for the word group
        # Calculate the variance for the word group based on the frequency
        variances[word_data["frequency"] // 7] += (strength_weighted_value_squared / total_strength) - ((strength_weighted_value / total_strength) ** 2)
    return variances  


    
def save_data(category_data, json_file_name):
    for word_data in category_data.values():
        for value, strengths in word_data["exemplars"].items():
            word_data["exemplars"][value] = list(strengths)

    with open(json_file_name, 'w') as json_file:
        json.dump(category_data, json_file, indent=4)

def save_averages(group_averages, group_variances, output_average_file_name):
    with open(output_average_file_name, 'w', newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["FREQ_1_TO_6", "FREQ_7_TO_12", "VAR_1_TO_6", "VAR_7_TO_12"])
        writer.writerows(zip(group_averages[0], group_averages[1], group_variances[0], group_variances[1]))

if __name__ == '__main__':
    processes = 6
    runs = 10
    iterations = 20000
    burn_in = True
    save_every = 100
    decay_rate = 1 - (1 / 492)
    advancement = 0.1
    source_file = 'initial_data_1cat_decay-start.json'

    params = [(source_file, run, iterations, decay_rate, advancement, save_every, burn_in) for run in range(runs)]
    with Pool(processes=processes) as pool:
        pool.map(process_data, params)


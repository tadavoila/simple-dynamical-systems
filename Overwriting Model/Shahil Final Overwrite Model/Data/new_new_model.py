import random
import json
import csv
import numpy as np
from multiprocessing import Pool
import math

STRENGTH_THRESHOLD = 1e-6
#250-1000
# To burn in to within eps of the total stable strength of a system requires at least
# log(abs(eps * (1 - decay_rate) / (init_total_strength * (1 - decay_rate) - 1))) / log(decay_rate)
# iterations.
# To fill up the queue of strengths and stabilize the number of exemplars in the system requires
# log(strength_threshold) / log(decay_rate)
# iterations.
# Therefore, to ensure that filling up the queue of strengths also enacts sufficient burn-in, set
# strength_threshold < abs(eps * (1 - decay_rate) / (init_total_strength * (1 - decay_rate) - 1)).
# Given eps = 0.01 and init_total_strength = 492, the choice of strength_threshold = 1e-6 allows
# for sufficient burn-in for decay rates up to approx 1 - 1/10000
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
    group_averages = run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every)

    save_data(category_data, output_json_file_name)
    save_averages(group_averages, output_average_file_name)


def burn_in_model(category_data, words, word_probabilities, decay_rate):
    for iteration in range(math.ceil(math.log(STRENGTH_THRESHOLD) / math.log(decay_rate))):
        iterate_model(category_data, words, word_probabilities, decay_rate)

def run_model(category_data, words, word_probabilities, iterations, decay_rate, advancement, save_every):
    average_values, total_strengths = get_group_stats(category_data)
    group_averages = ([average_values[0]], [average_values[1]])

    for iteration in range(iterations):
        new_exemplar_value, word_group = iterate_model(category_data, words, word_probabilities, decay_rate,
                                                       advancement)

        average_values, total_strengths = update_group_stats(average_values, total_strengths,
                                                             word_group, new_exemplar_value, decay_rate)

        if iteration % save_every == 0:
            group_averages[0].append(average_values[0])
            group_averages[1].append(average_values[1])

    return group_averages


def iterate_model(category_data, words, word_probabilities, decay_rate, advancement=0):
    word = random.choices(words, weights=word_probabilities)[0]
    word_group = category_data[word]["frequency"] // 7
    exemplars = category_data[word]["exemplars"]

    # For efficiency, only remove exemplars of the chosen word, and do so before picking a target value
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

def update_group_stats(average_values, total_strengths, word_group, new_exemplar_value, decay_rate):
    # for the freq range that the chosen word is in:
    total_strengths[word_group] = total_strengths[word_group] * decay_rate + 1
    average_values[word_group] = (average_values[word_group] * (total_strengths[word_group] - 1) + new_exemplar_value) / \
                                 total_strengths[word_group]
    # for the other freq range:
    total_strengths[1 - word_group] *= decay_rate

    return average_values, total_strengths

def save_data(category_data, json_file_name):
    # Need to get rid of numpy arrays to save to JSON
    for word_data in category_data.values():
        for value, strengths in word_data["exemplars"].items():
            word_data["exemplars"][value] = list(strengths)

    with open(json_file_name, 'w') as json_file:
        json.dump(category_data, json_file, indent=4)

def save_averages(group_averages, output_average_file_name):
    with open(output_average_file_name, 'w', newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["FREQ_1_TO_6", "FREQ_7_TO_12"])
        writer.writerows(zip(*group_averages))


if __name__ == '__main__':
    processes = 6
    runs = 10  # Adjust the number of runs per k value if needed
    iterations = 10000
    burn_in = True
    save_every = 100
    advancement = 0.1
    source_file = 'initial_data_1cat_decay-start.json'

    # Create a wrapper function for printing progress and calling process_data
    def process_with_progress(params):
        source_json_file, run_number, iterations, decay_rate, advancement, save_every, burn_in, output_file_suffix = params
        print(f'Processing k value for x={1/(1-decay_rate):.0f}, decay_rate={decay_rate:.4f}')
        process_data(params)

    for x in range(10, 1001):  # Loop from x=10 to x=1000, adjust as needed
        decay_rate = 1 - (1 / x)  # Calculate decay rate as k=1-1/x
        output_file_suffix = f'_decay_{x}'  # Suffix for output files to indicate decay rate
        params = [(source_file, run, iterations, decay_rate, advancement, save_every, burn_in, output_file_suffix) for run in range(runs)]
        with Pool(processes=processes) as pool:
            pool.map(process_with_progress, params)


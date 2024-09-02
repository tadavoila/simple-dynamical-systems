import random
import json
import shutil
from multiprocessing import Process

def process_iteration(iter_num, json_file):
    # Duplicate the initial data file for each iteration
    duplicated_file = f'initial_data_copy_{iter_num + 1}.json'
    shutil.copy(json_file, duplicated_file)

    with open(duplicated_file, 'r') as file:
        data = json.load(file)

    words_data = data['Category']['words']
    frequencies = [word_info['frequency'] for word_info in words_data.values()]

    # Initialize running means for each group
    running_mean_1_to_6 = 0
    running_mean_7_to_12 = 0

    group_1_to_6 = {word: attributes for word, attributes in words_data.items() if 1 <= attributes['frequency'] <= 6}
    group_7_to_12 = {word: attributes for word, attributes in words_data.items() if 7 <= attributes['frequency'] <= 12}

    flattened_exemplars_1_to_6 = [exemplar for attributes in group_1_to_6.values() for exemplar in attributes['exemplars']]
    flattened_exemplars_7_to_12 = [exemplar for attributes in group_7_to_12.values() for exemplar in attributes['exemplars']]

    if flattened_exemplars_1_to_6:
        running_mean_1_to_6 = sum(flattened_exemplars_1_to_6) / len(flattened_exemplars_1_to_6)
    if flattened_exemplars_7_to_12:
        running_mean_7_to_12 = sum(flattened_exemplars_7_to_12) / len(flattened_exemplars_7_to_12)

    # Dictionaries to store the averages with iteration number as key
    means_1_to_6 = {0: running_mean_1_to_6}
    means_7_to_12 = {0: running_mean_7_to_12}

    for i in range(20000):  # Adjust the number of iterations as needed
        chosen_word = random.choices(list(words_data.keys()), weights=frequencies, k=1)[0]
        attributes = words_data[chosen_word]
        exemplars_list = attributes['exemplars']
        chosen_exemplar = random.choice(exemplars_list)

        new_exemplar = chosen_exemplar + 0.1
        random_index = random.randrange(len(exemplars_list))
        old_value = exemplars_list[random_index]
        exemplars_list[random_index] = new_exemplar

        frequency = attributes['frequency']
        if 1 <= frequency <= 6:
            diff = new_exemplar - old_value
            running_mean_1_to_6 += diff / len(flattened_exemplars_1_to_6)
            means_1_to_6[i] = running_mean_1_to_6
        elif 7 <= frequency <= 12:
            diff = new_exemplar - old_value
            running_mean_7_to_12 += diff / len(flattened_exemplars_7_to_12)
            means_7_to_12[i] = running_mean_7_to_12

    json_file_1_to_6 = f'averages_1_to_6_{iter_num + 1}.json'
    with open(json_file_1_to_6, 'w') as file:
        json.dump(means_1_to_6, file, indent = 4)

    json_file_7_to_12 = f'averages_7_to_12_{iter_num + 1}.json'
    with open(json_file_7_to_12, 'w') as file:
        json.dump(means_7_to_12, file, indent = 4)

    # Save the updated data back to the duplicated JSON file
    with open(duplicated_file, 'w') as file:
        json.dump(data, file, indent = 4)

def process_data(json_file, iterations=20):
    processes = []

    for iter_num in range(iterations):
        process = Process(target=process_iteration, args=(iter_num, json_file))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == '__main__':
    process_data('initial_data_1cat copy.json', iterations=50) 
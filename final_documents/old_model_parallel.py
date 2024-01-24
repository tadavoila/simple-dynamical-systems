import random
import json
import shutil  # Import shutil for file copying

def process_data(json_file, iterations=10):
    for iter_num in range(iterations):
        # Duplicate the initial data file for each iteration
        duplicated_file = f'initial_data_copy_{iter_num + 1}.json'
        shutil.copy(json_file, duplicated_file)

        averages_1_to_6 = {}  # Dictionary to store averages_1_to_6 for the current iteration
        averages_7_to_12 = {}  # Dictionary to store averages_7_to_12 for the current iteration

        # Open the duplicated JSON file
        with open(duplicated_file) as json_data:
            data = json.load(json_data, strict=False)

        # Access the 'words' section within the JSON data
        words = data["Category"]["words"]

        # Loop through the process _ times
        for i in range(10000):
            word_frequencies = {}

            # Extract word frequencies from the data
            for key, value in words.items():
                frequency = value["frequency"]
                word_frequencies[key] = frequency

            # Calculate the total frequency
            total_frequency = sum(word_frequencies.values())

            # Calculate the probabilities of each word
            word_probabilities = {}
            for key, freq in word_frequencies.items():
                prob = freq / total_frequency
                word_probabilities[key] = prob

            # Randomly select a word based on probabilities
            chosen_word = random.choices(list(word_probabilities.keys()), list(word_probabilities.values()))[0]

            exemplars_lst = words[chosen_word]["exemplars"]
            chosen_exemplar = random.choice(exemplars_lst)

            frequency_of_word = words[chosen_word]["frequency"]

            newExemplar = chosen_exemplar + 0.1

            exemplars_lst.append(newExemplar)
            exemplars_lst.pop(random.randrange(len(exemplars_lst)))

            words[chosen_word]["exemplars"] = exemplars_lst

            final_average = sum(exemplars_lst) / len(exemplars_lst)

            if 1 <= frequency_of_word <= 6:
                averages_1_to_6[i] = final_average
            elif 7 <= frequency_of_word <= 12:
                averages_7_to_12[i] = final_average

            if "means" not in words[chosen_word]:
                words[chosen_word]["means"] = []

            mean_dict = {i: final_average}
            words[chosen_word]["means"].append(mean_dict)

        # Write the averages dictionaries to JSON files for the current iteration
        json_file_1_to_6 = f'averages_1_to_6_{iter_num + 1}.json'
        with open(json_file_1_to_6, 'w') as json_data:
            json.dump(averages_1_to_6, json_data, indent=4)

        json_file_7_to_12 = f'averages_7_to_12_{iter_num + 1}.json'
        with open(json_file_7_to_12, 'w') as json_data:
            json.dump(averages_7_to_12, json_data, indent=4)

        # Write the updated data back to the duplicated JSON file
        with open(duplicated_file, 'w') as json_data:
            json.dump(data, json_data, indent=4)

# Call the function with the initial JSON file and 10 iterations
process_data('initial_data_1cat copy.json', iterations=10)

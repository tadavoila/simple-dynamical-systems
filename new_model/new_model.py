import random
import json

def process_data(json_file):
    
    # Loop through the process _ times
    for i in range(100000):

        # Initialize list
        results_list = []

        # Open the JSON file
        with open(json_file) as json_data:
            data = json.load(json_data)

        # Access the 'words' section within the JSON data
        words = data["Category"]["words"]

        # Create a dictionary to store word frequencies
        word_frequencies = {}

        # Extract word frequencies from the data
        for keyy, valuee in words.items():
            frequency = valuee["frequency"]
            word_frequencies[keyy] = frequency

        # Calculate the total frequency
        total_frequency = sum(word_frequencies.values())

        # Calculate the probabilities of each word
        word_probabilities = {}
        for key, freq in word_frequencies.items():
            prob = freq / total_frequency
            word_probabilities[key] = prob

        # Randomly select a word based on probabilities
        key = random.choices(list(word_probabilities.keys()), list(word_probabilities.values()))[0]

       


        # Access the selected word's data
        exemplars_lst = words[key]["exemplars"]
        chosen_exemplar = random.choice(list(exemplars_lst.keys()))

        # Increment the value associated with the chosen exemplar key
        exemplars_lst[chosen_exemplar] += 1

        # Write the updated data back to the JSON file
        with open(json_file, 'w') as json_data:
            json.dump(data, json_data, indent=4)

process_data('initial_data_1cat copy 3.json')





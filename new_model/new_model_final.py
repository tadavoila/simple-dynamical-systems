import random
import json

averages_1_to_6 = {}
averages_7_to_12 = {}

def normalize_exemplars(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        json_data = file.read()

    # Parse JSON
    data = json.loads(json_data)

    max_value = float('-inf')
    max_exemplar = None

    # Find the maximum value
    for word, word_data in data["Category"]["words"].items():
        exemplars = word_data.get("exemplars", {})
        for exemplar, value in exemplars.items():
            if value > max_value:
                max_value = value
                max_exemplar = exemplar

    # Normalize exemplar values
    for word, word_data in data["Category"]["words"].items():
        exemplars = word_data.get("exemplars", {})
        for exemplar, value in exemplars.items():
            exemplars[exemplar] = value / max_value

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

file_path = 'initial_data_1cat copy 3.json'
normalized_data = normalize_exemplars(file_path)



def choose_weighted_exemplar(data, word):
    exemplars = data["Category"]["words"][word]["exemplars"]

    # Extract keys and corresponding weights
    keys, weights = zip(*exemplars.items())

    # Choose a key based on weights
    chosen_key = random.choices(keys, weights=weights)[0]

    # Convert the chosen key to a float
    chosen_key = float(chosen_key)

    return chosen_key






def process_data(json_file):
    
    # Loop through the process _ times
    for i in range(10000):

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
        key = random.choice(list(word_probabilities.keys()))

        # Get the frequency of the selected word
        frequency_of_word = words[key]["frequency"]


        # Access the selected word's data
        exemplars_dict = words[key]["exemplars"]
        chosen_exemplar = choose_weighted_exemplar(data, key)

        # Normalize exemplar values
        for word, word_data in data["Category"]["words"].items():
            exemplars = word_data.get("exemplars", {})
            for exemplar, value in exemplars.items():
                exemplars[exemplar] = value * 0.997967

        # Define a function to add a small increment to the average
        def addNum(chosen_exemplar) :
            newAvg = chosen_exemplar + 0.1
            return newAvg

        # Calculate the new average after the increment
        newExemplar = addNum(chosen_exemplar)


        # Add the value associated with the chosen exemplar key
        exemplars_dict[newExemplar] =  1


        #Have a tidy up step to make sure the data does not get too big, if the exemplar strength gets really small (less than 0.0001) and there are still other examples of that word then delete it. 
        for word, word_data in data["Category"]["words"].items():
            exemplars = word_data.get("exemplars", {})
            for exemplar, value in list(exemplars.items()):
                if value < 0.00000000000001 and len(exemplars) > 1:
                    del exemplars[exemplar]



        # Define a function to calculate the average of exemplars
        def averageExemplars(exemplars_dict):
            # Convert keys to float and then sum them
            sum_keys = sum(float(key) for key in exemplars_dict.keys())
            
            # Return the average
            return sum_keys / len(exemplars_dict)

        # Calculate the final average of exemplars
        finalAverage = averageExemplars(exemplars_dict)

        if 1 <= frequency_of_word <= 6:
            averages_1_to_6[i] = finalAverage
        elif 7 <= frequency_of_word <= 12:
            averages_7_to_12[i] = finalAverage

        # Check if 'means' key exists in the chosen word's data
        if "means" not in words[key]:
            words[key]["means"] = []

        mean_dict = {i: finalAverage}
        # Append the final average to the 'means' list
        words[key]["means"].append(mean_dict)

        # Write the updated data back to the JSON file
        with open(json_file, 'w') as json_data:
            json.dump(data, json_data, indent=4)

    json_file_new_1_to_6_1 = 'new_averages_1_to_6_1.json'
    json_file_new_7_to_12_1 = 'new_averages_7_to_12_1.json'

    # Save averages_1_to_6 dictionary to JSON file
    with open(json_file_new_1_to_6_1, 'w') as json_data:
        json.dump(averages_1_to_6, json_data, indent=4)

    # Save averages_7_to_12 dictionary to JSON file
    with open(json_file_new_7_to_12_1, 'w') as json_data:
        json.dump(averages_7_to_12, json_data, indent=4)


      

       

process_data('initial_data_1cat copy 4.json')





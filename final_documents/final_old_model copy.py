import random
import json

def process_data(json_file):
    averages_1_to_6 = {}
    averages_7_to_12 = {}

    # Loop through the process _ times
    for i in range(10):


        # Open the JSON file
        with open(json_file) as json_data:
            data = json.load(json_data)

        # Access the 'words' section within the JSON data
        words = data["Category"]["words"]

        # Create a dictionary to store word frequencies
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

        # Access the selected word's data
        exemplars_dict = words[chosen_word]["exemplars"]
        chosen_exemplar = random.choice(list(exemplars_dict))
        print(chosen_exemplar.value())
        

        # Get the frequency of the selected word
        frequency_of_word = words[chosen_word]["frequency"]

        # Define a function to add a small increment to the average
        def addNum(chosen_exemplar) :
            chosen_exemplar_float = float(chosen_exemplar.value())
            newAvg = chosen_exemplar_float * (1-(1/492))
            return newAvg

        # Calculate the new average after the increment
        newExemplar = addNum(chosen_exemplar)
        print(newExemplar)

        # Add the new average to exemplars 
        words[chosen_word]["exemplars"][].append(newExemplar)


        # Update the exemplars list in the data
        words[chosen_word]["exemplars"] = exemplars_dict

        # Define a function to calculate the average of exemplars
        def averageExemplars(exemplars_dict):
            return sum(exemplars_dict) / len(exemplars_dict)

        # Calculate the final average of exemplars
        finalAverage = averageExemplars(exemplars_dict)

        '''if 1 <= frequency_of_word <= 6:
            averages_1_to_6[i] = finalAverage
        elif 7 <= frequency_of_word <= 12:
            averages_7_to_12[i] = finalAverage

        # Check if 'means' key exists in the chosen word's data
        if "means" not in words[chosen_word]:
            words[chosen_word]["means"] = []

        mean_dict = {i: finalAverage}
        # Append the final average to the 'means' list
        words[chosen_word]["means"].append(mean_dict)

        # Write the updated data back to the JSON file
        with open(json_file, 'w') as json_data:
            json.dump(data, json_data, indent=4)

    json_file_1_to_6_10 = 'averages_1_to_6_10.json'
    json_file_7_to_12_10 = 'averages_7_to_12_10.json'

    # Save averages_1_to_6 dictionary to JSON file
    with open(json_file_1_to_6_10, 'w') as json_data:
        json.dump(averages_1_to_6, json_data, indent=4)

    # Save averages_7_to_12 dictionary to JSON file
    with open(json_file_7_to_12_10, 'w') as json_data:
        json.dump(averages_7_to_12, json_data, indent=4)'''





process_data('initial_data_1cat copy.json')
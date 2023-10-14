import random
import json


# Define the JSON file path
json_file = 'initial_data_1cat copy 2.json'

# Loop through the process _ times
for i in range(100000):

    # Initialize result and averages lists
    results_list = []

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
    mean = words[chosen_word]
    exemplars_lst = words[chosen_word]["exemplars"]

    # Define a function to calculate the average of exemplars
    def averageExemplars(exemplars_lst):
        return sum(exemplars_lst) / len(exemplars_lst)

    # Calculate the average of exemplars
    average = averageExemplars(exemplars_lst)

    # Get the frequency of the selected word
    frequency_of_word = words[chosen_word]["frequency"]

    # Define a function to add a small increment to the average
    def averageAdd(average, frequency_of_word) :
        newAvg = average + 0.1/frequency_of_word
        return newAvg

    # Calculate the new average after the increment
    newAvgg = averageAdd(average, frequency_of_word)

    # Add the new average to exemplars and remove a random value
    exemplars_lst.append(newAvgg) 
    exemplars_lst.pop(random.randrange(len(exemplars_lst))) 

    # Update the exemplars list in the data
    words[chosen_word]["exemplars"] = exemplars_lst

    # Calculate the final average of exemplars
    finalAverage = averageExemplars(exemplars_lst)

    # Check if 'means' key exists in the chosen word's data
    if "means" not in words[chosen_word]:
        words[chosen_word]["means"] = []

    mean_dict = {i: finalAverage}
    # Append the final average to the 'means' list
    words[chosen_word]["means"].append(mean_dict)

    # Write the updated data back to the JSON file
    with open(json_file, 'w') as json_data:
        json.dump(data, json_data, indent = 4)





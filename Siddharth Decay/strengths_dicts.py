import random
import json
import dataclasses
from dataclasses import dataclass
from multiprocessing import Pool

def reset_data():
    # Read the initial data file
    original_file = 'Siddharth Decay/Data/initial_data_1cat.json'
    with open(original_file, 'r') as file:
        data = json.load(file)

    # Process the 'words' data
    words_data = data['Category']['words']
    processed_data = {}
    for word_key, attributes in words_data.items():
        processed_data[word_key] = {
            'frequency': attributes['frequency'],
            'exemplars': attributes['exemplars']
        }

    # Save the processed data to a new JSON file
    pivoted_data_path = "Siddharth Decay/Data/pivoted_data.json"
    with open(pivoted_data_path, 'w') as file:
        json.dump(processed_data, file)

    return pivoted_data_path

@dataclass
class ExemplarData:
    word_key: str
    exemplar: str
    exemplar_index: int
    frequency: int
    exemplar_strength: float

    @staticmethod
    def add_exemplar(exemplar_data_list, chosen_word, new_exemplar, exemplar_index, frequency):
        exemplar_data_list.append(
            ExemplarData(
                word_key=chosen_word,
                exemplar=new_exemplar,
                exemplar_index=exemplar_index,
                frequency=int(frequency),
                exemplar_strength=1
            )
        )

    @staticmethod
    def remove_weak_exemplars(exemplar_data_list):
        return [data for data in exemplar_data_list if data.exemplar_strength >= 1e-10]

    @staticmethod
    def get_weights(exemplar_data_list, chosen_word, exemplars_list):
        weights = [0] * len(exemplars_list)  # Initialize all weights to 0

        for idx, exemplar in enumerate(exemplars_list):
            for data in exemplar_data_list:
                if data.word_key == chosen_word and data.exemplar == exemplar and data.exemplar_index == idx:
                    weights[idx] += data.exemplar_strength  # Incrementing the weight

        # Replace any zero weights with 1 (default weight)
        weights = [weight if weight > 0 else 1 for weight in weights]

        return weights

def process_with_k_value(args):
    k_value, iterations, pivoted_data_path = args
    # Load the processed data
    with open(pivoted_data_path, 'r') as file:
        words_dict = json.load(file)
    
    words_data = list(words_dict.keys())
    frequencies = [word_info['frequency'] for word_info in words_dict.values()]

    exemplar_data_list = []
    for i in range(iterations):
        chosen_word = random.choices(words_data, weights=frequencies, k=1)[0]
        chosen_word_info = words_dict[chosen_word]  # Access the chosen word's data directly from the dictionary
        exemplars_list = chosen_word_info['exemplars']
        frequency = chosen_word_info['frequency']

        weights = ExemplarData.get_weights(exemplar_data_list, chosen_word, exemplars_list) 

        exemplar_index = random.choices(range(len(exemplars_list)), weights=weights, k=1)[0]
        new_exemplar = exemplars_list[exemplar_index]

        for data in exemplar_data_list:
            data.exemplar_strength *= k_value
                
        # Add the new exemplar to the chosen word
        ExemplarData.add_exemplar(exemplar_data_list, chosen_word, new_exemplar, exemplar_index, frequency)
        exemplar_data_list = ExemplarData.remove_weak_exemplars(exemplar_data_list)

    k_str = "{:06.5f}".format(k_value).replace('.', '')[1:]
    strengths_path = f"Siddharth Decay/Outputs/strengths_k{k_str}.json"
    
    with open(strengths_path, 'w') as f:
         json.dump([dataclasses.asdict(data) for data in exemplar_data_list], f)

def parallel_process_with_k_values(k_values, iterations):
    pivoted_data_path = reset_data()
    # Prepare arguments for pool processing
    args = [(k_value, iterations, pivoted_data_path) for k_value in k_values]
    
    with Pool(processes=10) as pool:
        pool.map(process_with_k_value, args)

if __name__ == "__main__":
    values = [x*10 for x in range(1, 101, 10)]
    k_values = [1 - 1/value for value in values] 
    iterations = 20000
    parallel_process_with_k_values(k_values, iterations)

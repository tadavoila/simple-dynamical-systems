import pandas as pd
import numpy as np
import random
import json
import dataclasses
from dataclasses import dataclass
import copy
import multiprocessing
from multiprocessing import Process

def reset_data():
    data = pd.read_json('Data/initial_data_1cat.json')
    
    # Extracting the 'words' data and flattening it
    words_data = pd.json_normalize(data['Category']['words'])

    # Transposing the DataFrame for better readability and structure
    words_data = words_data.transpose()

    # Resetting the index to have a proper DataFrame structure
    words_data.reset_index(inplace=True)

    # Splitting the 'index' column to separate word keys from their properties
    words_data[['word_key', 'property']] = words_data['index'].str.split('.', expand=True)

    # Pivoting the table to have properties as columns
    pivoted_data = words_data.pivot(index='word_key', columns='property', values=0)

    # Resetting index for clarity
    pivoted_data.reset_index(inplace=True)

    # Saving the filtered data to JSON file
    pivoted_data_path = "Data/pivoted_data.json"
    pivoted_data.to_json(pivoted_data_path, orient='records', lines=True)
    
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

def process_with_k_value(k_value, iterations):
    pivoted_data_path = reset_data()

    # Load the DataFrame once outside the loop
    df = pd.read_json(pivoted_data_path, orient='records', lines=True)
    
    print (k_value, df.columns)

    words_data = df['word_key'].tolist()
    frequencies = df['frequency'].astype(int).tolist()

    exemplar_data_list = []
    for i in range(iterations):
        chosen_word = random.choices(words_data, weights=frequencies, k=1)[0]
        chosen_row = df[df['word_key'] == chosen_word].iloc[0]  # Get the row for the chosen word
        exemplars_list = chosen_row['exemplars']
        frequency = chosen_row['frequency']

        weights = ExemplarData.get_weights(exemplar_data_list, chosen_word, exemplars_list)

        exemplar_index = random.choices(range(len(exemplars_list)), weights=weights, k=1)[0]
        new_exemplar = exemplars_list[exemplar_index]

        for data in exemplar_data_list:
            data.exemplar_strength *= k_value

        ExemplarData.add_exemplar(exemplar_data_list, chosen_word, new_exemplar, exemplar_index, frequency)
        exemplar_data_list = ExemplarData.remove_weak_exemplars(exemplar_data_list)

        # Test
        #print(i, k_value)

    k_str = str(round(k_value, 5)).replace('.', '')[1:]
    strengths_path = f"Outputs/strengths_k{k_str}.json"
    
    with open(strengths_path, 'w') as f:
        json.dump([dataclasses.asdict(data) for data in exemplar_data_list], f)

def parallel_process_with_k_values(k_values, iterations):
    processes = []

    for k_value in k_values:
        process = Process(target=process_with_k_value, args=(k_value, iterations))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    k_values = [1 - 7/492 + i*0.001 for i in range(10)]  # Example of 10 different k values
    iterations = 20000
    parallel_process_with_k_values(k_values, iterations)
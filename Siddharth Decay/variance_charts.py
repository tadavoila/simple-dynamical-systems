import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the averaged variances for bins 1-6 and 7-12 separately."""
    all_variances = {'variances_1_6_new': [], 'variances_7_12_new': []}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Summer_k/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Calculate the average for bins 1-6 and 7-12
        variances_1_6 = pd.concat([pd.Series(data[f'variances_{i}_new']) for i in range(1, 7)], axis=1).mean(axis=1)
        variances_7_12 = pd.concat([pd.Series(data[f'variances_{i}_new']) for i in range(7, 13)], axis=1).mean(axis=1)

        all_variances['variances_1_6_new'].append(variances_1_6)
        all_variances['variances_7_12_new'].append(variances_7_12)

    # Average variances across all runs
    averaged_variances = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_variances.items()}

    return averaged_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the averaged variances over iterations for bins 1-6 and bins 7-12."""
    fig_1_6 = go.Figure()
    fig_7_12 = go.Figure()
    x_values = list(range(1, 10001))  # X-axis from 1 to 10000

    # Define the 10 colors
    colors = [
        "#87CEEB",  # Sky Blue
        "#DC143C",  # Crimson Red
        "#DAA520",  # Goldenrod Yellow
        "#228B22",  # Forest Green
        "#800080",  # Deep Purple
        "#FF4500",  # Orange Red
        "#008080",  # Teal
        "#4169E1",  # Royal Blue
        "#FF00FF",  # Magenta
        "#708090"   # Slate Gray
    ]

    for idx, (k_str, variances) in enumerate(tqdm(all_variances.items(), desc='Plotting variances')):
        color = colors[idx % len(colors)]  # Cycle through the colors
        value_used = values[idx]  # Get the corresponding value used to create k_value

        fig_1_6.add_trace(go.Scatter(
            x=x_values,
            y=variances['variances_1_6_new'].iloc[:20000],
            mode='lines',
            name=f'k = {value_used}',
            line=dict(color=color)
        ))

        fig_7_12.add_trace(go.Scatter(
            x=x_values,
            y=variances['variances_7_12_new'].iloc[:20000],
            mode='lines',
            name=f'k = {value_used}',
            line=dict(color=color)
        ))

    fig_1_6.update_layout(
        title=f'Average {var_type} for Bins 1-6 over Iterations',
        xaxis_title='Iteration',
        yaxis_title=f'{var_type} Variances',
        font=dict(family="Arial", size=12, color="Black")
    )

    fig_7_12.update_layout(
        title=f'Average {var_type} for Bins 7-12 over Iterations',
        xaxis_title='Iteration',
        yaxis_title=f'{var_type} Variances',
        font=dict(family="Arial", size=12, color="Black")
    )

    py.plot(fig_1_6, filename=f'Siddharth Decay Charts/{var_type.lower()}_plot_1_6.html')
    py.plot(fig_7_12, filename=f'Siddharth Decay Charts/{var_type.lower()}_plot_7_12.html')

if __name__ == '__main__':
    runs = 10  # Number of runs per k_value
    values = [x*10 for x in range(1, 101, 10)]
    k_values = [1 - 1/value for value in values]
    k_strings = ["{:06.5f}".format(k_value).replace('.', '')[1:] for k_value in k_values]

    all_variances = {}
    for k_str in tqdm(k_strings, desc='Loading and processing data'):
        averaged_variances = load_and_process_data(k_str, runs)
        all_variances[k_str] = averaged_variances

    plot_variances(all_variances, values, var_type='Variances')

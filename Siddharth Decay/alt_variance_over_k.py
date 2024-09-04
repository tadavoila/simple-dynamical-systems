import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the averaged variances for bins 1-6 and 7-12 separately."""
    all_variances = {f'alt_variances_{i}_new': [] for i in range(1, 13)}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Collect variances for bins 1-12
        for i in range(1, 13):
            variances = pd.Series(data[f'alt_variances_{i}_new'])
            all_variances[f'alt_variances_{i}_new'].append(variances)

    # Average variances across all runs
    averaged_variances = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_variances.items()}

    return averaged_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the averaged variances over different k values for bins 1-12 on a single plot."""
    fig = go.Figure()

    # Define the 12 colors
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
        "#708090",  # Slate Gray
        "#A52A2A",  # Brown
        "#FFD700"   # Gold
    ]

    # Plot each bin's variance against the values used to create the k_values
    for i in range(1, 13):
        bin_label = f'Bin {i}'
        color = colors[i-1]  # Select color for the current bin
        y_values = [all_variances[k_str][f'alt_variances_{i}_new'].mean() for k_str in all_variances.keys()]
        
        fig.add_trace(go.Scatter(
            x=values,
            y=y_values,
            mode='lines+markers',
            name=bin_label,
            line=dict(color=color)
        ))

    fig.update_layout(
        title=f'Average {var_type} for Bins 1-12 across Different k Values',
        xaxis_title='Value Used to Create k',
        yaxis_title=f'{var_type}',
        font=dict(family="Arial", size=12, color="Black"),
        height=600,
        showlegend=True
    )

    py.plot(fig, filename=f'Siddharth Decay/Siddharth Decay Charts/alt_{var_type.lower()}_plot_over_k.html')

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

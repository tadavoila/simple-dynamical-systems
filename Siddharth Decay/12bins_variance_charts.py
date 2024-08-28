import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm
from plotly.subplots import make_subplots

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the variances for each of the 12 bins separately."""
    all_variances = {f'variances_{i}_new': [] for i in range(1, 13)}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Store the variances for each bin separately
        for i in range(1, 13):
            all_variances[f'variances_{i}_new'].append(pd.Series(data[f'variances_{i}_new']))

    return all_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the variances over iterations for each of the 12 bins as subplots."""
    fig = make_subplots(rows=4, cols=3, subplot_titles=[f'Bin {i}' for i in range(1, 13)])
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

        for bin_num in range(1, 13):
            row = (bin_num - 1) // 3 + 1
            col = (bin_num - 1) % 3 + 1
            
            fig.add_trace(go.Scatter(
                x=x_values,
                y=pd.concat(variances[f'variances_{bin_num}_new'], axis=1).mean(axis=1)[:20000],
                mode='lines',
                name=f'k = {value_used}',
                line=dict(color=color)
            ), row=row, col=col)

    fig.update_layout(
        title=f'{var_type} for All Bins over Iterations',
        xaxis_title='Iteration',
        yaxis_title=f'{var_type} Variances',
        font=dict(family="Arial", size=12, color="Black"),
        height=1200,  # Adjust height for better readability
        showlegend=False  # Hide the legend to avoid clutter
    )

    py.plot(fig, filename=f'Siddharth Decay/Siddharth Decay Charts/12bins_{var_type.lower()}_subplots.html')

if __name__ == '__main__':
    runs = 10  # Number of runs per k_value
    values = [x*10 for x in range(1, 101, 10)]
    k_values = [1 - 1/value for value in values]
    k_strings = ["{:06.5f}".format(k_value).replace('.', '')[1:] for k_value in k_values]

    all_variances = {}
    for k_str in tqdm(k_strings, desc='Loading and processing data'):
        variances = load_and_process_data(k_str, runs)
        all_variances[k_str] = variances

    plot_variances(all_variances, values, var_type='Variances')

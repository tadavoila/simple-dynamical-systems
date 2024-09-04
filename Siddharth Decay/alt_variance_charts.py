import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm
from plotly.subplots import make_subplots

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the averaged variances for bins 1-6 and 7-12 separately."""
    all_variances = {'variances_1_6_new': [], 'variances_7_12_new': []}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Calculate the average for bins 1-6 and 7-12
        variances_1_6 = pd.concat([pd.Series(data[f'alt_variances_{i}_new']) for i in range(1, 7)], axis=1).mean(axis=1)
        variances_7_12 = pd.concat([pd.Series(data[f'alt_variances_{i}_new']) for i in range(7, 13)], axis=1).mean(axis=1)

        all_variances['variances_1_6_new'].append(variances_1_6)
        all_variances['variances_7_12_new'].append(variances_7_12)

    # Average variances across all runs
    averaged_variances = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_variances.items()}

    return averaged_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the averaged variances over iterations for bins 1-6 and bins 7-12 as subplots in a single figure."""
    fig = make_subplots(rows=2, cols=1, subplot_titles=[
        f'Average {var_type} for Bins 1-6 over Iterations',
        f'Average {var_type} for Bins 7-12 over Iterations'
    ])
    
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

        # Plot for bins 1-6
        fig.add_trace(go.Scatter(
            x=x_values,
            y=variances['variances_1_6_new'].iloc[:20000],
            mode='lines',
            name=f'k = {value_used}',
            line=dict(color=color)
        ), row=1, col=1)

        # Plot for bins 7-12 without legend
        fig.add_trace(go.Scatter(
            x=x_values,
            y=variances['variances_7_12_new'].iloc[:20000],
            mode='lines',
            name=f'k = {value_used}',
            line=dict(color=color),
            showlegend=False  # Hide the legend for the second subplot
        ), row=2, col=1)

    fig.update_layout(
        title=f'Average alternate {var_type} for Bins 1-6 and Bins 7-12 over Iterations',
        xaxis_title='Iteration',
        yaxis_title=f'{var_type}',
        yaxis2_title=f'{var_type}',
        font=dict(family="Arial", size=12, color="Black"),
        height=800,  # Adjust height for better readability
        showlegend=True  # Show legend only once (in the first subplot)
    )

    py.plot(fig, filename=f'Siddharth Decay/Siddharth Decay Charts/alt_{var_type.lower()}_plot_avg_2bins.html')

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

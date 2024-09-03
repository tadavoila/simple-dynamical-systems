import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm
from plotly.subplots import make_subplots

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the adjusted variances (relative to each file's initial variance) for each of the 12 bins separately."""
    all_variances = {f'variances_{i}_new': [] for i in range(1, 13)}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Adjust variances for each bin
        for i in range(1, 13):
            series = pd.Series(data[f'variances_{i}_new'])
            initial_variance = series.iloc[0]
            adjusted_variance = series - initial_variance
            all_variances[f'variances_{i}_new'].append(adjusted_variance)

    return all_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the adjusted variances over iterations for each of the 12 bins as subplots, including a baseline at y=0."""
    fig = make_subplots(rows=4, cols=3, subplot_titles=[f'Bin {i}' for i in range(1, 13)])
    x_values = list(range(1, 10001))  # X-axis from 1 to 10000

    # Define the 9 colors
    colors = [
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

    # Loop through each bin and add traces for each k value
    for bin_num in range(1, 13):
        row = (bin_num - 1) // 3 + 1
        col = (bin_num - 1) % 3 + 1
        
        for idx, (k_str, variances) in enumerate(tqdm(all_variances.items(), desc='Plotting variances')):
            color = colors[idx % len(colors)]  # Cycle through the colors
            value_used = values[idx]  # Get the corresponding value used to create k_value
            
            # Show legend only for the first subplot (first bin)
            show_legend = (bin_num == 1)

            fig.add_trace(go.Scatter(
                x=x_values,
                y=pd.concat(variances[f'variances_{bin_num}_new'], axis=1).mean(axis=1)[:20000],
                mode='lines',
                name=f'k = {value_used}',
                line=dict(color=color),
                showlegend=show_legend  # Show legend for the first subplot only
            ), row=row, col=col)

        # Add baseline to each subplot after the k-value traces
        fig.add_trace(go.Scatter(
            x=x_values,
            y=[0] * len(x_values),
            mode='lines',
            name='Baseline' if show_legend else '',
            line=dict(color='black', width=2, dash='dash'),
            showlegend=show_legend
        ), row=row, col=col)

    fig.update_layout(
        title=f'{var_type} Difference from Initial Variance for All Bins over Iterations (k > 110)',
        xaxis_title='Iteration',
        yaxis_title=f'Variance Difference',
        font=dict(family="Arial", size=12, color="Black"),
        height=1200,  # Adjust height for better readability
    )

    py.plot(fig, filename=f'Siddharth Decay/Siddharth Decay Charts/12bins_var_difference_subplots_kge110.html')


if __name__ == '__main__':
    runs = 10  # Number of runs per k_value
    values = [x*10 for x in range(11, 101, 10)]
    k_values = [1 - 1/value for value in values]
    k_strings = ["{:06.5f}".format(k_value).replace('.', '')[1:] for k_value in k_values]

    all_variances = {}
    for k_str in tqdm(k_strings, desc='Loading and processing data'):
        variances = load_and_process_data(k_str, runs)
        all_variances[k_str] = variances

    plot_variances(all_variances, values, var_type='Variances')

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm
from plotly.subplots import make_subplots

def load_and_process_data(runs):
    """Load data from all runs and return the means for each of the 12 bins separately."""
    all_means = {f'means_{i}_new': [] for i in range(1, 13)}

    for run_number in tqdm(range(runs), desc=f'Processing runs'):
        file_path = f'Siddharth Overwriting Model/all_data_run{run_number}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Store the means for each bin separately
        for i in range(1, 13):
            all_means[f'means_{i}_new'].append(pd.Series(data[f'means_{i}_new']))

    # Average means across all runs for each bin
    averaged_means = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_means.items()}

    return averaged_means

def plot_means(averaged_means, iterations=10000):
    """Plot the means over iterations for each of the 12 bins as subplots."""
    fig = make_subplots(rows=4, cols=3, subplot_titles=[f'Bin {i}' for i in range(1, 13)])
    x_values = list(range(1, iterations + 1))  # X-axis from 1 to the number of iterations

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
        "#5F9EA0",  # Cadet Blue
    ]

    for bin_num in range(1, 13):
        row = (bin_num - 1) // 3 + 1
        col = (bin_num - 1) % 3 + 1
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=averaged_means[f'means_{bin_num}_new'].iloc[:iterations],
            mode='lines',
            name=f'Bin {bin_num}',
            line=dict(color=colors[bin_num - 1])
        ), row=row, col=col)

    fig.update_layout(
        title='Means for All Bins over Iterations',
        xaxis_title='Iteration',
        yaxis_title='Mean Value',
        font=dict(family="Arial", size=12, color="Black"),
        height=1200,  # Adjust height for better readability
        showlegend=False  # Hide the legend to avoid clutter
    )

    py.plot(fig, filename=f'Siddharth Overwriting Charts/12bin_means_subplots.html')

if __name__ == '__main__':
    runs = 100  # Number of runs
    iterations = 10000  # Number of iterations per run

    averaged_means = load_and_process_data(runs)
    plot_means(averaged_means, iterations)

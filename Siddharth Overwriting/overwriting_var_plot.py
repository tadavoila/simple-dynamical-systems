import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm

def load_and_process_data(runs):
    """Load data from all runs and return the averaged variances for bins 1-6 and 7-12."""
    all_variances = {'variances_1_6_new': [], 'variances_7_12_new': []}

    for run_number in tqdm(range(runs), desc=f'Processing runs'):
        file_path = f'Siddharth Overwriting Model/all_data_run{run_number}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Calculate the average variance for bins 1-6 and 7-12
        variances_1_6 = pd.concat([pd.Series(data[f'variances_{i}_new']) for i in range(1, 7)], axis=1).mean(axis=1)
        variances_7_12 = pd.concat([pd.Series(data[f'variances_{i}_new']) for i in range(7, 13)], axis=1).mean(axis=1)

        all_variances['variances_1_6_new'].append(variances_1_6)
        all_variances['variances_7_12_new'].append(variances_7_12)

    # Average variances across all runs
    averaged_variances = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_variances.items()}

    return averaged_variances

def plot_variances(averaged_variances, iterations=10000):
    """Plot the averaged variances for bins 1-6 and bins 7-12."""
    fig = go.Figure()

    x_values = np.arange(1, iterations + 1)

    # Plot averaged variances for bins 1-6
    fig.add_trace(go.Scatter(
        x=x_values,
        y=averaged_variances['variances_1_6_new'].iloc[:iterations],
        mode='lines',
        name='Bins 1-6 (Average Variances)',
        line=dict(color='blue')
    ))

    # Plot averaged variances for bins 7-12
    fig.add_trace(go.Scatter(
        x=x_values,
        y=averaged_variances['variances_7_12_new'].iloc[:iterations],
        mode='lines',
        name='Bins 7-12 (Average Variances)',
        line=dict(color='red')
    ))

    fig.update_layout(
        title='Averaged Variances for Bins 1-6 and Bins 7-12',
        xaxis_title='Iteration',
        yaxis_title='Average Variance',
        font=dict(family="Arial", size=12, color="Black"),
        height=600,
        showlegend=True
    )

    py.plot(fig, filename='Siddharth Overwriting Charts/variances_avg_2bins.html')

if __name__ == '__main__':
    runs = 100  # Number of runs
    iterations = 10000  # Number of iterations per run

    averaged_variances = load_and_process_data(runs)
    plot_variances(averaged_variances, iterations)

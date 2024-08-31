import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm

def load_and_process_data(runs):
    """Load data from all runs and return the averaged means for bins 1-6 and 7-12."""
    all_means = {'means_1_6_new': [], 'means_7_12_new': []}

    for run_number in tqdm(range(runs), desc=f'Processing runs'):
        file_path = f'Siddharth Overwriting Model/all_data_run{run_number}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Calculate the average for bins 1-6 and 7-12
        means_1_6 = pd.concat([pd.Series(data[f'means_{i}_new']) for i in range(1, 7)], axis=1).mean(axis=1)
        means_7_12 = pd.concat([pd.Series(data[f'means_{i}_new']) for i in range(7, 13)], axis=1).mean(axis=1)

        all_means['means_1_6_new'].append(means_1_6)
        all_means['means_7_12_new'].append(means_7_12)

    # Average means across all runs
    averaged_means = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_means.items()}

    return averaged_means

def plot_means_with_difference_regression(averaged_means, iterations=10000):
    """Plot the averaged means for bins 1-6 and bins 7-12 along with the regression difference curve."""
    fig = go.Figure()

    x_values = np.arange(1, iterations + 1)

    # Plot averaged means for bins 1-6
    fig.add_trace(go.Scatter(
        x=x_values,
        y=averaged_means['means_1_6_new'].iloc[:iterations],
        mode='lines',
        name='Bins 1-6 (Average Means)',
        line=dict(color='blue')
    ))

    # Plot averaged means for bins 7-12
    fig.add_trace(go.Scatter(
        x=x_values,
        y=averaged_means['means_7_12_new'].iloc[:iterations],
        mode='lines',
        name='Bins 7-12 (Average Means)',
        line=dict(color='red')
    ))

    # Calculate the difference between the averaged means
    difference_means = averaged_means['means_7_12_new'].iloc[:iterations] - averaged_means['means_1_6_new'].iloc[:iterations]

    # Apply and plot regression on the difference
    slope_diff, intercept_diff = np.polyfit(x_values, difference_means, 1)
    regression_diff = slope_diff * x_values + intercept_diff

    fig.add_trace(go.Scatter(
        x=x_values,
        y=regression_diff,
        mode='lines',
        name='Difference Regression Curve',
        line=dict(color='purple', dash='dash')
    ))

    fig.update_layout(
        title='Averaged Means for Bins 1-6 and Bins 7-12 with Regression Difference Curve',
        xaxis_title='Iteration',
        yaxis_title='Average Mean / Regression Difference',
        font=dict(family="Arial", size=12, color="Black"),
        height=600,
        showlegend=True
    )

    py.plot(fig, filename='Siddharth Overwriting Charts/means_avg_2bins.html')

if __name__ == '__main__':
    runs = 100  # Number of runs
    iterations = 10000  # Number of iterations per run

    averaged_means = load_and_process_data(runs)
    plot_means_with_difference_regression(averaged_means, iterations)

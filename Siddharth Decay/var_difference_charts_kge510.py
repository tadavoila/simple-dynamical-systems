import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py
import json
from tqdm import tqdm
from plotly.subplots import make_subplots

def load_and_process_data(k_str, runs):
    """Load data for a given k_str and return the adjusted variances (relative to each file's initial variance) for bins 1-6 and 7-12 separately."""
    all_variances = {'variances_1_6_new': [], 'variances_7_12_new': []}

    for run_number in tqdm(range(runs), desc=f'Processing runs for k={k_str}'):
        file_path = f'Siddharth Decay/Siddharth Decay Model/all_data_r{run_number}_k{k_str}.json'
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Adjust variances for bins 1-6
        variances_1_6 = []
        for i in range(1, 7):
            series = pd.Series(data[f'variances_{i}_new'])
            initial_variance = series.iloc[0]
            adjusted_variance = series - initial_variance
            variances_1_6.append(adjusted_variance)
        variances_1_6 = pd.concat(variances_1_6, axis=1).mean(axis=1)

        # Adjust variances for bins 7-12
        variances_7_12 = []
        for i in range(7, 13):
            series = pd.Series(data[f'variances_{i}_new'])
            initial_variance = series.iloc[0]
            adjusted_variance = series - initial_variance
            variances_7_12.append(adjusted_variance)
        variances_7_12 = pd.concat(variances_7_12, axis=1).mean(axis=1)

        all_variances['variances_1_6_new'].append(variances_1_6)
        all_variances['variances_7_12_new'].append(variances_7_12)

    # Average variances across all runs
    averaged_variances = {key: pd.concat(value, axis=1).mean(axis=1) for key, value in all_variances.items()}

    return averaged_variances

def plot_variances(all_variances, values, var_type='Regular'):
    """Plot the adjusted variances over iterations for bins 1-6 and bins 7-12 as subplots in a single figure, including a baseline at y=0."""
    fig = make_subplots(rows=2, cols=1, subplot_titles=[
        f'Average Variance Difference for Bins 1-6 over Iterations',
        f'Average Variance Difference for Bins 7-12 over Iterations'
    ])
    
    x_values = list(range(1, 10001))  # X-axis from 1 to 10000

    # Define the colors
    colors = [
        "#FF4500",  # Orange Red
        "#008080",  # Teal
        "#4169E1",  # Royal Blue
        "#FF00FF",  # Magenta
        "#708090"   # Slate Gray
    ]

    # Add baseline to both subplots but only show once in legend
    for row in range(1, 3):
        fig.add_trace(go.Scatter(
            x=x_values,
            y=[0] * len(x_values),
            mode='lines',
            name='Baseline',
            showlegend= row == 1,
            line=dict(color='black', width=2, dash='dash')
        ), row=row, col=1)

    # Plot variances with specified colors
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
        title=f'Average Variance Difference for Bins 1-6 and Bins 7-12 over Iterations (k >= 510)',
        xaxis_title='Iteration',
        yaxis_title=f'Variance Difference',
        yaxis2_title=f'Variance Difference',
        font=dict(family="Arial", size=12, color="Black"),
        height=800,  # Adjust height for better readability
        showlegend=True  # Show legend only once (in the first subplot)
    )

    py.plot(fig, filename=f'Siddharth Decay/Siddharth Decay Charts/var_difference_plot_avg_2bins_kge510.html')


if __name__ == '__main__':
    runs = 10  # Number of runs per k_value
    values = [x*10 for x in range(51, 101, 10)]
    k_values = [1 - 1/value for value in values]
    k_strings = ["{:06.5f}".format(k_value).replace('.', '')[1:] for k_value in k_values]

    all_variances = {}
    for k_str in tqdm(k_strings, desc='Loading and processing data'):
        averaged_variances = load_and_process_data(k_str, runs)
        all_variances[k_str] = averaged_variances

    plot_variances(all_variances, values, var_type='Variances')

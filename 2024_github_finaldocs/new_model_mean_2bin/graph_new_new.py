'''from plotly import graph_objs as go
import json
import numpy as np

# Define the file paths and their respective labels
file_path1 = ["new_averages_1_to_6_0.json", "new_averages_1_to_6_1.json", "new_averages_1_to_6_2.json", "new_averages_1_to_6_3.json", "new_averages_1_to_6_4.json"]
file_path2 = ["new_averages_7_to_12_0.json", "new_averages_7_to_12_1.json", "new_averages_7_to_12_2.json", "new_averages_7_to_12_3.json", "new_averages_7_to_12_4.json"]
def process_files(file_paths):
    file_data = []

    for path in file_paths:
        with open(path, 'r') as file:
            file_data.append(json.load(file))

    # Combine all data into one dictionary
    combined_data = {}
    for data in file_data:
        combined_data.update(data)

    # Calculate Averages for Each 10 Iterations
    total_averages = {}

    for i in range(0, 4000, 5):
        keys = [str(j) for j in range(i, i+10)]
        values = [combined_data.get(key) for key in keys]
        
        # Filter out None values and ensure the list is not empty
        values = [value for value in values if value is not None]
        
        if values:
            total_averages[f"{i+1}-{i+10}"] = sum(values) / len(values)
        else:
            total_averages[f"{i+1}-{i+10}"] = None
    
    return total_averages

result_1 = process_files(file_path1)
result_2 = process_files(file_path2)

# Extract x (iteration numbers) and y (average values)
x1 = list(result_1.keys())
y1 = list(result_1.values())
x2 = list(result_2.keys())
y2 = list(result_2.values())

# Calculate linear regression for dataset 1
x1_numeric = [int(item.split('-')[0]) for item in x1 if result_1[item] is not None]
slope1, intercept1 = np.polyfit(x1_numeric, [result_1[item] for item in x1 if result_1[item] is not None], 1)

# Create the linear regression line for dataset 1
x1_fit = np.array(x1_numeric)
y1_fit = slope1 * x1_fit + intercept1

# Create the plot
fig = go.Figure()

# Add the scatter plot of data points for dataset 1
fig.add_trace(go.Scatter(x=x1, y=y1, mode='markers', name='Low Frequency (1-6)', marker=dict(color='red')))

# Add the linear fit curve for dataset 1
fig.add_trace(go.Scatter(x=x1, y=y1_fit, mode='lines', name=f'Low Frequency (1-6)  slope = {slope1:.10f}', line=dict(color='orange')))

# Calculate linear regression for dataset 2
x2_numeric = [int(item.split('-')[0]) for item in x2 if result_2[item] is not None]
slope2, intercept2 = np.polyfit(x2_numeric, [result_2[item] for item in x2 if result_2[item] is not None], 1)

# Create the linear regression line for dataset 2
x2_fit = np.array(x2_numeric)
y2_fit = slope2 * x2_fit + intercept2

# Add the scatter plot of data points for dataset 2
fig.add_trace(go.Scatter(x=x2, y=y2, mode='markers', name='High Frequency (7-12)', marker=dict(color='blue')))

# Add the linear fit curve for dataset 2
fig.add_trace(go.Scatter(x=x2, y=y2_fit, mode='lines', name=f'High Frequency (7-12) slope = {slope2:.10f}', line=dict(color='green')))

# Update layout
fig.update_layout(
    title='Total Averages vs. Iteration',
    xaxis_title='Iteration',
    yaxis_title='Average Value',
)

# Calculate the y-values predicted by the regression lines for both datasets
y1_predicted = [slope1 * x + intercept1 for x in x1_numeric]
y2_predicted = [slope2 * x + intercept2 for x in x2_numeric]

# Calculate the difference between the predicted y-values
y_difference = [y2 - y1 for y1, y2 in zip(y1_predicted, y2_predicted)]

# Calculate the slope of the difference line
slope_difference = slope2 - slope1

# Add the difference curve
fig.add_trace(go.Scatter(x=x1, y=y_difference, mode='lines', name=f'Difference Curve, Slope = {slope_difference:.10f}', line=dict(color='purple')))

fig.show()
'''

'''from plotly import graph_objs as go
import pandas as pd
import numpy as np

# Define the CSV file paths

csv_paths = [f'averages_run{i}.csv' for i in range(20)]

# Function to process and combine CSV data
def process_csv_files(csv_paths):
    combined_df = pd.DataFrame()
    for path in csv_paths:
        df = pd.read_csv(path)
        if combined_df.empty:
            combined_df = df.copy()
        else:
            combined_df += df
    combined_df /= len(csv_paths)
    return combined_df

# Process the CSV files
averages_df = process_csv_files(csv_paths)

# Extract iteration numbers and average values
x = averages_df.index + 1
y1 = averages_df['FREQ_1_TO_6']
y2 = averages_df['FREQ_7_TO_12']

# Calculate linear regression for both datasets
slope1, intercept1 = np.polyfit(x, y1, 1)
slope2, intercept2 = np.polyfit(x, y2, 1)

# Create the linear regression lines
x_fit = np.array(x)
y1_fit = slope1 * x_fit + intercept1
y2_fit = slope2 * x_fit + intercept2

# Calculate the difference between the two regression lines
y_difference = y2_fit - y1_fit

# Create the plot
fig = go.Figure()

# Add the scatter plots for both datasets
fig.add_trace(go.Scatter(x=x, y=y1, mode='markers', name='Low Frequency (1-6)', marker=dict(color='red')))
fig.add_trace(go.Scatter(x=x, y=y2, mode='markers', name='High Frequency (7-12)', marker=dict(color='blue')))

# Add the linear fit curves for both datasets
fig.add_trace(go.Scatter(x=x, y=y1_fit, mode='lines', name=f'Low Frequency Fit, Slope = {slope1:.10f}', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=x, y=y2_fit, mode='lines', name=f'High Frequency Fit, Slope = {slope2:.10f}', line=dict(color='green')))

# Add the difference curve
fig.add_trace(go.Scatter(x=x, y=y_difference, mode='lines', name='Difference Curve', line=dict(color='purple', dash='dot')))

# Update layout
fig.update_layout(
    title='Group Averages vs. Iteration (Combined Runs) with Difference Curve',
    xaxis_title='Iteration',
    yaxis_title='Average Value / Difference',
)

fig.show()'''

from plotly import graph_objs as go
import pandas as pd
import numpy as np
import os
import re

slope_dict = {}

pattern = re.compile(r'averages_run\d+_decay_(\d+)\.csv')

# Step 1: Read all CSV files and collect slopes
for file in os.listdir('.'):
    match = pattern.match(file)
    if match:
        k = int(match.group(1))
        df = pd.read_csv(file)
        df['difference'] = df['FREQ_7_TO_12'] - df['FREQ_1_TO_6']
        x = np.arange(len(df)) * 100
        slope, intercept = np.polyfit(x, df['difference'], 1)
        
        if k not in slope_dict:
            slope_dict[k] = []
        slope_dict[k].append(slope)

# Step 2: Average the slopes for each k value
k_values = []
average_slopes = []
for k, slopes in slope_dict.items():
    average_slope = sum(slopes) / len(slopes)
    k_values.append(1 - 1/k)  # Convert k back to decay rate for plotting
    average_slopes.append(average_slope)

# Sort the data based on k_values to ensure proper plotting
sorted_indices = np.argsort(k_values)
sorted_k_values = np.array(k_values)[sorted_indices]
sorted_average_slopes = np.array(average_slopes)[sorted_indices]

# Transformed k value for plotting
transformed_k_values = [1 / (1 - k) for k in sorted_k_values]

# Plotting with the transformed k values
fig = go.Figure(data=go.Scatter(x=transformed_k_values, y=sorted_average_slopes, mode='markers+lines', name='Average Slope vs. Transformed Decay Rate'))
fig.update_layout(
    title='Average Slope of Difference Curve vs. Transformed Decay Rate',
    xaxis_title='K value (1/(1-k))',
    yaxis_title='Average Slope of Difference Curve',
    xaxis=dict(
        tickmode='auto',  
        type='linear' 
    )
)

fig.show()
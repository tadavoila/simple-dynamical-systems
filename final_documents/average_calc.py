import json

# Step 1: Process the Data
file_path1 = ["averages_1_to_6_1.json", "averages_1_to_6_2.json", "averages_1_to_6_3.json", "averages_1_to_6_4.json", "averages_1_to_6_5.json", "averages_1_to_6_6.json","averages_1_to_6_7.json", "averages_1_to_6_8.json","averages_1_to_6_9.json", "averages_1_to_6_10.json"]
file_path2 = ["averages_7_to_12_1.json", "averages_7_to_12_2.json", "averages_7_to_12_3.json", "averages_7_to_12_4.json", "averages_7_to_12_5.json", "averages_7_to_12_6.json","averages_7_to_12_7.json", "averages_7_to_12_8.json","averages_7_to_12_9.json", "averages_7_to_12_10.json"]

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

    for i in range(0, 10000, 10):
        keys = [str(j) for j in range(i, i+10)]
        values = [combined_data[key] for key in keys if key in combined_data]
        if values:
            total_averages[f"{i+1}-{i+10}"] = sum(values) / len(values)
        else:
            total_averages[f"{i+1}-{i+10}"] = None
    
    return total_averages


result_1 = process_files(file_path1)
result_2 = process_files(file_path2)



# Step 2: Create the Plotly Visualization

from plotly import graph_objs as go
import numpy as np

# Extract x (iteration numbers) and y (average values)
x1 = list(result_1.keys())
y1 = list(result_1.values())
x2 = list(result_2.keys())
y2 = list(result_2.values())



# Calculate linear regression
x1_numeric = [int(item.split('-')[0]) for item in x1]
slope1, intercept1 = np.polyfit(x1_numeric, y1, 1)

# Create the linear regression line
x1_fit = np.array(x1_numeric)
y1_fit = slope1 * x1_fit + intercept1

# Create the plot
fig = go.Figure()

# Add the scatter plot of data points first
fig.add_trace(go.Scatter(x=x1, y=y1, mode='markers', name='Low Frequency (1-6)', marker=dict(color='red')))

# Add the linear fit curve on top
fig.add_trace(go.Scatter(x=x1, y=y1_fit, mode='lines', name=f'Low Frequency (1-6)  slope = {slope1:.10f}', line=dict(color='orange')))






# Calculate linear regression
x2_numeric = [int(item.split('-')[0]) for item in x2]
slope2, intercept2 = np.polyfit(x2_numeric, y2, 1)

# Create the linear regression line
x2_fit = np.array(x2_numeric)
y2_fit = slope2 * x2_fit + intercept2


# Add the scatter plot of data points first
fig.add_trace(go.Scatter(x=x2, y=y2, mode='markers', name='High Frequency (7-12)', marker=dict(color='blue')))

# Add the linear fit curve on top
fig.add_trace(go.Scatter(x=x2, y=y2_fit, mode='lines', name= f'High Frequency (7-12) slope = {slope2:.10f}', line=dict(color='green')))


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


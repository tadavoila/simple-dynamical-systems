from plotly import graph_objs as go
import json
import numpy as np

# Define the file paths and their respective labels
file_paths1 = ["averages_1_to_6_1.json", "averages_1_to_6_2.json", "averages_1_to_6_3.json", "averages_1_to_6_4.json", "averages_1_to_6_5.json", "averages_1_to_6_6.json","averages_1_to_6_7.json", "averages_1_to_6_8.json","averages_1_to_6_9.json", "averages_1_to_6_10.json"]
file_paths2 = ["averages_7_to_12_1.json", "averages_7_to_12_2.json", "averages_7_to_12_3.json", "averages_7_to_12_4.json", "averages_7_to_12_5.json", "averages_7_to_12_6.json","averages_7_to_12_7.json", "averages_7_to_12_8.json","averages_7_to_12_9.json", "averages_7_to_12_10.json"]

# Create an empty figure
fig = go.Figure()

# Loop through the file paths for file_path1
for path in file_paths1:
    with open(path) as f:
        data = json.load(f)
    
    x = np.array(list(map(int, data.keys())))
    y = np.array(list(data.values()))

    coefficients = np.polyfit(x, y, 1)
    regression_line = np.polyval(coefficients, x)

    fig.add_trace(go.Scatter(x=x, y=regression_line, mode='lines', name=path, marker=dict(color='blue')))

# Loop through the file paths for file_path2
for path in file_paths2:
    with open(path) as f:
        data = json.load(f)
    
    x = np.array(list(map(int, data.keys())))
    y = np.array(list(data.values()))

    coefficients = np.polyfit(x, y, 1)
    regression_line = np.polyval(coefficients, x)

    fig.add_trace(go.Scatter(x=x, y=regression_line, mode='lines', name=path, marker=dict(color='red')))

# Customize the layout
fig.update_layout(
    title='Regression Lines for Files',
    xaxis_title='Iteration Count',
    yaxis_title='Exemplar Value'
)

# Show the plot
fig.show()

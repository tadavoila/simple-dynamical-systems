from plotly import graph_objs as go
import pandas as pd
import numpy as np
import os
import re

# Initialize a dictionary to store the data
# This time, we store lists of lists to accumulate all averages for each bin and decay rate
data = {f'FREQ_{i}': {} for i in range(1, 13)}
decay_rates_set = set()

pattern = re.compile(r'averages_run\d+_decay_(\d+)\.csv')

# Step 1: Read all CSV files

for file in os.listdir('.'):
    match = pattern.match(file)
    if match:
        decay_rate = int(match.group(1))
        decay_rates_set.add(decay_rate)
        
        df = pd.read_csv(file)
        
        # Collect data for each bin
        for bin_name in data.keys():
            if bin_name in df.columns:
                if decay_rate not in data[bin_name]:
                    data[bin_name][decay_rate] = []
                
                # Calculate the x values
                x_values = np.arange(len(df)) * 100
                
                # Perform linear regression to get slope
                slope, intercept = np.polyfit(x_values, df[bin_name], 1)
                
                # Append the slope to the list for its decay rate
                data[bin_name][decay_rate].append(slope)


# Calculate the overall average for each bin and decay rate
for bin_name in data.keys():
    for decay_rate in data[bin_name]:
        data[bin_name][decay_rate] = np.mean(data[bin_name][decay_rate])

# Convert decay rates to transformed k values for plotting
decay_rates = sorted(list(decay_rates_set))
transformed_k_values = decay_rates

fig = go.Figure()

# Plot each frequency bin as a separate line
for bin_name, averages in data.items():
    # Prepare the y values sorted according to the decay rates
    y_values = [averages[k] for k in decay_rates]
    
    fig.add_trace(go.Scatter(x=transformed_k_values, y=y_values, mode='lines+markers', name=bin_name))

# Add vertical lines at 492/x for x ranging from 1-12
for x_val in range(1, 13):
    fig.add_shape(type="line",
                  x0=492/x_val, y0=0,
                  x1=492/x_val, y1=0.0025,
                  line=dict(color="black", width=1, dash="dash"))

fig.update_layout(
    title='Overall Average Values for Frequency Bins vs. Transformed Decay Rate',
    xaxis_title='Transformed K Value (1/(1-(1-1/k)))',
    yaxis_title='Overall Average Value',
    legend_title='Frequency Bin'
)

fig.show()

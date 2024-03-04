import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def database(runs):    
    # Initialize lists to store dataframes for each group
    dfs_1_6 = []
    dfs_7_12 = []
    
    for a in range(1, runs+1):
        means_1_6_path = 'Outputs/means_1_6_new_run' + str(a) + '.json'
        means_7_12_path = 'Outputs/means_7_12_new_run' + str(a) + '.json'
        
        means_1_6 = pd.read_json(means_1_6_path, typ='series').to_frame(name=f'Mean{a}')
        means_7_12 = pd.read_json(means_7_12_path, typ='series').to_frame(name=f'Mean{a}')
        
        means_1_6[f'Iteration{a}'] = (means_1_6.index + 1).astype(float)
        means_7_12[f'Iteration{a}'] = (means_7_12.index + 1).astype(float)
        
        # Append the dataframes to their respective lists
        dfs_1_6.append(means_1_6)
        dfs_7_12.append(means_7_12)
    
    # Concatenate the dataframes side by side for each group
    df_1_6 = pd.concat(dfs_1_6, axis=1)
    df_7_12 = pd.concat(dfs_7_12, axis=1)
    
    return df_1_6, df_7_12

def plots(runs):
    df_1_6, df_7_12 = database(runs)
    
    # Calculate the average mean for each group of iterations
    df_1_6['AvgMean'] = df_1_6.filter(like='Mean').mean(axis=1)
    df_7_12['AvgMean'] = df_7_12.filter(like='Mean').mean(axis=1)
    
    # Group by iterations per 200 and calculate the mean for each group
    grouped_1_6 = df_1_6.groupby((df_1_6.index // 200) * 200)['AvgMean'].mean()
    grouped_7_12 = df_7_12.groupby((df_7_12.index // 200) * 200)['AvgMean'].mean()
    
    # Calculate bin edges for x-axis labels based on the maximum iteration
    max_iteration = max(grouped_1_6.index.max(), grouped_7_12.index.max())
    bin_edges = [(i, i+200) for i in range(0, max_iteration+1, 200)]
    bin_labels = [f'{edge[0]}-{edge[1]}' for edge in bin_edges]
    
    # Scatter plot for the 'grouped_1_6' DataFrame with blue dots
    fig = go.Figure(data=go.Scatter(x=bin_labels,
                                    y=grouped_1_6,
                                    mode='markers',
                                    marker=dict(color='blue', size=5),
                                    name='Low Frequency (1-6) Words'))

    # Scatter plot for the 'grouped_7_12' DataFrame with red dots
    fig.add_trace(go.Scatter(x=bin_labels,
                             y=grouped_7_12,
                             mode='markers',
                             marker=dict(color='red', size=5),
                             name='High Frequency (7-12) Words'))

    # Linear regression for grouped_1_6
    slope_1_6, intercept_1_6 = np.polyfit(grouped_1_6.index, grouped_1_6, 1)
    regression_1_6 = slope_1_6 * grouped_1_6.index + intercept_1_6

    # Linear regression for grouped_7_12
    slope_7_12, intercept_7_12 = np.polyfit(grouped_7_12.index, grouped_7_12, 1)
    regression_7_12 = slope_7_12 * grouped_7_12.index + intercept_7_12

    # Regression line for grouped_1_6
    fig.add_trace(go.Scatter(x=bin_labels,
                             y=regression_1_6,
                             mode='lines',
                             line=dict(color='black'),
                             name='Regression (1-6)'))

    # Regression line for grouped_7_12
    fig.add_trace(go.Scatter(x=bin_labels,
                             y=regression_7_12,
                             mode='lines',
                             line=dict(color='gold'),
                             name='Regression (7-12)'))

    # Calculate the difference between the means of the two groups
    difference = grouped_7_12 - grouped_1_6

    # Linear regression for the difference
    slope_diff, intercept_diff = np.polyfit(difference.index, difference, 1)
    regression_diff = slope_diff * difference.index + intercept_diff

    # Regression line for the difference
    fig.add_trace(go.Scatter(x=bin_labels,
                             y=regression_diff,
                             mode='lines',
                             line=dict(color='purple'),
                             name='Difference Regression'))

    # Update the layout
    fig.update_layout(title='Average exemplar means over time (averaged per 200 iterations)', 
                      xaxis_title='Iteration', 
                      yaxis_title='Mean',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(
                            family="Arial",
                            size=12,
                            color="Black"
                        ),
                     width = 1500)

    fig.show()

plots(50)
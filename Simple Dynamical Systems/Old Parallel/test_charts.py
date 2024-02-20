import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Generate k_values
k_values = [str(round(1 - 7/492 + i*0.001, 5))[1:].replace('.', '') for i in range(10)]

def database(runs, k_value):
    k_str = k_value
    
    dfs_1_6, dfs_7_12 = [], []

    for a in range(0, runs):
        means_1_6_path = f'Outputs/old_means_1_6_r{a}_k{k_str}.json'
        means_7_12_path = f'Outputs/old_means_7_12_r{a}_k{k_str}.json'

        means_1_6 = pd.read_json(means_1_6_path, typ='series').to_frame(name=f'Mean{a}')
        means_7_12 = pd.read_json(means_7_12_path, typ='series').to_frame(name=f'Mean{a}')

        means_1_6[f'Iteration{a}'] = (means_1_6.index + 1).astype(float)
        means_7_12[f'Iteration{a}'] = (means_7_12.index + 1).astype(float)

        dfs_1_6.append(means_1_6)
        dfs_7_12.append(means_7_12)

    df_1_6 = pd.concat(dfs_1_6, axis=1)
    df_7_12 = pd.concat(dfs_7_12, axis=1)

    return df_1_6, df_7_12

def generate_plot(fig, df_group, group_label, color):
    df_group['AvgMean'] = df_group.filter(like='Mean').mean(axis=1)
    grouped = df_group.groupby((df_group.index // 200) * 200)['AvgMean'].mean()

    fig.add_trace(go.Scatter(x=grouped.index, y=grouped, mode='markers', marker=dict(color=color, size=5), name=f'{group_label} Words'))

    slope, intercept = np.polyfit(grouped.index, grouped, 1)
    regression = slope * grouped.index + intercept

    fig.add_trace(go.Scatter(x=grouped.index, y=regression, mode='lines', line=dict(color=color), name=f'Regression ({group_label})'))

def plot_all_k_values(runs):
    fig = go.Figure()

    for k_value in k_values:
        df_1_6, df_7_12 = database(runs, k_value)
        generate_plot(fig, df_1_6, 'Low Frequency (1-6)', 'blue')
        generate_plot(fig, df_7_12, 'High Frequency (7-12)', 'red')

    fig.update_layout(height=600, width=1000, title_text="Exemplar Means Over Time by k Value", showlegend=True)
    fig.show()

if __name__ == '__main__':
    plot_all_k_values(10)

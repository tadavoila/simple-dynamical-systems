import plotly.graph_objects as go
import final_dict

data = final_dict.finall


means_data = {}
for word, info in data["Category"]["words"].items():
    frequency = info["frequency"]
    for mean in info["means"]:
        iteration = list(mean.keys())[0]
        value = list(mean.values())[0]
        if frequency not in means_data:
            means_data[frequency] = {"iterations": [], "values": []}
        means_data[frequency]["iterations"].append(int(iteration))
        means_data[frequency]["values"].append(value)

# Compute averages for every 10 iterations
averages = {"1-6": {"iterations": [], "values": []}, "7-12": {"iterations": [], "values": []}}
for frequency, values in means_data.items():
    iterations = values["iterations"]
    mean_values = values["values"]
    for i in range(0, len(iterations), 25):
        group_iterations = iterations[i:i+25]
        group_values = mean_values[i:i+25]
        avg_value = sum(group_values) / len(group_values)
        if frequency <= 6:
            averages["1-6"]["iterations"].append(sum(group_iterations) / len(group_iterations))
            averages["1-6"]["values"].append(avg_value)
        else:
            averages["7-12"]["iterations"].append(sum(group_iterations) / len(group_iterations))
            averages["7-12"]["values"].append(avg_value)

# Create the plot
fig = go.Figure()

# Add traces for each frequency group
fig.add_trace(go.Scatter(x=averages["1-6"]["iterations"], y=averages["1-6"]["values"], mode='markers', name='Frequency 1-6', marker=dict(color='blue')))
fig.add_trace(go.Scatter(x=averages["7-12"]["iterations"], y=averages["7-12"]["values"], mode='markers', name='Frequency 7-12', marker=dict(color='red')))

# Calculate regression lines using regression equation
def calculate_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x_squared = sum(x[i] ** 2 for i in range(n))

    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x**2)
    b = (sum_y - m * sum_x) / n

    return m, b

x_1_6 = averages["1-6"]["iterations"]
y_1_6 = averages["1-6"]["values"]
m_1_6, b_1_6 = calculate_regression(x_1_6, y_1_6)

x_7_12 = averages["7-12"]["iterations"]
y_7_12 = averages["7-12"]["values"]
m_7_12, b_7_12 = calculate_regression(x_7_12, y_7_12)

# Add regression lines
fig.add_trace(go.Scatter(x=x_1_6, y=[m_1_6 * x + b_1_6 for x in x_1_6], mode='lines', name=f'Regression Line 1-6: y = {m_1_6:.10f}x + {b_1_6:.10f}', line=dict(color='green')))
fig.add_trace(go.Scatter(x=x_7_12, y=[m_7_12 * x + b_7_12 for x in x_7_12], mode='lines', name=f'Regression Line 7-12: y = {m_7_12:.10f}x + {b_7_12:.10f}', line=dict(color='purple')))

# Update layout
fig.update_layout(
    title='Means vs. Iteration with Regression Lines',
    xaxis_title='Iteration',
    yaxis_title='Mean Value'
)

# Show the plot
fig.show()
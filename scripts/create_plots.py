'''
Create EDA plots and visualize regression results
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import statsmodels.formula.api as smf
import plotly.express as px
import plotly.graph_objects as go
from process_functions import *


def plot_weekly_question_count(df, output_var, type=0):
    type_list = ['Raw', 'Normalized']
    # Ensure 'CreationDate' is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['CreationDate']):
        df['CreationDate'] = pd.to_datetime(df['CreationDate'], errors='coerce')  # Convert with error handling
    
    # Group by 'CreationDate' and sum 'QuestionCount'
    grouped_data = df.groupby('CreationDate')[output_var].sum().reset_index()
    
    # Create a plot
    plt.figure(figsize=(8, 8))  # Increased figure size
    plt.plot(grouped_data['CreationDate'], grouped_data[output_var], linestyle='-')
    
    # Adding a marker for the specific date
    post_chatgpt = pd.to_datetime('2022-11-30')
    plt.axvline(x=post_chatgpt, color='red', linestyle='--', linewidth=2, label='ChatGPT Introduction')

        
    # Set x-axis tick frequency
    tick_spacing = 30  # Set the spacing between ticks to every 30 days
    plt.gca().set_xticks(grouped_data['CreationDate'][::tick_spacing])  # Set ticks every 30 days
    plt.gca().set_xticklabels([date.strftime('%Y-%m-%d') for date in grouped_data['CreationDate'][::tick_spacing]], rotation=45)

    plt.title(f'{type_list[type]} Question Count per Week', fontsize=14)
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Normalized Question Count', fontsize=12)
    # plt.grid(True)
    sns.despine()
    plt.tight_layout()  # Adjust subplots to fit into figure area.
    plt.show()

    
def plot_weekly_question_count_by_thread(df, output_var, type=0):
    type_list = ['Raw', 'Normalized']
    
    # Ensure 'CreationDate' is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['CreationDate']):
        df['CreationDate'] = pd.to_datetime(df['CreationDate'], errors='coerce')
    
    # Group by 'CreationDate' and 'Thread' and sum 'QuestionCount'
    grouped_data = df.groupby(['CreationDate', 'Thread'])[output_var].sum().unstack().fillna(0)
    
    # Create a plot
    fig = go.Figure()
    
    # Plot each thread separately
    for thread in grouped_data.columns:
        fig.add_trace(go.Scatter(x=grouped_data.index, y=grouped_data[thread],
                                 mode='lines', name=thread))
    
    # Adding a vertical red dashed line at the specific date
    specific_date = pd.to_datetime('2022-11-30')
    fig.add_trace(go.Scatter(x=[specific_date, specific_date], y=[0, grouped_data.max().max()],
                             mode='lines', line=dict(color='red', dash='dash'),
                             showlegend=False, name='Specific Date'))
    
    # Updating the layout of the plot
    fig.update_layout(
        title=f'{type_list[type]} Question Count by Creation Date and Thread',
        xaxis_title='Creation Date',
        yaxis_title='Sum of Question Count',
        legend_title='Thread ID'
    )
    
    fig.update_xaxes(tickangle=45)
    
    # Show plot
    fig.show()

def plot_event_study_simple(result, rel_weeks):
    # Prepare the plot
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Extract the predicted values and confidence intervals directly
    predictions = result.get_prediction().summary_frame(alpha=0.05)
    
    # Plotting the mean estimate
    ax.errorbar(rel_weeks, predictions['mean'], 
                yerr=[predictions['mean'] - predictions['mean_ci_lower'], 
                      predictions['mean_ci_upper'] - predictions['mean']],
                fmt='o', color='black', capsize=5)

    # Adding reference line and labels
    ax.axvline(x=0, color='gray', linestyle='--')
    ax.set_xlabel('Weeks Relative to Event')
    ax.set_ylabel('Predicted Question Volume')
    ax.set_title('Event Study Analysis: Predicted Impact on Question Volume')
    plt.grid(True)
    
    # Show plot
    plt.show()

def plot_treatment_effect(model):
     # Get the coefficients and the confidence intervals
    coefs = model.params
    conf = model.conf_int()

    # Create a DataFrame from the coefficients and confidence intervals
    results_df = pd.DataFrame({
        'Coefficient': coefs,
        'Lower CI': conf[0],
        'Upper CI': conf[1]
    })
    
    # Filter results to include only interaction terms or main effects as needed
    results_df = results_df.filter(like='Post:C(Thread)', axis=0)  # This filters for terms involving 'Thread'

    # Simplify index to show only the thread name
    results_df.index = results_df.index.str.extract('C\(Thread\)\[T\.(.*?)\]', expand=False)

    # Sort values by the coefficient for better visualization
    results_df = results_df.sort_values(by='Coefficient', ascending=False)
    results_df['Knowledge'] = results_df.index.map(add_knowledge_type)
    print(results_df.head())
    # results_df = results_df
    # Create the plot
    # plt.figure(figsize=(10, len(results_df) / 2))  # Adjust the figure size dynamically based on the number of items
    # plt.errorbar(x=results_df['Coefficient'], y=results_df.index,
    #              xerr=[results_df['Coefficient'] - results_df['Lower CI'], results_df['Upper CI'] - results_df['Coefficient']],
    #              fmt='o', ecolor='gray', capsize=3, color='black')
    # plt.axvline(x=0, linestyle='--', color='red')
    # plt.title('Effect Sizes and Confidence Intervals')
    # plt.xlabel('Estimated Coefficient')
    # plt.yticks(rotation=0)  # Keep thread labels horizontal
    # # plt.grid(True)
    # sns.despine()
    # plt.tight_layout()
    # plt.show()
    
    color_map = {
        'Hybrid': 'grey',
        'Explicit': 'teal',
        'Tacit': 'purple'
    }
    
    # Plotting
    fig, ax = plt.subplots()
    for index, row in results_df.iterrows():
        color = color_map[row['Knowledge']]
        ax.errorbar(x=row['Coefficient'], y=index, xerr=[[row['Coefficient'] - row['Lower CI']], [row['Upper CI'] - row['Coefficient']]],
                fmt='o', color=color, label=row['Knowledge'] if row['Knowledge'] not in ax.get_legend_handles_labels()[1] else "")

    # Improving the layout
    ax.set_yticks(range(len(results_df)))
    ax.set_yticklabels(results_df.index)
    ax.invert_yaxis()  # Invert axis to have the largest value on top if needed
    ax.set_xlabel('Coefficient')
    ax.set_title('Effect Sizes and Confidence Interval')
    ax.legend(title='Knowledge')
    plt.axvline(x=0, linestyle='--', color='grey')
    sns.despine()

    plt.show()

def observe_by_knowledge_type(model):
    # Get the coefficients, p-values, and the confidence intervals
    coefs = model.params
    p_values = model.pvalues
    conf = model.conf_int()

    # Create a DataFrame from the coefficients, p-values, and confidence intervals
    results_df = pd.DataFrame({
        'Coefficient': coefs,
        'P-value': p_values,
        'Lower CI': conf[0],
        'Upper CI': conf[1]
    })
    
    # Filter results to include only interaction terms or main effects as needed
    results_df = results_df.filter(like='Post:C(Thread)', axis=0)  # This filters for terms involving 'Thread'

    # Simplify index to show only the thread name
    results_df.index = results_df.index.str.extract('C\(Thread\)\[T\.(.*?)\]', expand=False)

    # Sort values by the coefficient for better visualization
    results_df = results_df.sort_values(by='Coefficient', ascending=False)

    # Add a column for the knowledge type
    results_df['Knowledge'] = results_df.index.map(add_knowledge_type)
    
    # Filter out non-significant results (p-value greater than 0.05)
    results_df = results_df[results_df['P-value'] < 0.05]
    
    # Aggregate by knowledge type to get the average effect
    results_agg = results_df.groupby('Knowledge').agg({
        'Coefficient': 'mean',
        'P-value': 'mean',
        'Lower CI': 'mean',
        'Upper CI': 'mean'
    })
    print(results_agg)
    return results_agg
    
    
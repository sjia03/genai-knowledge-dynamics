import pandas as pd
from process_data import *
from run_regressions import *
from create_plots import *

# Load in data from all threads
print("Starting script")
base_folder = '/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data'
save_path = '/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data/all_threads.csv'
# all_df = load_data(base_folder, save_path)
# all_df = pd.read_csv('/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data/all_threads.csv')

# Aggregate by week
save_weekly_path = '/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data/all_weekly_threads.csv'
# weekly_df = clean_data(all_df, save_weekly_path)
# weekly_df = pd.read_csv('/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data/all_weekly_threads.csv')
print("Read in weekly df")
weekly_df = pd.read_csv('/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/pilot-v2/data/all_weekly_threads_v2.csv')

# Add knowledge type 
# weekly_df = add_knowledge_type_column(weekly_df)

# Visualize raw count
weekly_stackoverflow_df = weekly_df[weekly_df['Thread'] == 'stackoverflow']
weekly_other_df = weekly_df[weekly_df['Thread'] != 'stackoverflow']
# plot_weekly_question_count(weekly_stackoverflow_df, 'QuestionCount') # TODO: plot separate line for stack overlofw
# plot_weekly_question_count(weekly_other_df, 'QuestionCount')
# plot_weekly_question_count_by_thread(weekly_df, 'QuestionCount')


# Normalize
normalized_weekly_df = normalize_question_count(weekly_df)
# normalized_stackoverflow_weekly_df = normalized_weekly_df[normalized_weekly_df['Thread'] == 'stackoverflow']
# normalized_other_weekly_df = normalized_weekly_df[normalized_weekly_df['Thread'] != 'stackoverflow']
# plot_weekly_question_count(normalized_stackoverflow_weekly_df, 'NormalizedQuestionCount', type=1)
# plot_weekly_question_count(normalized_other_weekly_df, 'NormalizedQuestionCount', type=1)
# plot_weekly_question_count_by_thread(normalized_weekly_df, 'NormalizedQuestionCount', type=1)

# Regression
# TODO: consider log linear
result = run_slr_with_seasonal_by_thread(normalized_weekly_df)
# plot_treatment_effect(result)
observe_by_knowledge_type(result)

# result, unique_rel_weeks = run_rel_weeks_regression(normalized_weekly_df)
# plot_event_study_simple(result, unique_rel_weeks)

# TOOD: might need to normalize (looking at raw score of each)
# main_results = run_treatment_effect_regression(weekly_df)
# plot_treatment_effect_regression(main_results)

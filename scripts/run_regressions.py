'''
Run two regression on newly built data
'''
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# TODO: consider running loglinear (as Sarah suggested)

# Run event study regression to observe coefficients relative to each week since ChatGPT
## Novelty lies in the dataset of diverse array of threads
def run_rel_weeks_regression(df, reference_date_str='2022-11-30'):  
    
    if not pd.api.types.is_datetime64_any_dtype(df['CreationDate']):
        df['CreationDate'] = pd.to_datetime(df['CreationDate'])
      
    # Set the reference date for 'RelWeek' calculation
    reference_date = pd.Timestamp(reference_date_str)
    
    # Calculate the 'RelWeek' as the number of weeks from the reference date
    df['RelWeek'] = ((df['CreationDate'] - reference_date).dt.days / 7).astype(int)
    df['Month'] = df['CreationDate'].dt.month
    
    # Set up the regression model
    model_formula = 'QuestionCount ~ RelWeek + Post + Post * RelWeek + C(Month)'
    
    # Fit the model
    result = smf.ols(formula=model_formula, data=df).fit()
    
    # Print and return the results
    print(result.summary())
    return result, sorted(df['RelWeek'].unique())

# SLR with seasonal effects
# QuestionVolume_{it} = Thread_i + ChatGPT + Thread_i * ChatGPT + tau_i + mu_{it}
## tau_c = week fixed effect (in calendar time)
## i = thread tag , t = number of posts in a week

def run_slr_with_seasonal_by_thread(df):
    
    df['Month'] = df['CreationDate'].dt.month
    
    # Ensure 'Thread' is treated as a categorical variable
    df['Thread'] = df['Thread'].astype(str)
    
    # Define the regression formula
    # Includes the interaction between 'ChatGPT' and 'Thread'
    formula = 'NormalizedQuestionCount ~ C(Thread) + Post + C(Month) + Post:C(Thread)'
    
    # Fit the regression model
    model = smf.ols(formula, data=df).fit()
    
    # Print the results
    print(model.summary())
    return model

def run_slr_with_seasonal(df):
    df['Month'] = df['CreationDate'].dt.month
    df['Thread'] = df['Thread'].astype(str)
    df['StackExchange'] = df['Thread'] != 'stackoverflow'
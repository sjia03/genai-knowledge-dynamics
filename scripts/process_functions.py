'''
Store functions for processing and cleaning data from Stack Exchange
'''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xml.etree.ElementTree as ET

import statsmodels.api as sm
from statsmodels.formula.api import ols

# PROCESS DATA

def xml_to_pd(file_path):
    # Load the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract data
    data = []
    for child in root:
        data.append(child.attrib)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

def adjust_dtype_of_posts_data(df):
    df['CreationDate'] = pd.to_datetime(df['CreationDate'])
    df['YearMonth'] = df['CreationDate'].dt.to_period('M')
    # df['OwnerUserId'] = df['OwnerUserId'].astype(float)
    df['PostTypeId'] = df['PostTypeId'].astype(int)
    # df['AnswerCount'] = df['AnswerCount'].astype('Int64')
    # df['CommentCount'] = df['CommentCount'].astype(int)
    # df['ViewCount'] = df['ViewCount'].astype('Int64')
    # df['Score'] = df['Score'].astype(int)
    return df
    
def process_users_data(df):
    df['Id'] = df['Id'].astype(float)
    df['Reputation'] = df['Reputation'].astype(float)
    return df
    
def process_and_merge(df_posts, df_users):
    df_posts = adjust_dtype_of_posts_data(df_posts)
    df_users = process_users_data(df_users)
    df_full = df_posts.merge(right=df_users, left_on='OwnerUserId', right_on='Id')
    df_full = df_full.drop(columns=['ContentLicense', 'LastActivityDate', 'LastEditDate', 'LastEditorUserId', 'DisplayName', 'WebsiteUrl'])
    return df_full    

def aggregate_by_week(df, aggregate_by_thread=True):
    # Ensure 'CreationDate' is a datetime type
    df['CreationDate'] = pd.to_datetime(df['CreationDate'])
    
    # Set 'CreationDate' as the index (needed for resampling)
    df.set_index('CreationDate', inplace=True)
    
    # Group by 'Thread', then resample by week, and count the number of questions
    # Use 'fill_value=0' to fill weeks with no data
    # if aggregate_by_thread == True:
    df = df.groupby(['Thread']).resample('W-MON').size().reset_index(name='QuestionCount').fillna(0)
    
    return df

# Attempting to implement Burtch et al 2023's reference period model to analyze question volume
def add_treat_column(df, treatment_start, treatment_end, control_start, control_end):

    # Filter the DataFrame to only include the specified date ranges
    df = df[((df['CreationDate'] >= pd.to_datetime(control_start)) & (df['CreationDate'] <= pd.to_datetime(control_end))) |
            ((df['CreationDate'] >= pd.to_datetime(treatment_start)) & (df['CreationDate'] <= pd.to_datetime(treatment_end)))]

    # Create the 'treat' column based on the date
    df['Treat'] = ((df['CreationDate'] >= pd.to_datetime(treatment_start)) & 
                (df['CreationDate'] <= pd.to_datetime(treatment_end))).astype(int)
    
    return df

def normalize_question_count(df):
    
    # Convert 'CreationDate' to datetime if necessary
    if not pd.api.types.is_datetime64_any_dtype(df['CreationDate']):
        df['CreationDate'] = pd.to_datetime(df['CreationDate'], errors='coerce')
    
    # Filter data where 'Post' = 0
    data_post_0 = df[df['Post'] == 0]
    
    # Calculate mean and std of 'QuestionCount' for each 'Thread' where 'Post' = 0
    stats = data_post_0.groupby('Thread')['QuestionCount'].agg(['mean', 'std'])
    
    # Function to normalize 'QuestionCount'
    def normalize(row):
        if row['Thread'] in stats.index:
            mean = stats.at[row['Thread'], 'mean']
            std = stats.at[row['Thread'], 'std']
            return (row['QuestionCount'] - mean) / std if std > 0 else 0
        return row['QuestionCount']
    # def normalize(row):
    #     if row['Thread'] in stats.index:
    #         mean = stats.at[row['Thread'], 'mean']
    #         std = stats.at[row['Thread'], 'std']
    #         standardized_value = (row['QuestionCount'] - mean) / std if std > 0 else 0
    #         return np.tanh(standardized_value)  # Apply tanh to squish values to [-1, 1]
    #     return row['QuestionCount']
    
    # Apply normalization across all data (for both 'Post' = 0 and 'Post' = 1)
    df['NormalizedQuestionCount'] = df.apply(normalize, axis=1)
    
    return df

def add_knowledge_type(thread_name):
    explicit_knowledge = [
        "chemistry", "computer-science", "physics", "stats", "tex",
        "english", "stackoverflow", "academia", "android", "apple",
        "askubuntu", "codegolf", "codereview", "dba", "electronics",
        "magento", "money", "software-engineering"
    ]

    tacit_knowledge = [
        "christianity", "hermeneutics", "judaism", "worldbuilding",
        "english-language-learners", "scifi"
    ]

    hybrid_knowledge = [
        "diy", "blender", "drupal", "gaming", "user-experience",
        "serverfault", "meta.stackexchange", "meta.stackoverflow",
        "sharepoint", "wordpress", "salesforce", "magento", "philosophy", "politics"
    ]
    
    if thread_name in explicit_knowledge:
        return 'Explicit'
    elif thread_name in tacit_knowledge:
        return 'Tacit'
    elif thread_name in hybrid_knowledge:
        return 'Hybrid'
    else:
        return 'Unknown'
    
    return df
        
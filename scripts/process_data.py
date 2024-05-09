'''
Combine data from each thread into one data frame

Format of data
*  Id | CreationDate | ... | Thread | Treat | Post 
* Thread = string of name of that thread (will be used for thread fixed effects)
* Treat = 1 if current time period else 0
* Post = 1 if after ChatGPT's release in November 30, 2022 else 0

Clean
* Turn CreationDate into datetime object
'''

from process_functions import *
import os

def load_data(base_folder, new_file_path):
    # Iterate over each folder and download the file with a new `Thread` column
    # Create an empty list to store dataframes
    combined_df = []

    # Iterate over all directories in the base folder
    for root, dirs, files in os.walk(base_folder):
        # Check if 'Posts.csv' is in the files list
        if 'Posts.xml' in files:
            # Construct the full path to the file
            file_path = os.path.join(root, 'Posts.xml')
            
            # Determine the thread name from the path
            thread_name = os.path.basename(root)
            print("Checking: ", thread_name)
            
            # Load the CSV into a DataFrame
            df = xml_to_pd(file_path)
            print("Finished loading xml file")
            
            # Add a 'Thread' column indicating the subject
            df['Thread'] = thread_name
            
            # Append the dataframe to the list
            combined_df.append(df)

        print("-"*10)
    # Concatenate all dataframes into one
    combined_df = pd.concat(combined_df, ignore_index=True)
    print("Saving dataframe...")
    combined_df.to_csv(new_file_path, index=False)
    print("Dataframe saved!")
    return combined_df

'''
Adjust data type, weekly aggregated data, adds Treat and Post column 
'''
def clean_data(df, new_file_path, aggregate_by_thread=True):
    # Adjust dtype of each column 
    df = adjust_dtype_of_posts_data(df)
    
    # Filter for Question posts (filter out Answers)
    df = df[df['PostTypeId'] == 1]
    
    # Shorten data frame
    earliest_date = pd.to_datetime('2021-01-10')
    df = df[df['CreationDate'] > earliest_date]
    
    # Aggregate data by week for each thread
    # if aggregate_by_week == True:
    df = aggregate_by_week(df, aggregate_by_thread)
    
    # Create Post column
    post_chatgpt = pd.to_datetime('2022-11-30')
    df['Post'] = (df['CreationDate'] > post_chatgpt).astype(int)
    
    # Normalize 
    
    print("Columns: ", df.columns) 
    print(df.head())
    # print("Thread count: ", df_weekly.groupby('Thread').size())
    
    print("Saving weekly aggreagated data...")
    df.to_csv(new_file_path, index=False)
    print("Dataframe saved!")
    return df

    

    

    








'''
Convert xml to csv file
'''

import csv
from lxml import etree
from tqdm import tqdm
import os
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import seaborn as sns

# Define the path to your XML and output CSV file
xml_file_path = '/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/data/philosophy/Posts.xml'
csv_file_path = '/Users/stellajia/Desktop/Academic/UCB/ECON/ECON191/stack-exchange/data/philosophy/Posts.csv'

def convert_xml_to_csv(xml_file_path, csv_file_path):
    """
    Convert an XML file to a CSV file using the specified columns.
    Only includes rows where 'CreationDate' is January 2019 or after.
    
    :param xml_file_path: Path to the XML file.
    :param csv_file_path: Path to the output CSV file.
    """
    columns = ['Id',
        'Reputation',
        'CreationDate',
        'DisplayName',
        'EmailHash',
        'LastAccessDate',
        'WebsiteUrl',
        'Location',
        'Age',
        'AboutMe',
        'Views',
        'UpVotes',
        'DownVotes']
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        
        row_num = 0
        start_date = datetime.datetime(2019, 1, 1)
        
        # Assuming each record is within a 'row' tag
        for event, elem in etree.iterparse(xml_file_path, events=('end',), tag='row'):
            creation_date_str = elem.get('CreationDate', '')
            try:
                creation_date = datetime.datetime.strptime(creation_date_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:  # Handles cases without microseconds
                try:
                    creation_date = datetime.datetime.strptime(creation_date_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:  # Skip rows with invalid or missing CreationDate
                    continue

            if creation_date >= start_date:
                row_data = {col: elem.get(col, '') for col in columns}
                    
            row_num += 1
            print("Working on row: ", row_num)
                    
            writer.writerow(row_data)
            
                    
            elem.clear()
            # Remove parent elements to keep memory usage low
            while elem.getprevious() is not None:
                del elem.getparent()[0]
       
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
                
def convert_xml_to_csv_pt2(xml_file_path, csv_file_path):
    df = xml_to_pd(xml_file_path)
    df.to_csv(csv_file_path, index=False)
    
                
                
convert_xml_to_csv_pt2(xml_file_path, csv_file_path)

print("Conversion completed.")
import os
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from simple_term_menu import TerminalMenu
from argparse import ArgumentParser


class expenser():
    def __init__(self):
        self.DATA = []
        self.CONFIG_FILE = ""
        self.CONFIG_DIR = os.path.join(os.getcwd(), "config")
        self.DATA_RAW_DIR = os.path.join(os.getcwd(), "data/raw")
        self.PROC_RAW_DIR = os.path.join(os.getcwd(), "data/processed")


def process_fb(raw):
    df_raw = pd.read_csv(raw, header = None)
    raw_cols = ['Date', 'Description', 'Type', 'Amount']
    df_raw.columns = raw_cols
    
    new_cols = ['Date', 'Amount', 'Description', 'Category']
    df = pd.DataFrame(columns = new_cols)
    for index, row in df_raw.iterrows():
        df.loc[index] = {'Date':row['Date'], 'Amount':row['Amount'],
                         'Description':row['Description']}
    return df

def process_chase(raw):
    df_raw = pd.read_csv(raw)
    new_cols = ['Date', 'Amount', 'Description', 'Category']
    df = pd.DataFrame(columns = new_cols)

    for index, row in df_raw.iterrows():
        df.loc[index] = {'Date':row['Transaction Date'], 'Amount':row['Amount'],
                         'Description':row['Description']}
    return df

def select_data_file(location, file_type):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(location):
        files.extend(filenames)
        break
    dataFiles = []
    for dataFile in files:
        if file_type == 'csv':
            if dataFile.endswith('.csv') or dataFile.endswith('CSV'):
                dataFiles.append(dataFile)
        elif file_type == 'yaml':
            if dataFile.endswith('.yml') or dataFile.endswith('.yaml'):
                dataFiles.append(dataFile)
    
    if not dataFiles:
        print(f"ERROR - no files to process in {location}")
        exit(1)
    elif len(dataFiles) > 1:
        terminal_menu = TerminalMenu(dataFiles)
        menu_entry_index = terminal_menu.show()

        print(f"you have selected {dataFiles[menu_entry_index]}")
        return_file = os.path.join(location, dataFiles[menu_entry_index])
    else:
        print(f"NOTICE - only file is {dataFiles[0]}. Continuing...")
        return_file = os.path.join(location, dataFiles[0])

    return return_file

def fill_categories(df_processed, budge):
    categories = budge.DATA[0]['categories']
    for index, row in df_processed.iterrows():
        description = row['Description'].upper()
        for key in categories:
            for subcat in categories.get(key):
                entry_list = list(categories[key][subcat])
                for entry in entry_list:
                    if entry.upper() in description:
                        df_processed.loc[index, 'Category'] = key
    return df_processed

def resolve_nulls(df_processed, budge):
    categories = budge.DATA[0]['categories']
    print("processing expenses with no categories..")
    for index, row in df_processed.iterrows():
        if pd.isna(row['Category']):
            print(f"{row['Date']} {row['Amount']} {row['Description'].upper()}")

            keyword = input("enter a keyword for the expense above: ")
            cat_list = list(categories)
            terminal_menu = TerminalMenu(cat_list)
            menu_entry_index = terminal_menu.show()
            cat = cat_list[menu_entry_index]
            print(f"prime category selected is {cat}")
            
            sub_list = list(categories[cat])
            terminal_menu = TerminalMenu(sub_list)
            menu_entry_index = terminal_menu.show()
            sub = sub_list[menu_entry_index]
            print(f"sub category selected is {sub}")

            budge.DATA[0]['categories'][cat][sub].append(keyword)
            write_config(budge)
            load_config(budge)

def display_data(df):
    category_sums = df.groupby('Category').sum()*-1
    ax = category_sums.plot.bar(y='Amount')
    plt.xticks(rotation=45)
    plt.show()

def write_to_csv(df_new):
    df_cur = pd.DataFrame()
    file_name = "file_name_test2.csv"  #TODO: actually write to expected file
    try:
        df_cur = pd.read_csv(file_name, sep=',')
    except:
        print(f"NOTICE - no file to read from, creating new file: {file_name}")

    cur_rows_total = len(df_cur.index)
    new_rows_total = len(df_new.index)

    df_comb = pd.concat([df_cur, df_new])
    df_dup = df_new[df_new.duplicated(keep=False)]

    if len(df_dup.index) > 1:
        print("WARNING - duplicates found in raw report")
        print(df_dup)

    df_comb = df_comb.drop_duplicates()
    df_comb = df_comb.sort_values(by='Date')
    comb_rows_total = len(df_comb.index)
    new_actual_total = comb_rows_total - cur_rows_total

    print(f"processed expenses {new_actual_total}/{new_rows_total}")
    print(f"total expenses are now {comb_rows_total}")

    df_comb.to_csv(file_name, sep=',', index = False, encoding = 'utf-8')

def load_config(budget_obj):
    if not budget_obj.CONFIG_FILE:
        print("please select a config you'd like to load:")
        budget_obj.CONFIG_FILE = select_data_file(budget_obj.CONFIG_DIR, 'yaml')

        with open(budget_obj.CONFIG_FILE, 'r') as f:
            budget_obj.DATA = list(yaml.load_all(f, Loader = yaml.loader.SafeLoader))
    
def write_config(budget_obj):
    with open(budget_obj.CONFIG_FILE, 'w') as f:
        yaml.dump(budget_obj.DATA[0], f, sort_keys = False)

def process_transfers(df, budget_obj):
    # TODO: finish this
    transfers = budget_obj.DATA[0]['transfers']
    for index, row in df.iterrows():
        for transfer in transfers:
            if transfer in row['Description'].upper():
                print(f"transfer found: {row['Date']} {row['Amount']} {row['Description']}")

def main():
    parser = ArgumentParser(description = "budget tracker utility")
    parser.add_argument('-d', '--display', action = 'store_true',
                        help = "display a processed report (in data/processed directory)")
    parser.add_argument('-p', '--process', action = 'store_true',
                        help = "process a raw expense report (in data/raw directory)")
    args = parser.parse_args()

    budget = expenser()
    load_config(budget)

    if args.process:
        print("please select a file you'd like to process")
        rawDataFile = select_data_file(budget.DATA_RAW_DIR, 'csv')
        if 'chase' in rawDataFile.lower():
            dataFile = process_chase(rawDataFile)
        elif 'firstbank' in rawDataFile.lower():
            dataFile = process_fb(rawDataFile)
        else:
            print(f"ERROR - file format not recognized for {rawDataFile}")
            exit(1)
    
        dataFile = fill_categories(dataFile, budget)

        resolve_nulls(dataFile, budget)
        process_transfers(dataFile, budget)

        # TODO: process NaN's (and save config for new keywords in categories)

        write_to_csv(dataFile)

    elif args.display:
        print("please select a file you'd like to display:")
        dataFile = select_data_file(budget.PROC_RAW_DIR, 'csv')
        df = pd.read_csv(dataFile, sep=',')

        # TODO: create stacked bar for plot

        na_count = np.count_nonzero(df.isnull())
        tot_expenses = len(df.index)

        if (tot_expenses - na_count) is not tot_expenses:
            print(f"WARNING - {na_count} / {tot_expenses} expenses without a category")

        display_data(df)


if __name__ == "__main__":
    main()

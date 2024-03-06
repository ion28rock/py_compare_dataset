# py_compare_dataset
The purpose of this app is to compare data from 2 csv files and generate an excel file containing the comparison result.

## compare_dataset.py 
This is the main module. This requires a string input as the datasetname. The given datasetname will be used to find the configuration values and will be suffixed with '_dataset_a.csv' and '_dataset_b.csv' to find the CSV file that will be compared against each other.  The comparison result file will be created and named as datasetname suffixed with '_CompareResult.xlsx'.
This module will go through each row of data in dataset A and B, and for every row the module will generate a key (based on the configured keycolumns). If the key from dataset A does not exist in dataset B then the compare result will be tagged as 'MISSING'. If the key from dataset B does not exist in dataset A then the compare result will be tagged as 'EXCRESS'. If the same key exists in both dataset A and B then each of the column values (based on the configured columncount) from dataset A and B will be compared against each other. If all of the column values from both dataset A and B are the same then the compare result will be tagged as 'MATCHED' otherwise the compare result will be tagged as 'MISMATCHED'.                

## compare_functions.py: 
This module contains the common functions that are used by compare_dataset.py

## compare.config 
This file contains the configuration values specific to the given datasetname that will be used by compare_dataset.py and compare_functions.py.

## Other Folders
data_folder contains the files names_dataset_a.csv and names_dataset_b.cav. These csv files are sample files for datasetname 'names'. The folder can be re-named as per user's preference as long as it is specified in the configuration file.

## How to Use
1.) Setup Configuration
  Edit the file compare.config and append the data with the following configuration variables:
  [datasetname] -> The datasetname is a user assigned unique name. (i.e. names)
  file_dir -> The folder path where the csv files for compareison is located. Leave as blank if the csv files are located in the same folder as compare_dataset.py
  columncount -> The number of columns that will be compared between datasets A and B
  keycolumns -> The column number(s) that will be used to generate a key string that is unique for each record. 
                The key and will be used to check if a record is either missing or excess.
  sortcolumns -> The column number(s) that will be used to sort the order of records in dataset A and B
  matchcase -> Indicates if the comparison is case sensitive or not
  roundthreshold -> Indicates the number of decimal position the numeric values are rounded before comparing.
                    If set to *, the numeric values will be compared without rounding the values.

2.) Setup the Datasets
  Place the csv files in the folder specified in configuration variable file_dir.
  The csv files should be names as datasetname suffixed with '_dataset_a.csv' and '_dataset_b.csv' (i.e. names_dataset_a.csv and names_dataset_b.csv)

3.) Execute the compare function
  Open a command prompt, cd to the same directory as compare_dataset.py
  Execute the following command:
    $ python compare_dataset.py <datasetname>
  When the compare process is completed successfully, the result file <datasetname>_CompareResult.xlsx will be generated in the same directory as compare_dataset.py



                

import pandas as pd
import numpy as np
import xlsxwriter
import datetime
import sys
from compare_functions import *

# Check if the number of command-line arguments is correct
if len(sys.argv) != 2:
  print("Usage: python compare_dataset.py <datasetname>")
  sys.exit(1)

# Get the parameter from the command line
datasetname = sys.argv[1]

# alternatively dataset name can come from user or hard-coded
# datasetname = input("Dataset Name:")
# datasetname = 'ER_WCD_IsFatal'

print("Compare Started at: ",datetime.datetime.now())

# validate if give dataset name has existing configuration
config_data = validateConfig(datasetname)

# get configuration for comparison
file_dir = config_data['file_dir']
columncount = int(config_data['columncount'])
sortcolumns = config_data['sortcolumns'].split(',')
matchcase = config_data['matchcase']
roundthreshold = config_data['roundthreshold']

# validate if file for dataset A exists and load in to DataFrame
raw_data_a = validateCsvFile(file_dir + datasetname + '_dataset_a.csv')
raw_data_b = validateCsvFile(file_dir + datasetname + '_dataset_b.csv')

# get datafame header names
header_a = getHeaderNames(raw_data_a.head())
header_b = getHeaderNames(raw_data_b.head())


# init Excel workbook and worksheet
xlWbk = xlsxwriter.Workbook(datasetname + '_CompareResult' + '.xlsx')
xlSht = xlWbk.add_worksheet()
xlSht.name = datasetname

# add format with font colors
font_color = getFontFormat(xlWbk)

# sort both dataset A & B based on config
dataset_a = raw_data_a.sort_values(convertColNumToHdrNames(sortcolumns, header_a))
dataset_b = raw_data_b.sort_values(convertColNumToHdrNames(sortcolumns, header_b))

# init compare result counters
comparestats, emptystats = createStatsArray(config_data, header_a, header_b)
countstats = initStatsList()

# init process Row number
row_now = 1
row_a = 0
last_row_a = dataset_a.index[-1]
last_col_a = len(dataset_a.columns)
row_b = 0
last_row_b = dataset_b.index[-1]
last_col_b = len(dataset_a.columns)

# write dataset A and B header names
writeRowData(xlSht, header_a, 0, 0)
writeRowData(xlSht, header_b, 0, last_col_a + 3)

while row_a <= last_row_a and row_b <= last_row_b:
  # if row_a >= 20 or row_b >= 20: break  #Uncomment this line to limit records for texting

  row_value_a = dataset_a.iloc[row_a]
  row_value_b = dataset_b.iloc[row_b]

  # get dataset key values
  key_a = getCompareKey(config_data, header_a, row_value_a)
  key_b = getCompareKey(config_data, header_b, row_value_b)
  # print('key_a:',key_a,' | key_b:',key_b,' | compare:',key_a==key_b)

  # get dataset stats data
  stats_a = ""  #getStatsData(config_data, header_a, row_value_a)
  stats_b = ""  #getStatsData(config_data, header_b, row_value_b)

  # Compare each cell velues when both dataset A and B key values matched 
  if key_a == key_b:
    all_matched = True
    
    # write dataset A column values
    writeRowData(xlSht, row_value_a, row_now, 0)
    writeRowData(xlSht, row_value_b, row_now, last_col_a + 3)    

    # go through each column within the current row
    for i in range(1, columncount + 1):
      cur_matched = False
      col_now = i-1
      cellvalue_a = dataset_a.iloc[row_a, col_now]
      if pd.isnull(cellvalue_a): cellvalue_a = "NULL"
      cellvalue_b = dataset_b.iloc[row_b, col_now]
      if pd.isnull(cellvalue_b): cellvalue_b = "NULL"
      if isNumberOrFloat(cellvalue_a) and isNumberOrFloat(cellvalue_b):
        if isNumberOrFloat(roundthreshold) and isinstance(float(cellvalue_a), float) and isinstance(float(cellvalue_b), float):
          if round(cellvalue_a, roundthreshold) == round(cellvalue_b, roundthreshold):
            cur_matched = True
        else:
          if cellvalue_a == cellvalue_b:
            cur_matched = True
      else:
        if matchcase == "true":
          if str(cellvalue_a) == str(cellvalue_b):
            cur_matched = True
        else:
          if str(cellvalue_a).upper() == str(cellvalue_b).upper():
            cur_matched = True

      if cur_matched == False:
        # highlight cells of mismatched columns
        all_matched = False
        xlSht.write(0, col_now, dataset_a.columns[col_now], font_color["MISMATCHED"])
        xlSht.write(row_now, col_now, cellvalue_a, font_color["MISMATCHED"])
        xlSht.write(0, last_col_a + 3 + col_now, dataset_b.columns[col_now], font_color["MISMATCHED"])
        xlSht.write(row_now, last_col_a + 3 + col_now, cellvalue_b, font_color["MISMATCHED"])

    if all_matched == True:
      # Write compare result and increment stats
      writeCompResult(xlWbk, xlSht, row_now, last_col_a + 1, "MATCHED", stats_a, stats_b, comparestats)
      countstats["MATCHED"] += 1
    else:
      # Write compare result and increment stats
      writeCompResult(xlWbk, xlSht, row_now, last_col_a + 1, "MISMATCHED", stats_a, stats_b, comparestats)
      countstats["MISMATCHED"] += 1
    
    row_a += 1
    row_b += 1

  elif (key_a > key_b and key_a and key_b) or (not key_a and key_b):
    # write dataset B column values
    writeRowData(xlSht, row_value_b, row_now, last_col_a + 3)    
    row_b += 1
    # Write compare result and increment stats
    writeCompResult(xlWbk, xlSht, row_now, last_col_a + 1, "EXCESS", emptystats, stats_b, comparestats)
    countstats["EXCESS"] += 1

  elif (key_a < key_b and key_a and key_b) or (key_a and not key_b):  
    # write dataset A column values
    writeRowData(xlSht, row_value_a, row_now, 0)
    row_a += 1
    # Write compare result and increment stats
    writeCompResult(xlWbk, xlSht, row_now, last_col_a + 1, "MISSING", stats_a, emptystats, comparestats)
    countstats["MISSING"] += 1
  
  if row_now % 10000 == 0:
    print("Number [",row_now,"] compare result logged at: ",datetime.datetime.now())
  row_now += 1

# Add autofilter on sheet
xlSht.autofilter(0, 0, row_now, last_col_a + 3 + last_col_b)

# Write Compare statistics
writeCompareStats(xlWbk, xlSht, last_col_a + 5 + last_col_b,  countstats, comparestats)

# Save and close output excel file
xlWbk.close()
print("Compare Completed at: ",datetime.datetime.now())
     

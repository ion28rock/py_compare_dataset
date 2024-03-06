# function
from configparser import ConfigParser
from openpyxl import load_workbook
import pandas as pd
import numpy as np

def getCompareKey(config, header, dataRow):
  keycolumns = convertColNumToHdrNames(config['keycolumns'].split(','), header)
  matchcase = config['matchcase']
  roundthreshold = config['roundthreshold']
  tempKey = ""
  for keyCol in keycolumns:
    curCellValue = dataRow[keyCol]
    if pd.isnull(curCellValue): curCellValue = "NULL"
    if tempKey: tempKey = tempKey + "#"
    if isNumberOrFloat(curCellValue):
      if isNumberOrFloat(roundthreshold) and isinstance(float(curCellValue), float):
        strCurCellValue = str(round(curCellValue, int(roundthreshold)))
      else:
        strCurCellValue = str(curCellValue)
    else:
      if matchcase == "true":
        strCurCellValue = str(curCellValue)
      else:
        strCurCellValue = str(curCellValue).upper()
    
    if strCurCellValue[-2:] == '.0':
      strCurCellValue = strCurCellValue[:len(strCurCellValue)-2]
    tempKey = tempKey + strCurCellValue
  return tempKey

# def getStatsData(config, header, dataRow):
#   statscolumns = convertColNumToHdrNames(config['statscolumns'].split(','), header)
#   matchcase = config['matchcase']
#   roundthreshold = config['roundthreshold']
#   tempKey = ""
#   for statsCol in statscolumns:
#     curCellValue = dataRow[statsCol]
#     if pd.isnull(curCellValue): curCellValue = "NULL"
#     if tempKey: tempKey = tempKey + ","
#     if isNumberOrFloat(curCellValue):
#       if isNumberOrFloat(roundthreshold) and isinstance(float(curCellValue), float):
#         strCurCellValue = str(round(curCellValue, int(roundthreshold)))
#       else:
#         strCurCellValue = str(curCellValue)
#     else:
#       if matchcase == "true":
#         strCurCellValue = str(curCellValue)
#       else:
#         strCurCellValue = str(curCellValue).upper()
    
#     tempKey = tempKey + strCurCellValue
#   return tempKey.split(",")

def createStatsArray(config, header_a, header_b):
#   statscolumns_a = convertColNumToHdrNames(config['statscolumns'].split(','), header_a)
#   statscolumns_b = convertColNumToHdrNames(config['statscolumns'].split(','), header_b)
#   statscolumns_a.extend(['Result'])
#   statscolumns_a.extend(statscolumns_b)
  statscolumns_a = ''
  statscolumns_b = ''
  emptystats = [None] * len(statscolumns_b)

  return [statscolumns_a], emptystats

def initStatsList():
  return {
    "MATCHED": 0,
    "EXCESS": 0,
    "MISSING": 0,
    "MISMATCHED": 0
  }

def validateConfig(datasetname):
  config = ConfigParser()
  config.read("compare.config")
  # validate if give dataset name has existing configuration
  try:
    return config[datasetname]
  except:
    print('There is no configuration found for the given dataset name [' + datasetname + ']')
    exit(0)
  
def validateCsvFile(file_name):
  # validate if file for dataset exists and load in to DataFrame
  try:
    inputFile = pd.read_csv(file_name)
    
  except:
    print('File name [' + file_name + '] not found')
    exit(0)
  
  if len(inputFile.index) > 1:
    return inputFile
  else:
    print('File name [' + file_name + '] does not contain any data')
    exit(0)       

def validateExcelFile(file_name, sheet_name):
  # validate if file for dataset exists and load in to DataFrame
  try:
    workbook = load_workbook(file_name, data_only=True)
  except:
    print('File name [' + file_name + '] not found')
    exit(0)
  
  try:
    return workbook[sheet_name], workbook
  except:
    print('File name [',file_name,'] found but does not contain the sheet name[',sheet_name,']')
    exit(0)

def isNumberOrFloat(value):
  # validate if the string variable contains either a number or float
  try:
    return value.isnumeric()
  except:
    try:
      return isinstance(float(value), float)
    except:
      return False

def getHeaderNames(dataframeHead):
  tempStr = ""
  for col_num, header_name in enumerate(dataframeHead):
    if tempStr: tempStr = tempStr + ","
    tempStr = tempStr + header_name
  return tempStr.split(",")

def convertColNumToHdrNames(listValues, header):
  tempStr = ""
  for i, col_val in enumerate(listValues):
    if tempStr: tempStr = tempStr + ","
    if isNumberOrFloat(col_val):
      tempStr = tempStr + header[int(col_val)]
    else:
      tempStr = tempStr + col_val
  return tempStr.split(",")

def writeRowData(worksheet, row_data, target_row, offset_col):
  for col_num, cell_value in enumerate(row_data):
    if pd.isnull(cell_value): cell_value = "NULL"
    worksheet.write(target_row, offset_col + col_num, cell_value)

def getFontFormat(wrokbook):
  # add format with font colors
  font_green=wrokbook.add_format({'font_color':'#00B050','bg_color':'#EDEDED'})
  font_yellow=wrokbook.add_format({'font_color':'#CC9900','bg_color':'#FFFFCC'})
  font_orange=wrokbook.add_format({'font_color':'#C65911','bg_color':'#FCE4D6'})
  font_red=wrokbook.add_format({'font_color':'#FF0000','bg_color':'#E9C9C9'})
  font_color = {
    "MATCHED": font_green,
    "EXCESS": font_yellow,
    "MISSING": font_orange,
    "MISMATCHED": font_red
  }
  return font_color

def writeCompResult(wrokbook, worksheet, row, col, result, stats_a, stats_b, comparestats):
  font_color = getFontFormat(wrokbook)
  # Write compare result and increment stats
  worksheet.write(row, col, result, font_color[result])

  # # loop through compare stats if either stats A or B already exist
  # idx_a = 0
  # idx_b = len(stats_a) + 2
  # combined_stats = stats_a + [result] + stats_b
  # data_exist = False
  # for row_num, row_data in enumerate(comparestats):
  #   # print("row_data:",row_data," len:",len(row_data)," | idx_a:",idx_a," | idx_b:",idx_b)
  #   compstat_a = [row_data[idx_a],row_data[idx_a+1]]
  #   compstat_b = [row_data[idx_b],row_data[idx_b+1]]
  #   # compresult = [row_data[idx_b-1]]
  #   # print("stats_a[:2]: ",stats_a[:2]," | stats_b[:2]: ",stats_b[:2])
  #   if (compstat_a == stats_a[:2] and stats_a[:2] != [None, None]) or (compstat_b == stats_b[:2] and stats_b[:2] != [None, None]):
  #     print("EXISTS > compstat_a: ",compstat_a," | compstat_b: ",compstat_b)
  #     data_exist = True
  #     if [result] == ['MISMATCHED']:
  #       comparestats[row_num] = combined_stats
  #     break 
  # if not data_exist:
  #   comparestats.append(combined_stats)

def writeCompareStats(wrokbook, worksheet, col,  countstats, comparestats):
  font_color = getFontFormat(wrokbook)
  worksheet.write(0, col, "Result")
  worksheet.write(0, col + 1, "Count")
  for idx, stats_name in enumerate(countstats):
    worksheet.write(1 + idx, col, stats_name, font_color[stats_name])
    worksheet.write(1 + idx, col + 1, countstats[stats_name], font_color[stats_name])

  # col_offset = col + 3
  # for row, row_data in enumerate(comparestats):
  #   for col_cell, cell_data in enumerate(row_data):
  #     worksheet.write(1 + row, col_cell + col_offset, cell_data)

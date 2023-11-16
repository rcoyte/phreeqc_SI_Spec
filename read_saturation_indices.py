import re
import codecs
from collections import defaultdict
import pandas as pd

gathering_cat = None
initial_soln_index = None
#TODO: how to get different tempretures without having to add every possible one? 
skip_lines = ['**For a gas, SI = log10(fugacity). Fugacity = pressure * phi / 1 atm.',
    'For ideal gases, phi = 1.',
    '',
    'Log       Log       Log    mole V',
    'Species          Molality    Activity  Molality  Activity     Gamma   cm≥/mol',
    'Phase               SI** log IAP   log K(297 K,   1 atm)',
    'Phase               SI** log IAP   log K(298 K,   1 atm)',
    'Phase               SI** log IAP   log K(299 K,   1 atm)',
    'Phase               SI** log IAP   log K(300 K,   1 atm)',
    'Phase               SI** log IAP   log K(301 K,   1 atm)',
    'Phase               SI** log IAP   log K(302 K,   1 atm)',
    'Phase               SI** log IAP   log K(303 K,   1 atm)',
    'Phase               SI** log IAP   log K(304 K,   1 atm)',    
    'Phase               SI** log IAP   log K(305 K,   1 atm)',
    'Phase               SI** log IAP   log K(306 K,   1 atm)',
    'Phase               SI** log IAP   log K(307 K,   1 atm)',
    'Phase               SI** log IAP   log K(308 K,   1 atm)',
    'Phase               SI** log IAP   log K(309 K,   1 atm)',
    'Phase               SI** log IAP   log K(310 K,   1 atm)',
    'Phase               SI** log IAP   log K(311 K,   1 atm)',
    'Phase               SI** log IAP   log K(322 K,   1 atm)',
    'Phase               SI** log IAP   log K(282 K,   1 atm)',
    'Phase               SI** log IAP   log K(283 K,   1 atm)',
    'Phase               SI** log IAP   log K(284 K,   1 atm)',
    'Phase               SI** log IAP   log K(285 K,   1 atm)',
    'Phase               SI** log IAP   log K(286 K,   1 atm)',
    'Phase               SI** log IAP   log K(287 K,   1 atm)',
    'Phase               SI** log IAP   log K(288 K,   1 atm)',
    'Phase               SI** log IAP   log K(289 K,   1 atm)',
    'Phase               SI** log IAP   log K(290 K,   1 atm)',
    'Phase               SI** log IAP   log K(291 K,   1 atm)',
    'Phase               SI** log IAP   log K(292 K,   1 atm)',
    'Phase               SI** log IAP   log K(293 K,   1 atm)',
    'Phase               SI** log IAP   log K(294 K,   1 atm)',
    'Phase               SI** log IAP   log K(296 K,   1 atm)',
    'Phase               SI** log IAP   log K(295 K,   1 atm)',
    '---------------------------------Redox couples---------------------------------',
    'Redox couple             pe  Eh (volts)',
    '	O(-2)/O(0)          14.8073      0.8501',
    '	O(-2)/O(0)          15.3612      0.8947',
    'Elements           Molality       Moles',
    '------------------']
end_line = 'End of simulation.'

data_dict = defaultdict(list)
header_dict = {}
header_dict['Solution composition'] = ['Elements', 'Molality', 'Moles', 'SolutionIndex']
header_dict['Description of solution'] = ['Key', 'Value', 'SolutionIndex']
header_dict['Distribution of species'] = ['Species', 'Molality', 'Activity', 'LogMolality', 'LogActivity', 'LogGamma', 'moleV', 'SolutionIndex']
header_dict['Saturation indices'] = ['Phase', 'SI', 'logIAP', 'logK', 'Formula', 'SolutionIndex']

with codecs.open('phreeqc.log', 'r', encoding='mac_roman') as f:
  for line in f:
    # Done
    if line.strip() == end_line:
      break
    # Don't need these lines for anything, so skip analysis
    if line.strip() in skip_lines:
      continue
    
    if line.strip() in skip_lines:
      print(line)
    # Start of a new section / solution
    initial_soln_match = re.match(r'Initial solution (\d+)\.', line)
    if initial_soln_match:
      initial_soln_index = initial_soln_match.group(1)
      print(initial_soln_index)
      continue
    
    # Still in header, so don't bother testing any more
    if initial_soln_index is None:
      continue
      
    # Divider bewteen sub-sections 
    divider_match = re.match(r'-{3,}([A-Za-z ]+)-{3,}', line)
    if divider_match:
      gathering_cat = divider_match.group(1)
      print(gathering_cat)
      continue
    
    # Gather lines in the proper list, with solution number appended
    if gathering_cat is not None:
      if gathering_cat == 'Description of solution':
        # desc of soln has spaces in keys, so can't just split by space character
        data_list = line.strip().split('=')
        # still need to explicitly strip off leading and trailing spaces
        data_list = [xx.strip() for xx in data_list]
      else:
        data_list = line.strip().split()
        # Distribution of species has special rows so blanks need to be added
        if gathering_cat == 'Distribution of species' and len(data_list) == 2:
          data_list.extend([None]*5)
      data_list.append(initial_soln_index)
      data_dict[gathering_cat].append(data_list)
      
# Process DataFrames
dataframe_dict = {}
for dataset, values_list in data_dict.items():
  dataframe_dict[dataset] = pd.DataFrame(data=values_list, columns=header_dict[dataset])
  
# Save as CSVs
for name,df in dataframe_dict.items():
  df.to_csv(name.title().replace(' ','')+'.csv', index=None, encoding='utf-8')

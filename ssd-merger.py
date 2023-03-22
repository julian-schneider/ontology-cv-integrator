import pandas as pd
import subprocess
import os
import wget


robot_installation = '/custom/path/to/ROBOT'

# Download BFO, unless it already exists
if not os.path.isfile('bfo.owl'):
    wget.download('http://purl.obolibrary.org/obo/bfo.owl')


ssd_df = pd.read_excel('Controlled_Vocabularies_Master_Table_V1.04.xlsx')
os.environ['PATH'] += ':'+robot_installation
subprocess.run("robot", shell=True)

print('fin')

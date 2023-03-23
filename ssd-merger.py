import subprocess
import os
import wget
from template_creators.process import process_template


robot_installation = '/custom/path/to/ROBOT'
os.environ['PATH'] += ':'+robot_installation

# Download BFO, unless it already exists
if not os.path.isfile('bfo.owl'):
    wget.download('http://purl.obolibrary.org/obo/bfo.owl')

qtt_file = process_template()

robot_cmd = 'robot template --merge-before -t '+qtt_file+' --input bfo.owl --output bfo_with_ssd.owl'
subprocess.run(robot_cmd, shell=True)

print('fin')

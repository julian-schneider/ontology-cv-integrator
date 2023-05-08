import subprocess
import os
import wget
import json
import pandas as pd


def apply_transformation(string, transformation, args): #simple pre-defined string transformations
    assert transformation in ['prefix', 'suffix', 'split_before', 'split_after', 'replace', 'use_fixed'], '"'+transformation+'" is not a valid transformation'
    if transformation == 'prefix': return args[0]+string
    if transformation == 'suffix': return string+args[0]
    if transformation == 'split_before': return string.split(args[0],1)[0]
    if transformation == 'split_after': return string.split(args[0],1)[-1]
    if transformation == 'replace': return string.replace(args[0], args[1])
    if transformation == 'use_fixed': return args[0]


robot_installation = '/custom/path/to/ROBOT'
os.environ['PATH'] += ':'+robot_installation

# Download BFO, unless it already exists
if not os.path.isfile('bfo.owl'):
    wget.download('http://purl.obolibrary.org/obo/bfo.owl')

# Build QTT files from JSON definitions
qtt_defs = json.load(open('example-qtts.json'))
finished_qtt_files = []

for qtt_def in qtt_defs:
    df_in = pd.read_excel(qtt_def['file'], sheet_name=qtt_def['sheet'])
    df_in.drop([idx-2 for idx in qtt_def['drop_rows']], inplace=True) #shift drop-indices because it is given as excel-index

    qtt_def['template_cols'].append({ # automatically define superclass column
        "name": "superclass (automatic)",
        "column": None,
        "template": "SC %",
        "transformations": [{
            "type": "use_fixed",
            "params": [qtt_def['parent_iri']]
        }]
      })

    finished_qtt_cols = []
    for template_def in qtt_def['template_cols']:
        if 'name' not in template_def: template_def['name'] = 'UNNAMED'

        if template_def['template'] == 'ID': parent_cell = qtt_def['parent_iri']
        elif template_def['template'] == 'LABEL': parent_cell = qtt_def['parent_label']
        elif template_def['template'] == 'SC %': parent_cell = qtt_def['parent_superclass']
        else: parent_cell = ''

        transformed_col = pd.Series('', index=range(df_in.shape[0])) if template_def['column'] is None else df_in[template_def['column']]
        for trans_def in template_def['transformations']:
            transformed_col = transformed_col.apply(apply_transformation, args=(trans_def['type'], trans_def['params']))
        finished_qtt_cols.append(pd.concat([pd.Series([template_def['name'], template_def['template'], parent_cell]), transformed_col], ignore_index=True))

    df_out = pd.concat(finished_qtt_cols, axis=1, keys=[s.name for s in finished_qtt_cols])
    template_row = df_out.loc[1]
    assert 'ID' in set(template_row) and 'LABEL' in set(template_row), 'The QTT definition for '+qtt_def['qtt_name']+' must contain "ID" and "LABEL" templates'
    df_out.to_csv('qtt/'+qtt_def['qtt_name'], sep='\t', header=False, index=False)
    finished_qtt_files.append('qtt/'+qtt_def['qtt_name'])

# Run ROBOT template for all built QTT files
robot_cmd = 'robot template --merge-before -t '+ ' -t '.join(finished_qtt_files)+' --input bfo.owl --output bfo_with_ssd.owl'
subprocess.run(robot_cmd, shell=True)


print('fin')

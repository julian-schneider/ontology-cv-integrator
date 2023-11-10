import subprocess
import os
import wget
import json
from jsonschema import validate
import pandas as pd


def apply_transformation(string, transformation, args): #simple pre-defined string transformations
    assert transformation in ['prefix', 'suffix', 'split_before', 'split_after', 'replace', 'use_fixed'], '"'+transformation+'" is not a valid transformation'
    if transformation == 'prefix': return args[0]+string
    if transformation == 'suffix': return string+args[0]
    if transformation == 'split_before': return string.split(args[0],1)[0]
    if transformation == 'split_after': return string.split(args[0],1)[-1]
    if transformation == 'replace': return string.replace(args[0], args[1])
    if transformation == 'use_fixed': return args[0]


# EDITABLE DEFAULTS:
qtt_json = 'example-qtts.json'
run_robot_subprocess = False #runs ROBOT template method directly after finishing QTT creation
robot_installation = '/custom/path/to/ROBOT' #only used if run_robot_subprocess is True


# Load JSON definitions and validate the input
qtt_defs = json.load(open(qtt_json))
validate(
    instance=qtt_defs,
    schema=json.load(open("qtt-definitions.schema.json"))
)
print("Successfully validated the given definitions JSON file:", qtt_json)

# Build QTT files from JSON definitions
finished_qtt_files = []
for qtt_def in qtt_defs:
    df_in = pd.read_excel(qtt_def['file'], sheet_name=qtt_def['sheet'], keep_default_na=False)
    df_in.drop([idx-2 for idx in qtt_def['drop_rows']], inplace=True) #shift drop-indices because it is given as excel-index

    # entities are either classes, or instances of parent Class. TODO support properties
    entity_type = 'owl:Class' if qtt_def['type'] == 'class' else qtt_def['parent_iri']
    qtt_def['template_cols'].append({ # automatically define type column
        "name": "entity type (automatic)",
        "column": None,
        "template": "TYPE",
        "transformations": [{
            "type": "use_fixed",
            "params": [entity_type]
        }]
      })

    # if entities are classes, superclass is the parent class. If they are individuals, there is no superclass.
    superclass = qtt_def['parent_iri'] if qtt_def['type'] == 'class' else ''
    qtt_def['template_cols'].append({ # automatically define superclass column
        "name": "superclass (automatic)",
        "column": None,
        "template": "SC %",
        "transformations": [{
            "type": "use_fixed",
            "params": [superclass]
        }]
      })

    finished_qtt_cols = []
    for template_def in qtt_def['template_cols']:
        if 'name' not in template_def: template_def['name'] = 'UNNAMED'

        # If language is given for the qtt, LABEL gets the annotation
        template_str = template_def['template']
        if 'language' in qtt_def and template_str == 'LABEL':
            template_str = 'AL rdfs:label@'+qtt_def['language']

        if template_def['template'] == 'ID': parent_cell = qtt_def['parent_iri']
        elif template_def['template'] == 'LABEL': parent_cell = qtt_def['parent_label']
        elif template_def['template'] == 'TYPE': parent_cell = 'owl:Class'
        elif template_def['template'] == 'SC %': parent_cell = qtt_def['parent_superclass']
        else: parent_cell = ''

        transformed_col = pd.Series('', index=range(df_in.shape[0])) if template_def['column'] is None else df_in[template_def['column']]
        for trans_def in template_def['transformations']:
            transformed_col = transformed_col.apply(apply_transformation, args=(trans_def['type'], trans_def['params']))
        finished_qtt_cols.append(pd.concat([pd.Series([template_def['name'], template_str, parent_cell]), transformed_col], ignore_index=True))

    df_out = pd.concat(finished_qtt_cols, axis=1, keys=[s.name for s in finished_qtt_cols])
    template_row = df_out.loc[1]
    assert 'ID' in set(template_row) or 'LABEL' in set(template_row), 'The QTT definition for '+qtt_def['qtt_name']+' must contain "ID" or "LABEL" templates'
    df_out.to_csv('qtt/'+qtt_def['qtt_name'], sep='\t', header=False, index=False)
    finished_qtt_files.append('qtt/'+qtt_def['qtt_name'])


# Optionally run ROBOT template for all built QTT files
robot_cmd = 'robot template --merge-before -t '+ ' -t '.join(finished_qtt_files)+' --input cv-ontology-base.owl --output cv-ontology-filled.owl'
if run_robot_subprocess:
    os.environ['PATH'] += ':'+robot_installation
    subprocess.run(robot_cmd, shell=True)
else:
    print('ROBOT command to run:', robot_cmd, sep='\n')

import subprocess
import os
import json
from jsonschema import validate
import pandas as pd


def apply_transformation(string, transformation, args): #simple pre-defined string transformations
    assert transformation in ['prefix', 'suffix', 'split_before', 'split_after', 'replace', 'use_fixed'], '"'+transformation+'" is not a valid transformation'
    if transformation == 'prefix': return args[0]+str(string)
    if transformation == 'suffix': return string+args[0]
    if transformation == 'split_before': return string.split(args[0],1)[0]
    if transformation == 'split_after': return string.split(args[0],1)[-1]
    if transformation == 'replace': return string.replace(args[0], args[1])
    if transformation == 'use_fixed': return args[0]


entity_type_map = {
    'class': 'owl:Class',
    'individual': 'owl:Individual', #not used, since instantiated class is the type instead, in QTT
    'datatypeProperty': 'owl:DatatypeProperty',
    'objectProperty': 'owl:ObjectProperty'
}

# EDITABLE DEFAULTS:
qtt_json = 'fskxo-instructions.json'
del_duplicate_labels = True #per sheet, if multiple rows have the same label, only keep the first occurrence
run_robot_subprocess = False #runs ROBOT template method directly after finishing QTT creation
robot_installation = '/home/schneider/applications/ROBOT' #only used if run_robot_subprocess is True
iri_base = 'http://semanticlookup.zbmed.de/km/fskxo/FSKXO_'
iri_id_start = 3 #lowest number that should be assigned
base_onto = 'fskxo-base.owl'
output_onto = 'fskxo.owl'


# Load JSON definitions and validate the input
qtt_defs = json.load(open(qtt_json))
validate(
    instance=qtt_defs,
    schema=json.load(open("qtt-definitions.schema.json"))
)
print("Successfully validated the given definitions JSON file:", qtt_json)

next_iri_id = iri_id_start
# Build QTT files from JSON definitions
finished_qtt_files = []
for qtt_def in qtt_defs:
    df_in = pd.read_excel(qtt_def['file'], sheet_name=qtt_def['sheet'], keep_default_na=False)
    df_in.drop([idx-2 for idx in qtt_def['drop_rows']], inplace=True) #shift drop-indices because it is given as excel-index
    df_in.reset_index(drop=True, inplace=True)

    if qtt_def['type'] == 'individual':
        assert 'parent' in qtt_def, 'Individuals for '+qtt_def['qtt_name']+' cannot be created, because no parent has been supplied.'

    # Assign IRIs for parent and entities
    if "parent" in qtt_def:
        parent_iri = iri_base + str(next_iri_id).zfill(10)
        next_iri_id += 1
    df_in['IRIs'] = pd.Series(range(next_iri_id, next_iri_id + df_in.shape[0]))
    df_in['IRIs'] = df_in['IRIs'].astype(str).str.zfill(10)
    next_iri_id += df_in.shape[0]

    qtt_def['template_cols'].append({ # automatically define iri column
        "name": "iri (automatic)",
        "column": "IRIs",
        "template": "ID",
        "transformations": [{
            "type": "prefix",
            "params": [iri_base]
        }]
      })

    entity_type = parent_iri if qtt_def['type'] == 'individual' else entity_type_map[qtt_def['type']]
    qtt_def['template_cols'].append({ # automatically define type column
        "name": "entity type (automatic)",
        "column": None,
        "template": "TYPE",
        "transformations": [{
            "type": "use_fixed",
            "params": [entity_type]
        }]
      })

    # for classes/properties, parent becomes superclass/superproperty if supplied
    # even in case of instances, an empty column is created for the parent_cell
    if 'parent' in qtt_def:
        superentity = '' if qtt_def['type'] == 'individual' else parent_iri
        qtt_def['template_cols'].append({ # automatically define superclass column
            "name": "superclass (automatic)",
            "column": None,
            "template": "SC %",
            "transformations": [{
                "type": "use_fixed",
                "params": [superentity]
            }]
          })

    finished_qtt_cols = []
    duplicate_idx = [] # indicates rows with duplicate labels
    for template_def in qtt_def['template_cols']:
        if 'name' not in template_def: template_def['name'] = 'UNNAMED'

        template_str = template_def['template']

        # mark rows with duplicate labels
        if template_str == 'LABEL':
            duplicate_idx = df_in[df_in[template_def['column']].duplicated()].index.values + 3 #shift 3 for QTT header rows

        # If language is given for the qtt, LABEL gets the annotation
        if 'language' in qtt_def and template_str == 'LABEL':
            template_str = 'AL rdfs:label@'+qtt_def['language']

        parent_cell = ''
        if 'parent' in qtt_def:
            if template_def['template'] == 'ID': parent_cell = parent_iri
            elif template_def['template'] == 'LABEL': parent_cell = qtt_def['parent']['parent_label']
            elif template_def['template'] == 'TYPE': parent_cell = 'owl:Class'
            elif template_def['template'] == 'SC %': parent_cell = qtt_def['parent']['parent_superclass']

        transformed_col = pd.Series('', index=range(df_in.shape[0])) if template_def['column'] is None else df_in[template_def['column']]
        for trans_def in template_def['transformations']:
            transformed_col = transformed_col.apply(apply_transformation, args=(trans_def['type'], trans_def['params']))
        finished_qtt_cols.append(pd.concat([pd.Series([template_def['name'], template_str, parent_cell]), transformed_col], ignore_index=True))

    df_out = pd.concat(finished_qtt_cols, axis=1, keys=[s.name for s in finished_qtt_cols])

    # if wanted, only keep the first occurrence when label has duplicates
    if del_duplicate_labels and len(duplicate_idx) > 0:
        df_out = df_out.drop(duplicate_idx)
        print('Dropped', len(duplicate_idx), 'duplicates from:', qtt_def['sheet'])

    template_row = df_out.loc[1]
    assert 'ID' in set(template_row) or 'LABEL' in set(template_row), 'The QTT definition for '+qtt_def['qtt_name']+' must contain "ID" or "LABEL" templates'
    df_out.to_csv('qtt/'+qtt_def['qtt_name'], sep='\t', header=False, index=False)
    finished_qtt_files.append('qtt/'+qtt_def['qtt_name'])


# Optionally run ROBOT template for all built QTT files
robot_cmd = 'robot template --merge-before -t ' + ' -t '.join(finished_qtt_files)+' --input ' + base_onto + ' --output ' + output_onto
if run_robot_subprocess:
    os.environ['PATH'] += ':'+robot_installation
    subprocess.run(robot_cmd, shell=True)
else:
    print('ROBOT command to run:', robot_cmd, sep='\n')

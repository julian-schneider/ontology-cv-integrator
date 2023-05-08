import pandas as pd


def param_dist_template():
    filename = 'param_dist_qtt.tsv'

    param_dist_df = pd.read_excel('Controlled_Vocabularies_Master_Table_V1.04.xlsx', sheet_name='Parameter distribution')
    param_dist_df = param_dist_df.loc[:,:'Comment']
    param_dist_df['given_IRI'] = 'http://id.zbmed.de/ssd/' + param_dist_df['ID']
    param_dist_df['ID'] = 'EFSA_SSD2:' + param_dist_df['ID']
    param_dist_df['superclass'] = 'http://id.zbmed.de/ssd/Parameter_distribution'

    # Insert class 'Parameter distribution' under BFO process as superclass for all rows
    param_dist_df.loc[-0.1] = 'Parameter distribution', '', '', 'http://id.zbmed.de/ssd/Parameter_distribution', 'http://purl.obolibrary.org/obo/BFO_0000019'

    # Insert template logic row
    param_dist_df.loc[-0.2] = 'LABEL', \
        'A http://www.geneontology.org/formats/oboInOwl#hasDbXref', \
        'A http://purl.obolibrary.org/obo/IAO_0000119', \
        'ID', \
        'SC %'
    param_dist_df = param_dist_df.sort_index().reset_index(drop=True)

    param_dist_df.to_csv(filename, sep='\t', index=False)

    return filename

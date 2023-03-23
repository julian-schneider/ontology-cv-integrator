import pandas as pd


def process_template():
    filename = 'process_qtt.tsv'

    process_df = pd.read_excel('Controlled_Vocabularies_Master_Table_V1.04.xlsx', sheet_name='Product treatment')
    process_df['given_IRI'] = 'http://id.zbmed.de/ssd/' + process_df['ID']
    process_df['ID'] = 'EFSA_SSD2:' + process_df['ID']
    process_df['superclass'] = 'http://id.zbmed.de/ssd/Product_treatment'

    # Insert class 'Product treatment' under BFO process as superclass for all rows
    process_df.loc[-0.1] = 'Product treatment', '', '', 'http://id.zbmed.de/ssd/Product_treatment', 'http://purl.obolibrary.org/obo/BFO_0000015'

    # Insert template logic row
    process_df.loc[-0.2] = 'LABEL', \
        'A http://www.geneontology.org/formats/oboInOwl#hasDbXref', \
        'A http://purl.obolibrary.org/obo/IAO_0000115', \
        'ID', \
        'SC %'
    process_df = process_df.sort_index().reset_index(drop=True)

    process_df.to_csv(filename, sep='\t', index=False)

    return filename

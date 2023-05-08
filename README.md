# Adds Controlled Vocabularies to BFO

Reads controlled vocabulary contents from Excel spreadsheets, transforming them into valid [Quick Term Template](http://robot.obolibrary.org/template) files.
Optionally runs uses ROBOT's template function to insert them into BFO.


## Usage
1) Copy source Excel spreadsheet to this directory
2) Create a JSON file outlining how CVs from the Excel file should become QTTs. JSON file must conform to `qtt-definitions.schema.json`. Edit the input JSON filename in `ssd-merger.py`.
3) Run `ssd-merger.py` to create the QTT files.
4) Run the ROBOT command produced by the previous step to create the ontology classes.


- *Optional note: ROBOT's installation directory can be entered in `ssd-merger.py` to execute step 4 automatically after 3*

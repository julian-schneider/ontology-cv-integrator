# Adds Controlled Vocabularies to BFO

Reads controlled vocabulary contents from Excel spreadsheets, transforming them into valid [Quick Term Template](http://robot.obolibrary.org/template) files.
Optionally runs uses ROBOT's template function to insert them into an empty ontology that imports BFO.


## Prerequisites
- Python 3.8
- [ROBOT tools](http://robot.obolibrary.org/)


## Usage
1) Copy source Excel spreadsheet to this directory
2) Create a JSON file outlining how CVs from the Excel file should become QTTs. JSON file must conform to `qtt-definitions.schema.json`. Edit the input JSON filename in `qtt-creator.py`.
3) Run `qtt-creator.py` to create the QTT files.
4) Run the ROBOT command produced by the previous step to create the ontology classes.


- *Optional note: ROBOT's installation directory can be entered in `qtt-creator.py` to execute step 4 automatically after 3*

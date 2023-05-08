# Adds Controlled Vocabularies to BFO

Reads controlled vocabulary contents from Excel spreadsheets, transforms them into a valid [Quick Term Template](http://robot.obolibrary.org/template) file, and then uses ROBOT's template function to insert them into BFO.


## Usage
- Copy source Excel spreadsheet to this directory
- Install OBO ROBOT tools and edit its installation directory in `ssd-merger.py`
- Create a JSON file outlining how CVs from the Excel file should become QTTs. JSON file must conform to `qtt-definitions.schema.json`. Edit the input JSON filename in `ssd-merger.py`.
- Run `ssd-merger.py`
# meiyume_bte_dash_flask_app
repo for trend engine web application.
work in progress

## All the required data files are in dash_data folder. fhe file format is feather. You will need pandas.read_feather method to read the data files.

Run `pip install --upgrade -r requirements.txt` in the desired virtual environment before executing python file.

## Before running the application make sure you set correct path in the code file at line number: 34.

`dash_data_path = Path('enter your data folder path here')`


To run the app on local machine run `python beauty_trend_engine.py` in the command line.
## Navigate to the correct folder containing the python file before running it.

## To deploy the application, please follow how to deploy flask app on aws. Dash app and Flask app deployment procedures are identical.
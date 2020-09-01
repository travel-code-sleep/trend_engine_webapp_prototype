# meiyume_bte_dash_flask_app
repo for trend engine web application.
work in progress

## 1. Install requirements
Run `pip install --upgrade -r requirements.txt` in the desired virtual environment before executing python file.

## 2. Set environment variable
You have to set AWS credentials environment variables before you can get your application up and running.

To start with, create a file (if it is not exists) .env and set your AWS credentials inside the file.

The content of the .env file should be as follows:
```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

The .env file should be in the same folder as settings.py.

## 3. (Optional) Make neccessary changes on the settings.py file 
Default value inside settings.py should be fine. Feel free to make any changes

## 4. Start the dash server on your local computer
To run the app on local machine run
```
cd meiyume_bte_dash_flask_app
python main.py
```
in the command line.

## Default data is stored and read from S3
`bucket = meiyume-datawarehouse-prod`
`dash_data_path = 'Feeds/BeautyTrendEngine/WebAppData'`

## Navigate to the correct folder containing the python file before running it.

## To deploy the application, please follow how to deploy flask app on aws. Dash app and Flask app deployment procedures are identical.

## Make sure assets, images folders are present in correct path when deploying.

### Project Folder Structure
```
meiyume_bte_dash_flask_app
│   README.md
│   License
|   Manifest
│   requirements.txt
|   setup.py
└───meiyume_trend_engine
│   │   __init__.py
│   │   .env
│   │   settings.py
│   │   main.py
|   |   bte_category_page_data_and_plots.py
│   │   bte_ingredient_page_data_and_plots.py
|   |   bte_market_trend_page_data_and_plots.py
|   |   bte_product_page_data_and_plots.py
|   |   bte_utils.py
│   └───images
│   |   │   not_avlbl.jpg
│   |   │   temp_product_image.png
│   |   │   ...
|   └───assets
│   |   │   bte_logo.png
│   |   │   resizing_script.js
│   |   |   responsive-sidebar.css
|   |   |   styles.css
|   |   |   landing_page_bg.jpg
```
# meiyume_bte_dash_flask_app
repo for trend engine web application.
work in progress

Run `pip install --upgrade -r requirements.txt` in the desired virtual environment before executing python file.

## Data is stored and read from S3
`bucket = meiyume-datawarehouse-prod`
`dash_data_path = 'Feeds/BeautyTrendEngine/WebAppData'`


To run the app on local machine run `python beauty_trend_engine.py` in the command line.
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
│   │   beauty_trend_engine_app.py
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
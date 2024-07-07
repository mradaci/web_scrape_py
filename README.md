# Web_Scrape_Py
The purpose of this script is a PoC on how we can ude diffenet Python libraries and open source DBs to create a centralized, historical repository of any website.  

This is achieved via the below Python script and its dependencies. The script will create the tables in a local SQlite DB, one for the Pages of each url scrapped and the content in them, one for the media content urls/locations, and one for logging.  

Assuming you have Python already configured on your machine, please make sure that you also have pip installed and available as it will be used to obtain the dependencies for the script. If you don't already have Python configured, please see [this](https://www.howtogeek.com/197947/how-to-install-python-on-windows/) for the required information.  

## Requirements:

1. SQlite Database  
    `pip install sqlite`
2. Python 3+ configured on machine  
    [Python](http://www.python.org)
3. Vitual Env created with all import dependencies (see code)  
    - Create virtual env  
        `python -m venv /path/to/new/virtual/environment`  
    - Navigate into newly created venv path and activate it  
        `source .venv/bin/activate`  
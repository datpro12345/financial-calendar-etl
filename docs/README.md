# Project Architecture: Foreign Exchange Market ETL Pipeline

## Overview

This document outlines the architecture of the Forex Factory ETL (Extract, Transform, Load) pipeline. The purpose of this pipeline is to automate the process of extracting economic indicator data from the Forex Factory website, transforming this data into a structured format, and loading it into a storage solution for subsequent analysis. The data includes actual and forecasted economic indicators, which can be utilized for economic analysis and forecasting.

## Directory Structure

The project is organized into several directories, each serving a specific purpose within the ETL pipeline:

```
forex_etl_project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── scripts/
│   ├── extract/
│   ├── transform/
│   ├── load/
│   ├── utils/
│   └── run_etl.py
│
├── config/
│   └── config.yaml
│
├── notebooks/
│   ├── eda/
│   └── README.md
│
├── tests/
│   ├── test_extraction.py
│   ├── test_transformation.py
│   └── test_utils.py
│
├── docs/
│   ├── README.md
│   ├── architecture.md
│   └── deployment.md
│
├── logs/
│   └── etl_process.log
│
├── requirements.txt
├── .gitignore
└── setup.py
```

### Data Directory

- **`data/raw/`**: This directory stores raw data files that are directly downloaded from the Forex Factory website. The data is organized into subdirectories by month and week for easy access and management.
  
- **`data/processed/`**: Processed data files are stored here after the transformation stage. The data is structured and cleaned, making it ready for analysis.

### Scripts Directory

- **`scripts/extract/`**: Contains the script `forex_extractor.py` responsible for scraping data from the Forex Factory website. This script automates the extraction of economic indicators on a scheduled basis.

- **`scripts/transform/`**: The `forex_transformer.py` script handles data transformation, converting raw, unstructured data into a structured format suitable for analysis. This includes cleaning the data, handling missing values, and structuring it into a tabular format with relevant columns such as `date`, `indicator`, `actual`, and `forecast`.

- **`scripts/load/`**: The `load_to_gsheets.py` script manages the loading of processed data into Google Sheets or another data storage solution. This allows for easy access, sharing, and integration with other tools or workflows.

- **`scripts/utils/`**: Contains utility functions (`utils.py`) and logging configurations (`logger.py`) that are used across multiple scripts in the ETL process.

- **`scripts/run_etl.py`**: This script orchestrates the entire ETL process by sequentially running the extraction, transformation, and load steps. It serves as the main entry point for the ETL pipeline.

### Config Directory

- **`config.yaml`**: A configuration file that stores essential settings such as file paths, API keys, and other parameters required by the ETL scripts. This allows for easy modification of configurations without altering the core logic of the scripts.

### Notebooks Directory

- **`notebooks/eda/`**: Contains Jupyter notebooks for Exploratory Data Analysis (EDA). These notebooks help in exploring the data, understanding the distribution of economic indicators, and performing initial analysis on the actual vs. forecast data.

### Tests Directory

- **`tests/`**: This directory holds unit tests for different components of the ETL pipeline. It ensures that the extraction (`test_extraction.py`), transformation (`test_transformation.py`), and utility functions (`test_utils.py`) work as expected.

### Docs Directory

- **`docs/`**: Contains project documentation, including this architecture overview (`architecture.md`), general project information (`README.md`), and deployment instructions (`deployment.md`).

### Logs Directory

- **`logs/`**: Stores log files, such as `etl_process.log`, which capture the execution details of the ETL process. Logging is crucial for monitoring the process and troubleshooting issues.

## ETL Process Flow

### 1. **Extract**

The `forex_extractor.py` script is responsible for extracting economic indicator data from the Forex Factory website. This data includes actual and forecasted values of key economic indicators like GDP, CPI, and unemployment rates. The extracted data is saved in the `data/raw/` directory, organized by date.

### 2. **Transform**

The transformation stage, managed by the `forex_transformer.py` script, involves cleaning and structuring the raw data. This step includes:
- **Data Cleaning**: Handling missing values, removing duplicates, and correcting any inconsistencies.
- **Data Structuring**: Converting the raw data into a tabular format with columns for `date`, `indicator`, `actual`, `forecast`, and other relevant fields.
- **Aggregation**: Optionally, data can be aggregated on a weekly or monthly basis to facilitate trend analysis.

The transformed data is saved in the `data/processed/` directory, making it ready for further analysis.

### 3. **Load**

The final step is loading the processed data into a target storage solution, such as Google Sheets, for easy access and sharing. This is handled by the `load_to_gsheets.py` script. The structured data can then be used for downstream analysis, reporting, or integration with other analytical tools.

## Logging and Monitoring

The ETL process is monitored through detailed logging, with logs stored in the `logs/etl_process.log` file. This log captures key events, errors, and performance metrics during the ETL process, enabling easier troubleshooting and process optimization.

## Conclusion

The Forex ETL pipeline is a robust and scalable solution for automating the collection and processing of economic indicator data from Forex Factory. By organizing the project into clearly defined directories and scripts, the pipeline is easy to maintain, extend, and deploy. This architecture ensures that the data is consistently processed and readily available for analysis, supporting informed economic decision-making.
[Final Dashboard on Looker](https://lookerstudio.google.com/reporting/eef5b556-a5d4-4d54-be00-27cbc59f30d2)

### Project Description

This project focuses on two key goals:

1. **ETL (Extract, Transform, Load):**
   - The project automates the extraction of financial calendar data related to major currencies (USD, GBP, EUR). It then transforms this data to a structured format, filtering for high-impact events. Finally, it loads the cleaned data into a database or file for further analysis.

2. **Transform Raw Data to Google CSV Format:** (Done)
   - The project processes raw financial event data and converts it into a CSV format that is specifically structured for import into Google Calendar. This ensures the data is ready to be used in Google Calendar for scheduling and tracking important financial events.
-------------

### Project Phases for Task 1: ETL (Extract, Transform, Load)

This project is structured to efficiently manage the ETL process, converting raw financial calendar data into a structured format suitable for analysis and reporting. The ETL process is broken down into several key phases:

#### **Phase 1: Data Ingestion (Extract)**
- **Objective:** Collect raw data from the source, such as Forex Factory, and store it in the raw data layer (`bronze` layer).
- **Current Status:** The project currently contains raw data files in the `data/bronze/monthly` folder, indicating that data ingestion has been successfully implemented.
- **Next Steps:**
  - Refactor the extraction logic into a dedicated script under `scripts/extract`.
  - Automate the extraction process to fetch new data at regular intervals (e.g., monthly or weekly).

#### **Phase 2: Data Transformation**
- **Objective:** Clean, filter, and transform the raw data to prepare it for analysis. This includes filtering for relevant currencies, handling missing values, and formatting dates.
- **Current Status:** Transformation logic is currently implemented within a single notebook. This phase is in progress.
- **Next Steps:**
  - Modularize the transformation code by breaking it down into smaller, reusable functions or scripts. These scripts should be stored in the `scripts/transform` directory.
  - Automate the transformation steps, ensuring they can be executed independently and efficiently.
  - Store the transformed data in the intermediate `silver` layer, which is already set up with directories such as `silver/monthly` and `silver/weekly`.

#### **Phase 3: Data Loading**
- **Objective:** Load the transformed data into the final storage or destination for analysis, visualization, or reporting.
- **Current Status:** The project includes a `final_transformed_data.csv` file in the `silver` directory, indicating the beginning of this phase.
- **Next Steps:**
  - Finalize the data transformation, ensuring the dataset is ready for analysis or integration into tools such as Google Sheets or a data warehouse.
  - Save the final data products in the `silver` layer or prepare for a `gold` layer if necessary.
  - Organize the data loading scripts within the `scripts/load` directory for better maintainability.

#### **Phase 4: Validation and Testing**
- **Objective:** Validate the ETL pipeline to ensure it processes data accurately and reliably.
- **Current Status:** The validation phase has not been fully implemented yet.
- **Next Steps:**
  - Develop unit tests for each transformation function to verify correctness. Store these tests in the `tests` directory.
  - Implement data validation checks at each stage of the ETL pipeline to ensure data quality.

### Summary of Current Phase and Next Steps

**Current Phase:** The project is primarily in **Phase 2 (Data Transformation)**, with initial steps completed in **Phase 1 (Data Ingestion)** and **Phase 3 (Data Loading)**.

**Next Steps:**
1. **Refactor the existing notebook into modular scripts**, distributing them across `scripts/extract`, `scripts/transform`, and `scripts/load`.
2. **Automate the ETL pipeline** to ensure each step is executable independently and seamlessly.
3. **Enhance testing and validation** by implementing unit tests and data validation checks to ensure the pipeline's accuracy and robustness.


[Final Dashboard on Looker](https://lookerstudio.google.com/reporting/eef5b556-a5d4-4d54-be00-27cbc59f30d2)

### Project Description

This project focuses on two key goals:

1. **ETL (Extract, Transform, Load):**
   - The project automates the extraction of financial calendar data related to major currencies (USD, GBP, EUR). It then transforms this data to a structured format, filtering for high-impact events. Finally, it loads the cleaned data into a database or file for further analysis.

2. **Transform Raw Data to Google CSV Format:** (Done)
   - The project processes raw financial event data and converts it into a CSV format that is specifically structured for import into Google Calendar. This ensures the data is ready to be used in Google Calendar for scheduling and tracking important financial events.
-------------

### Project Phases for Task 1: ETL (Extract, Transform, Load)

Based on the current structure of your project and the tasks you want to accomplish, here’s how you can break down the ETL process into phases. I'll also clarify which phase you're currently in and suggest the next steps.

#### **Phase 1: Data Ingestion (Extract)**
- **Objective:** Collect raw data from the source (e.g., Forex Factory).
- **Current Status:** You've likely completed this phase since you have multiple CSV files stored in the `bronze/monthly` folder. These represent the raw, unprocessed data.
- **Next Steps:**
  - Refactor the code used for extraction into a script under `scripts/extract`.
  - Ensure that the extraction process is automated to fetch new data regularly (e.g., monthly, weekly).

#### **Phase 2: Data Transformation**
- **Objective:** Clean, filter, and transform the raw data into a structured format.
- **Current Status:** Based on the description, you're currently in this phase, working within a single notebook that handles the entire ETL process.
- **Next Steps:**
  - **Modularize the Code:** Break down the transformation code into smaller functions or scripts. These should be placed under `scripts/transform`.
    - Example: Create separate functions/scripts for filtering data, handling missing values, and transforming dates/times.
  - **Process Automation:** Ensure that each step in the transformation process can be executed automatically (without manual intervention).
  - **Intermediate Data Storage:** After transformation, save the data into an intermediate stage, typically referred to as the `silver` layer. You already have this set up with folders like `silver/monthly` and `silver/weekly`.

#### **Phase 3: Data Loading**
- **Objective:** Load the transformed data into the final storage or analysis destination.
- **Current Status:** It seems you may have started on this phase, given the `final_transformed_data.csv` in the `silver` directory.
- **Next Steps:**
  - **Final Transformation:** Ensure the data is in its final format for analysis or reporting. This could involve aggregating monthly data or filtering for specific events.
  - **Data Export:** Save the final datasets in the appropriate format (e.g., CSV, database) in the `silver` layer or directly into the `gold` layer if you intend to create one.
  - **Scripts Organization:** Move the data loading logic into `scripts/load` to keep it modular and maintainable.

#### **Phase 4: Validation and Testing**
- **Objective:** Ensure that the ETL process is working correctly.
- **Current Status:** This phase may not be fully addressed yet.
- **Next Steps:**
  - **Unit Testing:** Develop unit tests for each function, especially for transformations, to ensure they behave as expected. Place these tests in the `tests` directory.
  - **Data Validation:** Implement checks to verify the accuracy and completeness of the data at each stage.

### Summary of the Current Phase and Next Steps

**Current Phase:** You are primarily in **Phase 2 (Data Transformation)** but have elements of **Phase 1 (Data Ingestion)** and **Phase 3 (Data Loading)** in progress.

**Next Steps:**
1. **Refactor your Notebook into Modular Scripts:** Break down your existing notebook into separate scripts for extraction, transformation, and loading.
2. **Organize Your Scripts:** Place each script in the relevant folder (`scripts/extract`, `scripts/transform`, `scripts/load`).
3. **Automation:** Ensure that each step can be executed automatically, possibly through a main script or scheduler.
4. **Testing:** Begin writing tests to validate each part of your ETL pipeline.

# GEMINI.md

## Project Overview

This is a comprehensive, multi-page Streamlit web application for project portfolio analysis. It's built with Python and utilizes a suite of libraries including Streamlit for the user interface, Pandas for data manipulation, and Plotly for creating interactive charts. The application also integrates Google OAuth for user authentication and Firebase for data persistence, enabling a secure and personalized user experience.

The core of the application lies in its powerful Earned Value Management (EVM) analysis capabilities, providing deep insights into project performance. It supports data import from both CSV and JSON files, as well as manual data entry, offering flexibility in how data is brought into the system.

### Key Features:

- **Data Management:** Flexible data import options from CSV and JSON files, in addition to a manual data entry interface.
- **EVM Analysis:** A robust EVM engine for detailed project analysis and performance tracking.
- **Portfolio Visualization:** Interactive portfolio analysis tools, including Gantt charts for visualizing project timelines.
- **Simulators:** Includes both a Cash Flow Simulator and an EVM Simulator for advanced forecasting and scenario modeling.
- **User Authentication & Access Control:** Secure user authentication via Google OAuth, with role-based access control for different pages and features.
- **LLM Integration:** Leverages Large Language Models (LLMs) to generate executive summaries and provide AI-powered insights.

### Architecture:

The project is thoughtfully structured to ensure a clean separation of concerns, promoting maintainability and scalability.

- **`main.py`**: The main entry point of the Streamlit application, which serves as the central navigation hub.
- **`pages/`**: This directory houses the individual pages of the application, such as File Management, Project Analysis, and the various simulators.
- **`core/`**: Contains the core business logic of the application, most notably the `evm_engine.py` which is responsible for all EVM-related calculations.
- **`services/`**: Provides a suite of services for data management, EVM calculations, and data formatting, encapsulating key business operations.
- **`models/`**: Defines the data models used throughout the application, ensuring data consistency and integrity.
- **`utils/`**: A collection of utility functions that support various aspects of the application, including authentication, date handling, and Firebase integration.
- **`requirements.txt`**: A standard Python requirements file listing all project dependencies.
- **`render.yaml`**: A configuration file for deploying the application on the Render platform.
- **`mkdocs.yml`**: A configuration file for the MkDocs documentation site, streamlining the process of generating and maintaining project documentation.

## Building and Running

To get the application up and running on your local machine, follow these simple steps:

1.  **Install Dependencies:**
    Open your terminal and run the following command to install all the necessary Python packages:
    ```sh
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    Once the dependencies are installed, you can start the Streamlit application with this command:
    ```sh
    streamlit run main.py
    ```
    This will launch the application in your default web browser.

## Development Conventions

The project adheres to a set of modern development practices to maintain a high standard of code quality and consistency.

- **Modular Design:** The codebase is organized into distinct modules, each with a specific responsibility. This separation of concerns—encompassing the UI, business logic, and data layers—makes the application easier to understand, maintain, and extend.
- **Type Hinting:** The project makes extensive use of Python's type hints, which improves code clarity and allows for static analysis, helping to catch potential errors early in the development process.
- **Structured Codebase:** The project follows a clear and logical directory structure, making it easy to locate and work with different parts of the application.

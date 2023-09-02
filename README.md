# Hansard Topic Explorer

## Overview

The Hansard Topic Explorer is a web application built using Flask. It allows users to explore topics discussed in the UK Parliament by querying a database of speeches. The application provides various features like filtering speeches by year, party, and name, and displays related topics and keywords.

## Database Requirements

To run this project, you will need a database with a table named `hansard` structured as follows:

```sql
CREATE TABLE "hansard" (
    "index" INTEGER, 
    "speech_id" TEXT, 
    "text" TEXT, 
    "date" TEXT, 
    "year" INTEGER, 
    "decade" INTEGER, 
    "proc_party" TEXT, 
    "scraped_name" TEXT, 
    "person_url" TEXT, 
    "topic_id" INTEGER
);
```

For a sample dataset or the webscraping code to collect this data, contact pamanteroberts@yahoo.co.uk.

## Features

- **Topic Querying**: Enter a keyword to find related topics.
- **Speech Filtering**: Filter speeches based on various parameters like year, party, and name.
- **Topic Charts**: View distribution of topics over decades.

## Prerequisites

- Python 3.8 or higher
- Flask
- Flask-Bootstrap
- Flask-WTF
- SQLAlchemy
- Pandas
- TheFuzz

## Installation

1. Clone the repository.

    ```
    git clone https://github.com/ptear/hansard-topic-explorer.git
    ```

2. Navigate to the project directory.

    ```
    cd hansard-topic-explorer
    ```

3. Create a virtual environment.

    ```
    python3 -m venv venv
    ```

4. Activate the virtual environment.

    - On macOS and Linux:
    
        ```
        source venv/bin/activate
        ```
    
    - On Windows:
    
        ```
        .\venv\Scripts\activate
        ```

5. Install dependencies.

    ```
    pip install -r requirements.txt
    ```

## Usage

1. Set environment variables (Optional).

    ```
    export SECRET_KEY=your-secret-key
    ```

2. Run the Flask application.

    ```
    flask run
    ```

3. Open your web browser and go to `http://127.0.0.1:5000/`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

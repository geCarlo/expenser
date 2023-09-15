# expenser

Simple tool meant for ingesting .csv exports from credit accounts and convert into a "universal" csv file.

## First time setup instructions:

1. Create your virtual environment

    ```
    python3 -m venv venv
    ```

2. Source the environment

    ```
    source venv/bin/activate
    ```

3. Install the requirements

    ```
    python3 -m pip install -r requirements.txt
    ```

## Running the tool

### Processing raw data

1. Export expenses from your credit/debit account in csv format (if you are given the option between Windows and Mac csv, choose Windows)

1. Place the raw csv files into the `data/raw` directory of this project

1. Assuming your venv is activated, you can run the tool with

    ```
    python3 expenser.py -p
    ```

### Configuring your categories

TODO: Finish this

### Displaying your expenses

TODO: Finish this


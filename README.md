# Leetcode-Sheet-Automator
A simple python script to update problem solving progress on Leetcode in a Google Sheet.

### Motivation
Problem-Solving is a necessary skill for every software engineer. Leetcode is a great website for developing it. This script can enable you and your colleagues to track each other progress and push you to the limits.

### Disclaimer 
This project uses a non-public API Leetcode for querying the progress. Please note that the use of this API may violate the terms of service of Leetcode. The developer of this project is not responsible for any legal issues or damages that may arise from the use of this API. Use this project at your own risk.

## How to use
This script can be automated to run using GitHub Actions to run every 5 minutes or locally on your machine.

### A. Using GitHub Actions

- Fork the repo to your account

- Update usernames in `usernames` file. It should be in the format `username:column_name`. The column name is the name of the column as written in first row to reference the username owner. 

- Save sheet ID as a GitHub actions secret as `LEETCODE_SHEET`.

- [Create Sheets API credentials using Google Cloud.](https://docs.gspread.org/en/latest/oauth2.html)

- Save the contents of the JSON file obtained in last step as a GitHub actions secret as `GOOGLE_CREDENTIALS`.


### B. Locally

- Use the package manager [pip] to install dependencies
```bash
pip install requirements.txt
```

- Save Sheet ID in environment variables as `LEETCODE_SHEET`.

- [Create Sheets API credentials using Google Cloud.](https://docs.gspread.org/en/latest/oauth2.html)

- Save credentials obtained as `credentials.json` in the project folder.

- Run the script 


## Sheet Layout
An example can be found [here](https://docs.google.com/spreadsheets/d/1rHrXR2ygEfAlKZdcOHFZzD97x2TKhF8IK7CY0NT3lkg/edit?usp=sharing). You can create a copy of it.

The spreadsheet should have a separate work sheet for each difficulty level. These worksheets names should be "Easy", "Medium", "Hard" respectively.

Each worksheet should have a column for Problem Name and a column for Category.

The format is as follows:

| Problem Name   | Category          | Hints (optional) | Muhammad |   Magdy  |
| -----------    | -----------       |   -------------  |   -----  |----------|
| Two Sum        | Array, Hash Table |                  |     AC   |          |
| Ugly Number    | Math              |                  |          |    AC    |

For this example 'Muhammad' and 'Magdy' should be a column name in the usernames file.

If a problem already exists in the sheet, only the AC status will be added without duplicating the row.

The category column is filled automatically.

You can add additional worksheets for a specific set of problems, such as Leetcode 75. In that case you will add each problem name manually. An example of this is implemented in the code.


## Limitations
Due to limitations in Leetcode API, only the last 15 accepted problems are added. That being said, if you already solved 100 problems before using this script only the last 15 will be added. (This can be viewed as an advantage to encourage you to solve now).

Also, if you stopped the script for while there is a chance that some problems won't be added due to the limitation as mentions before. Thus, it is advised to run it periodically on GitHub actions.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
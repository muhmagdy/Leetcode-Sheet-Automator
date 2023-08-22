from types import NoneType
import gspread
import requests
from datetime import datetime
import time
# import threading
import os


# Set up Google Sheets API credentials
try:
    GOOGLE_CREDENTIALS = os.environ["GOOGLE_CREDENTIALS"]
    print('Credentials found in env, Saving as \'credentials.json\'.')
    with open('credentials.json', 'w') as f:
        f.write(GOOGLE_CREDENTIALS)
except KeyError:
    print('Credentials not found in env, Looking for file directly.')
client = gspread.service_account(filename='credentials.json')

# # Set up the spreadsheet and worksheet names
# spreadsheet_name = 'Your Google Sheet Name Here'
easy_worksheet_name = 'Easy'
medium_worksheet_name = 'Medium'
hard_worksheet_name = 'Hard'
leetcode_worksheet_name = 'Leetcode 75'

# Set up the list of users
usernames = list()
names_in_sheet = dict()
with open('usernames', 'r') as f:
    for line in f:
        if(line[0] == '/'):
            continue;
        splitted = line.split(':')
        usernames.append(splitted[0])
        names_in_sheet[splitted[0]] = splitted[1].removesuffix('\n')
print(usernames)

leetcode_url = 'https://leetcode.com/graphql/'

# Helper function to retrieve problem information from LeetCode API
def get_problem_difficulty(problem_slug):
    json_data = {
        'query': '\n    query questionTitle($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    title\n    titleSlug\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n  }\n}\n    ',
        'variables': {
            'titleSlug': problem_slug,
        },
        'operationName': 'questionTitle',
    }
    response = requests.post(leetcode_url, json=json_data)
    data = response.json()
    return data['data']['question']['difficulty']

def get_problem_topics(problem_slug):
    json_data = {
        'query': '\n    query singleQuestionTopicTags($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    topicTags {\n      name\n      slug\n    }\n  }\n}\n    ',
        'variables': {
            'titleSlug': problem_slug,
        },
        'operationName': 'singleQuestionTopicTags',
    }
    response = requests.post(leetcode_url, json=json_data)
    topics = list(map(lambda x: x['name'], response.json()['data']['question']['topicTags']))
    if('Depth-First Search' in topics):
        topics[topics.index('Depth-First Search')] = 'DFS'
    if('Breadth-First Search' in topics):
        topics[topics.index('Breadth-First Search')] = 'BFS'
    if('Dynamic Programming' in topics):
        topics[topics.index('Dynamic Programming')] = 'DP'
    if('Binary Search Tree' in topics):
        topics[topics.index('Binary Search Tree')] = 'BST'
    return topics
    


# Helper function to update a cell in a worksheet
def update_cell(worksheet, row_index, col_index, value):
    worksheet.update_cell(row_index, col_index, value)

def update_accepted(worksheet: gspread.Worksheet, row, username):
    column = worksheet.row_values(1).index(names_in_sheet[username])+1
    update_cell(worksheet, row, column, "AC")

# Helper function to check if a problem exists in a worksheet
def problem_exists(worksheet: gspread.Worksheet, problem_title):
    cell_list = worksheet.col_values(1)
    for i, cell in enumerate(cell_list):
        if problem_title in cell:
            return i+1
    else:
        return False

# Retrieve the worksheets from the Google Sheet
sheet_id = os.environ["LEETCODE_SHEET"]
spreadsheet = client.open_by_key(sheet_id)
easy_worksheet = spreadsheet.worksheet(easy_worksheet_name)
medium_worksheet = spreadsheet.worksheet(medium_worksheet_name)
hard_worksheet = spreadsheet.worksheet(hard_worksheet_name)
leetcode_worksheet = spreadsheet.worksheet(leetcode_worksheet_name)

latest_updated_time = datetime.fromtimestamp(float(leetcode_worksheet.cell(25, 30).value))

new_update_time = datetime.fromtimestamp(time.time())

print(f"Last Updated Time = {latest_updated_time}, Now = {new_update_time}")

def update_sheet():
    global latest_updated_time
    # Loop through the users and retrieve their submissions
    for user in usernames:
        json_data = {
            'query': '\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n    id\n    title\n    titleSlug\n    timestamp\n  }\n}\n    ',
            'variables': {
                'username': user,
                'limit': 30,
            },
            'operationName': 'recentAcSubmissions',
        }

        response = requests.post(leetcode_url, json=json_data)
        accepted_problems = response.json()['data']['recentAcSubmissionList']

        if type(accepted_problems) == NoneType:
            continue
        
        print(f"[{user}]")
        
        # Loop through the submissions and update the corresponding cells in the worksheets
        for problem in accepted_problems:
            problem_id = problem['id']
            problem_slug = problem['titleSlug']
            problem_title = problem['title']
            problem_dt = datetime.fromtimestamp(int(problem['timestamp']))
            if problem_dt < latest_updated_time:
                break
            problem_difficulty = get_problem_difficulty(problem_slug)
            problem_topics = get_problem_topics(problem_slug)
            print(problem_title, problem_difficulty)
            # status = problem['status_display']
            worksheet = None

            # Determine which worksheet to update based on the problem difficulty
            if problem_difficulty == "Easy":
                worksheet = easy_worksheet
            elif problem_difficulty == "Medium":
                worksheet = medium_worksheet
            elif problem_difficulty == "Hard":
                worksheet = hard_worksheet

            row_index = problem_exists(worksheet, problem_title)
            # Check if the problem exists in the worksheet
            if not row_index:
                # If the problem doesn't exist, add it to the worksheet
                row_list = worksheet.col_values(1)
                try:
                    row_index = row_list.index("")+1
                except ValueError:
                    row_index = len(row_list)+1
                update_cell(worksheet, row_index, 1, f'=HYPERLINK("https://leetcode.com/problems/{problem_slug}/", "{problem_title}")')
                update_cell(worksheet, row_index, 2, ", ".join(problem_topics))

            # Update the cell representing the user's submission status
            cell_list = worksheet.findall(problem_title)
            # row_index = cell_list[0].row
            # col_index = worksheet.find(user).col
            # update_cell(worksheet, row_index, col_index, 'AC')
            update_accepted(worksheet, row_index, user)
            # Check if the problem exists in the LeetCode 75 worksheet
            # Update the cell representing the user's submission status in the LeetCode 75 worksheet
            if row_index := problem_exists(leetcode_worksheet, problem_title):
                update_accepted(leetcode_worksheet, row_index, user)
            time.sleep(5)
    latest_updated_time = datetime.fromtimestamp(time.time()-600)
    update_cell(leetcode_worksheet, 25, 30, new_update_time.timestamp())
    print('Done');



# while True:
#     if threading.active_count() > 1:
#         time.sleep(100)
#         continue
#     thread = threading.Thread(target=update_sheet)
#     thread.start()
#     time.sleep(600)

update_sheet();

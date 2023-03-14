import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import traceback

def convert_time(time_str):
    if time_str.endswith("hours ago") or time_str.endswith("hour ago"):
        hours_ago = int(time_str.split()[0])
        timestamp = (datetime.utcnow() - timedelta(hours=hours_ago)).timestamp()
    elif time_str.endswith("days ago") or time_str.endswith("day ago"):
        days_ago = int(time_str.split()[0])
        timestamp = (datetime.utcnow() - timedelta(days=days_ago)).timestamp()
    elif time_str.endswith("months ago") or time_str.endswith("month ago"):
        months_ago = int(time_str.split()[0])
        timestamp = (datetime.utcnow() - timedelta(days=months_ago*30)).timestamp()
    elif time_str.endswith("minutes ago") or time_str.endswith("minute ago"):
        minutes_ago = int(time_str.split()[0])
        timestamp = (datetime.utcnow() - timedelta(minutes=minutes_ago)).timestamp()
    else:
        # handle other time formats as needed
        pass
    return int(timestamp)

def remove_comment(comment_str):
    """
    Converts a string of the form "X Comment(s)" into a String X.
    """
    # Split the string into a list of words
    words = comment_str.split()

    # Check if the second-to-last word is "Comment" or "Comments"
    if words[-1] == "Comment" or words[-1] == "Comments":
        # Convert the first word to an integer and return it
        return words[0]
    else:
        # If the string is not in the correct format, raise an exception
        raise ValueError("Invalid comment string format")

def convert_number(text):
    """
    Converts a String of form 1.3k into an int 1300
    """
    if text == 'Vote':
        return 0
    
    suffixes = {
        "k": 1000,
        "M": 1000000,
        # add more suffixes as needed
    }
    if text[-1] in suffixes:
        return int(float(text[:-1]) * suffixes[text[-1]])
    else:
        return int(text)


PATH = "/data/Downloads/chromedriver"
base_xpath = '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[4]/div[1]/div[4]/div[{}]'

chrome_options = webdriver.ChromeOptions()
browser = webdriver.Chrome(options=chrome_options, executable_path=PATH)
browser.maximize_window() # For maximizing window

browser.get("https://www.reddit.com/r/france/")
time.sleep(3)

# accept_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div/section/div/section[2]/section[1]/form/button'))).click()

target_count = 10000

title_list = []
user_list = []
nb_votes_list = []
nb_comments_list = []
date_list = []
category_list = []
text_content_list = []
result_dict = {}


for i in range(2, target_count):
    try:
        # time.sleep(1)
        print(i)
        xpath = base_xpath.format(i)
        block = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        wait = WebDriverWait(block, 20)
        #scroll page
        block.location_once_scrolled_into_view
        
        if i%10 == 9:
            
            #save in csv
            df = pd.DataFrame(result_dict)
            df.to_csv('reddit2.csv', index=False)
        
        try:
            # If promotion we continue the loop
            if block.find_element(By.CLASS_NAME, '_2oEYZXchPfHwcf9mTMGMg8').text == 'Promoted':
                continue
        except:
            pass
        
        title = wait.until(EC.visibility_of_element_located((By.XPATH, './/h3'))).text
        user = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'a'))).text
        nb_votes = convert_number(wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_1E9mcoVn4MYnuBQSVDt1gC'))).text)
        nb_comments_text = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'FHCV02u6Cp2zYL0fhQPsO'))).text
        nb_comments_str = remove_comment(nb_comments_text)
        nb_comments = convert_number(nb_comments_str)
        date = convert_time(wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_2VF2J19pUIMSLJFky-7PEI'))).text)
        category = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_2xu1HuBz1Yx6SP10AGVx_I'))).text
        text_content = block.find_element(By.CLASS_NAME, 'STit0dLageRsa2yR4te_b').text[:200]
        
        #save in dictionary
        title_list.append(title)
        user_list.append(user)
        nb_votes_list.append(nb_votes)
        nb_comments_list.append(nb_comments)
        date_list.append(date)
        category_list.append(category)
        text_content_list.append(text_content)
        result_dict = {'title': title_list, 
                    'username': user_list, 
                    'votes_number': nb_votes_list, 
                    'comments_number': nb_comments_list, 
                    'date_timestamp': date_list, 
                    'category': category_list, 
                    'text_content': text_content_list}

    except Exception as e:
        print('for loop error', repr(e))
        traceback.print_exc()
            
            
    


browser.quit()
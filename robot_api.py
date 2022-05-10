# Importing libraries
import re
import time
import sqlite3
import khayyam
from bs4 import BeautifulSoup
from tabulate import tabulate    
from selenium import webdriver   
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Preparing the database
conn = sqlite3.connect('class_absentees_database.db')
c = conn.cursor()
c.execute('''
             CREATE TABLE IF NOT EXISTS absentees (
                student text,
                class text,
                date text
                 )
                    ''')
conn.commit()

def adding_student(student, classroom, date):
    with conn:
        c.execute('INSERT INTO absentees VALUES (:student, :class, :date)', {'student':student, 'class':classroom, 'date':date})

def show_all_students_by_class(classroom):
    c.execute('SELECT * FROM absentees WHERE class = :class',({'class':classroom}))
    return c.fetchall()


def clear_class_list(classroom):
    with conn:
        c.execute('DELETE FROM absentees WHERE class = :class', {'class':classroom})

def show_all_students_by_name(student):
    c.execute('SELECT * FROM absentees WHERE student = :student',({'student':student}))
    return c.fetchall()


# Introduction and tips
print('''\nHello, I am shad attendance check robot!
Please answer the questions and if you have any problems, read the guide:''')
while True:
    a = input(
'''
|start -----> Start attendance check
|show list -----> Show absent students
|clear list -----> Clear the list of absent students in a class
|exit -----> Exiting the app\n
Please enter your order to begin:
'''

)
    if a == 'show list':
        a1 = input('\nDo you want to be separated by the name of the class or by the name of the student?(class name or student?)\n')
        if a1 == 'class name':
            classname = input('Please enter class name:\n')
            pdtabulate=lambda df:tabulate(df,tablefmt='psql')
            print(pdtabulate(show_all_students_by_class(classname)))
        if a1 == 'student':
            studentname = input('Please enter student name:\n')
            pdtabulate=lambda df:tabulate(df,tablefmt='psql')
            print(pdtabulate(show_all_students_by_name(studentname)))

    if a == 'clear list':
        a2 = input('Enter class name:\n')
        clear_class_list(a2)
    if a == 'exit':
        print('''\nThank you very much for using this program\nhave a nice day
\nGoodbye!\n''')
        c.close()
        break
    
    if a == 'start':

        my_phone_number = input(

            '''Please enter your phone number\nthat your shad account is based on:\n'''
            )


        # Variables
        class_absentees = {}
        students_list = []
        students_status_list = []

        # Web browser settings
        options = Options()
        options.headless = True 
        time.sleep(0.5)
        options.add_argument('chromedriver --log-level=OFF')
        time.sleep(0.5)
        driver = webdriver.Chrome(options=options)
        # Login to shad account
        driver.get('https://web.shad.ir/')
        time.sleep(0.5)
        phone_number= driver.find_element_by_xpath('//input[@name="phone_number"]')
        time.sleep(1)
        phone_number.click()
        time.sleep(0.5)
        time.sleep(0.5)
        phone_number.send_keys(my_phone_number, Keys.ENTER)
        time.sleep(1)
        driver.find_element_by_xpath('//span[@rb-localize="modal_ok"]').click()
        time.sleep(2)
        code = input('''\nPlease enter your verification code:\n''')
        verify_code = driver.find_element_by_xpath('/html/body/div/app-root/tab-login/div/div[2]/div[2]/form/div[4]/input')
        verify_code.click()
        verify_code.send_keys(code)
        # Finding classroom
        class_name = input(
            '''\nplease enter classroom name for attendance check
(Make sure this name is exactly the same as the class name in shad):\n''')
        driver.find_element_by_partial_link_text(class_name).click()
        # Extract student lists
        driver.find_element_by_class_name('tg_head_peer_title').click()
        html_text = driver.page_source
        time.sleep(1)
        html_text = driver.page_source
        soup = BeautifulSoup(html_text, 'html.parser')
        students = soup.find_all('a', attrs={'class':"md_modal_list_peer_name"})
        students_statuses = soup.find_all('div', attrs={'bot-chat-privacy':'true'})

        for student in students:
            students_list.append(re.findall(r'.*>(.*)<', str(student)))

        for status in students_statuses:
            students_status_list.append(re.findall(r'.*>(.*)<', str(status)))
        # show students of class
        print('''\nstudents of %s class:\n'''%(class_name))
        for i in range(len(students_list)):
            class_absentees.update({students_list[i][0] : students_status_list[i][0]})
            print(students_list[i][0],'\n', students_status_list[i][0],'\n')
        # Attendance check
        class_absentees_values = list(class_absentees.values())
        class_absentees_keys = list(class_absentees.keys())
        print('''\nAbsentees of %s class:\n'''%(class_name))
        for i in range(len(class_absentees)):
            if class_absentees_values[i] == 'آنلاین':
                pass
            else:
                adding_student(str(class_absentees_keys[i]), class_name, str(khayyam.JalaliDate.today()))
        pdtabulate=lambda df:tabulate(df,tablefmt='psql')
        print(pdtabulate(show_all_students_by_class(class_name)))

        driver.find_element_by_xpath('/html/body/div[1]/app-root/app-modal-container/div/app-modal-view/div/div/div/modal-chat-info/div/div[1]/div[1]/div[1]/a').click()
        time.sleep(0.5)
        driver.find_element_by_xpath('/html/body/div[1]/app-root/span/rb-head/div/div/div[1]/div/a/div/span[2]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath('/html/body/div[1]/app-root/span/rb-head/div/div/div[1]/div/ul/li[5]/a/span').click()
        driver.close()
conn.close()

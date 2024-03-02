import json
import sys
import time
import os
import SaveExcelToJson
import FuncPrint

def account_read_test_stud_num():
    json_file_name = "account.json"
    fi_json = open(json_file_name, 'r', encoding='utf-8')
    content = fi_json.read()
    account = json.loads(content)
    fi_json.close()
    return account["student_number"]

# 读取需要考试的科目
def account_read_test_subject():
    json_file_name = "account.json"
    fi_json = open(json_file_name, 'r', encoding='utf-8')
    content = fi_json.read()
    account = json.loads(content)
    fi_json.close()
    return account["test_subject"]


# 读取账号 密码
def account_read_cookies():
    json_file_name = "cookies.json"
    fi_json = open(json_file_name, 'r', encoding='utf-8')
    content = fi_json.read()
    dict_cookies = json.loads(content)
    fi_json.close()
    return dict_cookies["cookies"]


# 向json 文件写入新的cookies
def account_write_cookies(cookies_new):
    json_file_name = "cookies.json"
    dict_cookies = {"cookies": []}
    for item in cookies_new:
        dict_cookies["cookies"].append({"value": item["value"], "name": item["name"]})

    j_dump = json.dumps(dict_cookies, ensure_ascii=False, indent=2)
    fo_json = open(json_file_name, 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()

# 读取全部学生的科目考试情况
def account_read_stud_db():
    fi_json = open("stud_db.json", 'r', encoding='utf-8')
    content = fi_json.read()
    db = json.loads(content)
    fi_json.close()
    return db

# 把 Excel 的Task 列表读到json 文件中
def account_updata_excel_task2json():
    FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    file_path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
    excel_file_path = file_path + "\Excel"
    excel_file_name = excel_file_path + "\TaskList.xlsx"
    list_keys_tasks = SaveExcelToJson.setj_parse_excel(excel_file_name)
    keys = list_keys_tasks[0]
    tasks = []
    for item in list_keys_tasks[1:]:
        dict_task = {}
        for index, key in enumerate(keys):
            dict_task[key] = item[index]
        tasks.append(dict_task)

    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          "tasks:")
    for item in tasks:
        print(item)
    account_write_json_task(tasks)
    FuncPrint._func_out_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)


def account_write_json_task(list_tasks):
    j_dump = json.dumps(list_tasks, ensure_ascii=False, indent=2)
    fo_json = open("TaskList.json", 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()


# 从json 文件中读取全部task
def account_read_json_task():
    json_file_name = "TaskList.json"
    try:
        fi_json = open(json_file_name, 'r', encoding='utf-8')
        content = fi_json.read()
        list_tasks = json.loads(content)
        fi_json.close()
        return list_tasks
    except:
        print("[account_read_json_task]" + "没有找到文件 " + json_file_name)
        return []


def account_read_doing_task():
    dict_doing_task = {}
    list_tasks = account_read_json_task()
    for dict_task in list_tasks:
        if "STATUS" in dict_task:
            if dict_task["STATUS"] == "Doing":
                dict_doing_task = dict_task
                break

    if dict_doing_task:
        print("[account_read_doing_task]dict_doing_task:")
        print(dict_doing_task)
    else:
        print("[account_read_doing_task]No doing")
    return dict_doing_task


def account_update_json_next_task():
    print("[account_update_json_next_task] IN")
    list_tasks = account_read_json_task()
    dict_next_task = {}
    for index, dict_task in enumerate(list_tasks):
        if "STATUS" in dict_task:
            if dict_task["STATUS"] == "Doing":   # 把 Doing 状态切换成 Done 状态
                list_tasks[index]["STATUS"] = "Done"
                break

    for index, dict_task in enumerate(list_tasks):
        if "STATUS" in dict_task:
            if dict_task["STATUS"] == "Todo":  # 把 Todo 状态切换成 Doing 状态
                list_tasks[index]["STATUS"] = "Doing"
                dict_next_task = list_tasks[index]
                break

    account_write_json_task(list_tasks)
    if dict_next_task:
        print("next task:")
        print(dict_next_task)
    else:
        print("[account_update_json_next_task]全部 task 已经完成")
    print("[account_update_json_next_task] OUT")
    return dict_next_task

def account_update_stud_courses_to_db(list_courses):
    print("account_update_reg_courses_to_db() IN")
    dict_doing_task = account_read_doing_task()
    stud_num = dict_doing_task["student_number"]  #获取当前在做题目的学生
    db = account_read_stud_db()
    if stud_num not in db:
        db[stud_num] = {
                        stud_num: stud_num,
                        "student_name": dict_doing_task["student_name"],
                        "password": dict_doing_task["password"]
                        }

    if "stud_courses" not in db[stud_num]:
        db[stud_num]["stud_courses"] = {}

    for course in list_courses:
        db[stud_num]["stud_courses"][course["data-course-id"]] = course

    j_dump = json.dumps(db, ensure_ascii=False,  indent=2)
    # print(j_dump)
    fo_json = open("stud_db.json", 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()


def account_update_stud_papers_to_db(list_papers, course_id):
    print("account_update_stud_papers_to_db() IN")
    dict_doing_task = account_read_doing_task()
    stud_num = dict_doing_task["student_number"]  # 获取当前在做题目的学生
    db = account_read_stud_db()
    if stud_num not in db:
        db[stud_num] = {
                        stud_num: stud_num,
                        "student_name": dict_doing_task["student_name"],
                        "password": dict_doing_task["password"]
                        }

    if "stud_courses" not in db[stud_num]:
        db[stud_num]["stud_courses"] = {}

    if course_id not in db[stud_num]["stud_courses"]:
        db[stud_num]["stud_courses"][course_id] = {}

    if "stud_courses_papers" not in db[stud_num]["stud_courses"][course_id]:
        db[stud_num]["stud_courses"][course_id]["stud_courses_papers"] = {}

    for paper in list_papers:
        db[stud_num]["stud_courses"][course_id]["stud_courses_papers"][paper["id"]] = paper

    j_dump = json.dumps(db, ensure_ascii=False, indent=2)
    # print(j_dump)
    fo_json = open("stud_db.json", 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()
    print("account_update_stud_papers_to_db() OUT")


def account_main():
    Account.account_updata_excel_task2json()
    Account.account_read_json_task()
    Account.account_read_doing_task()
    Account.account_update_json_next_task()

import ParseTxt
import Account
import json
import time
import os
import re
import hashlib
import copy
from zhon.hanzi import punctuation
from selenium import webdriver


DOING_TASK = {}
def _sel_get_doing_task():
    global  DOING_TASK
    DOING_TASK = Account.account_read_doing_task()
    return DOING_TASK

def _sel_updata_doing_task():
    global DOING_TASK
    DOING_TASK = Account.account_update_json_next_task()
    return DOING_TASK

def _sel_open_local_driver(enter_url):
    USER_AGENT = "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.32"
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(USER_AGENT)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(enter_url)
    return driver



LOGIN_URL = ""
# 判断是没有登录，就重新登录
def sel_login_new_account(driver):
    account = DOING_TASK
    url = LOGIN_URL
    if LOGIN_URL.len == 0 :
        print("请设置 LOGIN_URL")
        return
    # 登录地址
    driver.get(
        "https://authserver.ougd.cn/authserver/login?service=https%3A%2F%2Fcourse.ougd.cn%2Flogin%2Findex.php%3FauthCAS%3DCAS")

    # 选择账号密码登录
    time.sleep(1)
    button = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[1]/ul/li[2]/span")
    button.click()

    # 账号
    element = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[3]/div[2]/form/p[1]/input")
    element.send_keys(account["student_number"])
    # 密码
    pws = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[3]/div[2]/form/p[2]/input[1]")
    pws.send_keys(account["password"])
    # 登录
    button = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[3]/div[2]/form/p[5]/button")
    button.click()
    # 获取 cookie
    cookies_new = driver.get_cookies()
    print(account["student_name"] + "成功登录！")
    print("new cookies:" + cookies_new.__str__())
    Account.account_write_cookies(cookies_new)


# 获取学生报名的科目
# return reg_courses
def sel_parse_courses(driver):
    print("[IN] sel_parse_courses")
    reg_courses = []
    for i in range(0, 9):
        # 等页面加载完成
        time.sleep(1)
        course_plates = driver.find_elements_by_class_name('paged-content-page-container')
        if len(course_plates) > 0:
            break
        if i >= 9:
            print("页面加载失败")

    for course_plate in course_plates:
        courses = course_plate.find_elements_by_class_name('card.dashboard-card')
        for i in range(0, 10):
            if len(courses) <= 0:
                print("没有找到 card.dashboard-card ,等3秒再试试")
                time.sleep(3)
                courses = course_plate.find_elements_by_class_name('card.dashboard-card')
            else:
                break

        if len(courses) <= 0:
            print("没有找到 card.dashboard-card ,等3秒再试试")
            time.sleep(3)
            courses = course_plate.find_elements_by_class_name('card.dashboard-card')

        if len(courses) <= 0:
            print("没有找到 card.dashboard-card ,等3秒再试试")
            time.sleep(3)
            courses = course_plate.find_elements_by_class_name('card.dashboard-card')

        for course in courses:
            dict_course = {}
            dict_course["data-course-id"] = course.get_attribute('data-course-id')
            dict_course["title"] = course.find_element_by_class_name('coursename.text-truncate').get_attribute('title')
            dict_course["short_title"] = dict_course["title"].split("（")[0]
            dict_course["href"] = course.find_element_by_class_name('coursename.text-truncate').get_attribute('href')
            try:
                dict_course["strong"] = course.find_element_by_tag_name('strong').text
            except:
                dict_course["strong"] = "100%"
            reg_courses.append(dict_course)
    print("[OUT] sel_parse_courses")
    return reg_courses


# 查找课程考核类型，例如 学习内容 形成性考核
# 点击学习内容 标签
def sel_parse_course_asse_type(driver, label="形成性考核"):
    asse_types = driver.find_elements_by_class_name('tab_content')
    for asse_type in asse_types:
        try:
            context = asse_type.text.strip()
            if context == label:
                asse_type.click()
                break
        except:
            break


# 选择没有完成的考试 或者测试题目
def sel_click_not_com_exam(driver, course_id=None):
    try:
        sections = driver.find_elements_by_class_name('activity.quiz.modtype_quiz')
        papers = []
        for section in sections:
            dict_paper = {"data-course-id": course_id,
                          "id": section.get_attribute("id"),
                          "href": section.find_element_by_tag_name("a").get_attribute("href")
            }
            status = False
            try:
                status = section.find_element_by_class_name("icon").get_attribute("src").find("auto-y") >= 0
            except:
                print("[sel_click_not_com_exam] no auto-y")
            dict_paper["status"] = status

            papers.append(dict_paper)

        url_sections = driver.find_elements_by_class_name('activity.url.modtype_url')
        for section in url_sections:
            dict_paper = {"data-course-id": course_id,
                          "id": section.get_attribute("id"),
                          "href": section.find_element_by_tag_name("a").get_attribute("href"),
                          "status": False}
            papers.append(dict_paper)

        print("[sel_click_not_com_exam] papers len " + len(papers).__str__())
        if course_id is not None:
            Account.account_update_stud_papers_to_db(papers, course_id)
        task = DOING_TASK
        task_papers_mode = task["papers"].__str__()
        print("[sel_click_not_com_exam] task mode :" + task_papers_mode.__str__())
        list_task_papers_mode = task_papers_mode.split(",")
        print("[sel_click_not_com_exam] task mode  list: " + list_task_papers_mode.__str__())
        for index, paper in enumerate(papers):
            if "All" in list_task_papers_mode:
                print("All test")
            elif "Auto" in list_task_papers_mode:
                if paper["status"]:  # 判断没有完成的测试
                    print("此题已经做过")
                    continue
                else:
                    print("Auto Test")
            elif (index.__str__()) in list_task_papers_mode:
                print("自定义:" + index.__str__() + "  " + list_task_papers_mode.__str__())
            else:
                print("不符合条件，跳过答题")
                continue

            print("[sel_click_not_com_exam]" + paper.__str__())
            driver.get(paper["href"])

            # 停在此处
            if task["auto_submit"] == "Hold":
                time.sleep(10000)

            if task["review"] == "Yes":
                print("[sel_click_not_com_exam]  review 开始")
                reviews = driver.find_elements_by_class_name("cell.c3")
                print("[sel_click_not_com_exam] cell.c3 len : " + len(reviews).__str__())
                list_table = []
                for review in reviews:
                    print(review.text)
                    if review.text == "回顾":
                        table = review.find_element_by_tag_name("a")
                        print(table.text)
                        list_table.append(table.get_attribute('href'))

                if len(list_table) <= 0:
                    reviews = driver.find_elements_by_class_name("cell.c4")
                    print("[sel_click_not_com_exam] cell.c3 len : " + len(reviews).__str__())
                    print("[sel_click_not_com_exam] cell.c4 len : " + len(reviews).__str__())
                    list_table = []
                    for review in reviews:
                        print(review.text)
                        if review.text == "回顾":
                            table = review.find_element_by_tag_name("a")
                            print(table.text)
                            list_table.append(table.get_attribute('href'))

                for table in list_table:
                    print(table)
                    driver.get(table)
                    time.sleep(1)
                    try:
                        othernav = driver.find_element_by_class_name("othernav")
                        list_a = othernav.find_elements_by_tag_name("a")
                        for a in list_a:
                            print("[sel_parse_correct_answer]" + a.text)
                            if a.text == "所有题目显示在一页":
                                a.click()
                                break
                    except:
                        print("[sel_parse_correct_answer] no oternav")

                    sel_parse_correct_answer(driver)  # 保存做过的答案，并且更新题库

                # review 完成还需要会到答题的页面
                driver.get(paper["href"])
                continue                    #  如果只是review 就不要去答题了


            if task["auto_answer"] == "No":  #  如果设置了自动答题才会选开始
                print("[sel_click_not_com_exam]  跳过答题")
                continue
            time.sleep(2)
            try:
                enters = driver.find_element_by_class_name("singlebutton.quizstartbuttondiv")
                enters.click()  # 点击确认开始考试
                time.sleep(1)
                enters = driver.find_elements_by_id("id_submitbutton")
                for enter in enters:
                    print(enter.text)
                    if enter.get_attribute("value") == "开始答题":
                        print("开始答题")
                        enter.click()
                time.sleep(1)
                sel_parse_paper(driver)  # 自动答题
                time.sleep(1)
            except:
                print("[sel_click_not_com_exam]没有找到开始答题按钮")

            #  先debug 一下，不用自动提交答案 ,配置成自动答题才会自动答题
            if task["auto_submit"] == "Yes":
                sel_click_submit(driver)  # 自动提交答案
                sel_parse_correct_answer(driver)  # 保存反馈的答案，并且更新题库


        print("[sel_click_not_com_exam] " + len(sections).__str__() + " 套试题已经全部作答完毕")
    except:
        return


# 从题库中获取正确答案
def sel_get_answer(stem):
    main_file_path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
    txt_file_path = main_file_path + "\SelQuestionBank\/"
    course = DOING_TASK["test_subject"]

    # 去除题目中的中文标点符号，并去空格
    stem = "".join(re.sub(r"[%s]+" % punctuation, "", stem).split())

    test_papers = ParseTxt.parse_json_file_to_list(txt_file_path + course + ".json")
    questions = []
    correct_answer = []

    for index, topic in enumerate(test_papers):
        if len(topic) >= 3:
            questions.append(topic[0])
            # 去除题源中文标点符号，并去空格
            topic[1] = "".join(re.sub(r"[%s]+" % punctuation, "", topic[1]).strip().split())
            if topic[1].find(stem) >= 0:
                correct_answer = topic[2]
                print("题源是：" + topic[1] + "\n  新题库的 题目是：" + stem)
                break

    if len(correct_answer) <= 0:
        print("新题库没有找到答案, 尝试从旧题库中查找")
        test_papers = ParseTxt.parse_txt_file_to_list(txt_file_path + course + ".txt")
        print("新题库没有找到答案, 尝试从旧题库中查找 1")
        for index, topic in enumerate(test_papers):
            if len(topic) == 4:
                questions.append(topic[1])
                # 去除题源中文标点符号，并去空格
                topic[1] = "".join(re.sub(r"[%s]+" % punctuation, "", topic[1]).strip().split())
                if topic[1].find(stem) >= 0:
                    print("新题库没有找到答案, 尝试从旧题库中查找 2")
                    correct_answer = topic[2]
                    print("题源是：" + topic[1] + "\n  题目是：" + stem)
                    # print(topic[2])
                    break

    return correct_answer


# 确认提交答案
def sel_click_submit(driver):
    buttons = driver.find_elements_by_class_name("btn.btn-secondary")
    for button in buttons:
        if button.text.strip() == "提交所有答案并结束":
            print(button.text.strip())
            button.click()
            time.sleep(2)
            confir_buttons = driver.find_elements_by_class_name("btn.btn-primary")
            for confir_button in confir_buttons:
                if confir_button.get_attribute("value") == "提交所有答案并结束":
                    print("确认提交")
                    confir_button.click()
            break


# 读取选择题题目，并且选择正确答案
def sel_parse_paper(driver):
    print("读取选择题题目，并且选择正确答案")
    # 获取题目的数量
    question_numbers = driver.find_elements_by_class_name("qnbutton")
    print("题目的总数为：" + len(question_numbers).__str__())
    for index, item in enumerate(question_numbers):
        if index == 0:  # 如果是答过的题目, 重新在第一题作答
            item.click()
            break

    for index, item in enumerate(question_numbers):
        print("第" + (index + 1).__str__() + "页")
        contents = driver.find_elements_by_class_name("content")
        for c_index, content in enumerate(contents):
            try:
                question = content.find_element_by_class_name("formulation.clearfix")
            except:
                print("完成读取题目")
                break
            print("第" + (index + 1).__str__() + "页", "第" + (c_index + 1).__str__() + "题")
            # time.sleep(5)
            stem = question.find_element_by_class_name("qtext")
            print("题目： " + stem.text)
            correct_answers = sel_get_answer(stem.text)
            print("正确答案：" + correct_answers.__str__())
            labels = []
            try:
                answer = question.find_element_by_class_name("answer")
                labels = answer.find_elements_by_tag_name("label")
            except:
                print("没有 answer 选项")

            for la_index, label in enumerate(labels):
                str_option = label.text
                print("选项:" + la_index.__str__() + " " + str_option)
                option_checked = driver.find_element_by_id(label.get_attribute("for"))
                option_type = option_checked.get_attribute("type")
                # 标记正确答案
                if len(correct_answers) <= 0:   # debug
                    print("题库中没有这条题目, 任意选择一个答案")

                for answer in correct_answers:
                    if label.text.strip().find(answer) >= 0:
                        if option_type.find("checkbox") >= 0:
                            # 判断是否已选择
                            if option_checked.is_selected():
                                print("Already selected!")
                            else:
                                option_checked.click()
                        elif option_type.find("radio") >= 0:
                            option_checked.click()
        # debug
        # return
        time.sleep(1)
        try:
            next_button = driver.find_element_by_name("next")
            next_button.click()
        except:
            print("没有找到下一页")
            break
    print("答题完成")


# 获取试卷的正确答案并且存入题库
def sel_parse_correct_answer(driver):
    print("sel_parse_correct_answer")
    contents = driver.find_elements_by_class_name("content")
    bank_a_paper = []
    for c_index, content in enumerate(contents):
        try:
            question = content.find_element_by_class_name("formulation.clearfix")
        except:
            print("完成读取题目")
            break

        bank_a_topic = [c_index]
        bank_options = []
        bank_correct_options = []

        print("第" + (c_index + 1).__str__() + "题")
        stem = question.find_element_by_class_name("qtext")
        print("[sel_parse_correct_answer]题目： " + stem.text)
        bank_a_topic.append(stem.text)
        try:
            rightanswer = content.find_element_by_class_name("rightanswer")  # 选项
        except:
            print("[sel_parse_correct_answer] no rightanswer")
            continue
        input_type = ""
        labels = []
        try:
            answer = question.find_element_by_class_name("answer")
            input = answer.find_element_by_tag_name("input")
            input_type = input.get_attribute("type")
            labels = answer.find_elements_by_tag_name("label")
        except:
            print("[sel_parse_correct_answer] 没有找到 answer")
        if input_type == "radio" or input_type == "checkbox":
            for la_index, label in enumerate(labels):
                str_option = label.text
                answer_num = label.find_elements_by_class_name("answernumber")
                if len(answer_num) == 1:  # 去掉 A B  C  D  ,但是判断题不需要去除
                    opt_i = len(answer_num[0].text)
                    str_option = str_option[opt_i:].strip()
                print("选项:" + la_index.__str__() + " " + str_option)
                bank_options.append(str_option)  # 填入选项
            for index, bank_option in enumerate(bank_options):
                if rightanswer.text.find(bank_option) >= 0:
                    bank_correct_options.append(bank_option)  # 填入正确答案
        else:
            bank_options.append("text")  # 填入选项
            bank_correct_options.append(rightanswer.text)  # 填入正确答案

        bank_a_topic.append(bank_correct_options)
        bank_a_topic.append(bank_options)
        # 第一个填入hash 值，由于标记题库中是否有存在了
        topic_hash = hashlib.md5(bank_a_topic[1].encode('utf-8')).hexdigest() + \
                     hashlib.md5(bank_a_topic[2][0].encode('utf-8')).hexdigest()
        # 第一个填入hash 值，由于标记题库中是否有存在了
        bank_a_topic[0] = topic_hash.__str__()
        bank_a_paper.append(copy.deepcopy(bank_a_topic))
    sel_save_correct_answer(bank_a_paper)


def sel_save_correct_answer(bank_a_paper):
    main_file_path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
    txt_file_path = main_file_path + "\SelQuestionBank\/"
    course = DOING_TASK["test_subject"]
    ParseTxt.parse_list_to_json_file(txt_file_path + course + ".json", bank_a_paper)


def sel_main_auto_submit(driver):

    reg_courses = sel_parse_courses(driver)  # 查找已经报名的科目
    print("已经报名的科目有：")
    print(reg_courses)
    Account.account_update_stud_courses_to_db(reg_courses)  # 更新每个科目的情况

    for reg_course in reg_courses:
        print(reg_course)
        task_papers_mode = DOING_TASK["papers"].__str__()
        list_task_papers_mode = task_papers_mode.split(",")
        if DOING_TASK["test_subject"] == reg_course["short_title"]:
            driver.get(reg_course["href"])  # 进入科目
            if DOING_TASK["test_subject"] == "安全与生活":
                sel_parse_course_asse_type(driver, label="学习内容")
                sel_click_not_com_exam(driver, reg_course["data-course-id"])  # 进入没有考试的科目
                print("[sel_main_auto_submit] 学习内容 完成")
                if "学习内容" in list_task_papers_mode:
                    print("[sel_main] 只是做 学习内容 完成")
                    break

        if DOING_TASK["test_subject"] == reg_course["short_title"]:
            driver.get(reg_course["href"])  # 进入科目
            sel_parse_course_asse_type(driver)  # 进入 形成性考核
            sel_click_not_com_exam(driver, reg_course["data-course-id"])  # 进入没有考试的科目
            print("[sel_main] task 完成")
            print(DOING_TASK)
            break
    print("[sel_main_auto_submit] OUT")


def sel_main():

    debug = 0
    if debug == 1:
        print("IN")
        Account.account_updata_excel_task2json()
        task = _sel_updata_doing_task()  # 获取当前的task
        driver = _sel_open_local_driver(
            "file:///H:/Share/Project/Source/debugWeb/%E5%AE%89%E5%85%A8%E4%B8%8E%E7%94%9F%E6%B4%BB%EF%BC%88%E4%B8%9322%E6%98%A5%EF%BC%89_%20%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%BD%A2%E6%88%90%E6%80%A7%E8%80%83%E6%A0%B8%EF%BC%8820%E5%88%86%EF%BC%89.html"
        )
        sel_click_not_com_exam(driver)
        #sel_parse_paper(driver)  # 提交答案后 ，获取正确答案
        time.sleep(10000)
        driver.quit()
        return

    Account.account_updata_excel_task2json()
    list_tasks = Account.account_read_json_task()
    task = _sel_updata_doing_task()  # 获取当前的task
    if not task:
        print("[sel_main] end")
    else:
        for item in list_tasks:
            driver = sel_open_selrion()
            sel_login(driver)  # 登录
            sel_main_auto_submit(driver)
            time.sleep(1)
            driver.quit()

            task = _sel_updata_doing_task()  # 获取当前的task
            if not task:
                print("[sel_main] end")
                break


    print("main hold")

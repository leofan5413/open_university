import sys
import time
import os
import copy
import hashlib
import re
import json
from zhon.hanzi import punctuation
import FuncPrint
import JsonFile
import Account
import Docr
import ParseTxt
from selenium import webdriver


# 功能: 创建一个Google浏览器
# 返回值： driver ,返回Google driver handle
def sel_open_selrion():
    FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    USER_AGENT = "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.32"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(USER_AGENT)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    FuncPrint._func_out_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    return driver


# 功能： 关闭Google 浏览器
# 输入： driver, google 句柄
def sel_close_selrion(driver):
    FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    driver.quit()
    FuncPrint._func_out_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)


COOKIES_NAME = "cookies.json"
# 读取账号 密码
def sel_read_cookies():
    dict_cookies = JsonFile.js_file_to_dict(COOKIES_NAME)
    return dict_cookies["cookies"]


# 向json 文件写入新的cookies
def sel_write_cookies(cookies_new):
    dict_cookies = {"cookies": []}
    for item in cookies_new:
        dict_cookies["cookies"].append({"value": item["value"], "name": item["name"]})
    JsonFile.js_dict_to_file(COOKIES_NAME, dict_cookies)

HOME_URL = ""
RELOGIN_URL = ""
def sel_login(driver, user_name, account, password):
    FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)

    if HOME_URL.len == 0:
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "请设置 HOME_URL")
        return
    if RELOGIN_URL.len == 0:
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "请设置 RELOGIN_URL")
        return

    # 登录主页
    enter_url = HOME_URL
    driver.get(enter_url)
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          "打开" + HOME_URL)

    # 设置cookie
    cookies = sel_read_cookies()
    for cookie in cookies:
        print(cookie)
        driver.add_cookie(cookie_dict=cookie)
    # time.sleep(100)
    enter_url = RELOGIN_URL
    driver.get(enter_url)
    time.sleep(2)
    try:
        user_text = driver.find_element_by_class_name("left_name")
        if user_text.text == user_name:
            print(user_name)
            print("cookies 有效")
        else:
            print("json 文件的姓名:" + user_name)
            print("cookies 失效")
            driver.delete_all_cookies()
            # sel_login_new_account(driver)
    except:
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "cookies 不正常, 失效,需要重新登录")
        driver.delete_all_cookies()
        sel_login_new_account(driver, user_name, account, password)
    FuncPrint._func_out_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)


# 判断是没有登录，就重新登录
def sel_login_new_account(driver, user_name, account, password):
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          "进行重新登录")
    # 登录地址
    url = RELOGIN_URL
    driver.get(url)

    # 请输入登录名字
    element = driver.find_element_by_id("loginName")
    element.send_keys(account)

    # 密码
    pws = driver.find_element_by_id("password")
    pws.send_keys(password)

    # kaptchaImage
    kaptchaImage = driver.find_element_by_id("kaptchaImage")
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          kaptchaImage.get_attribute("src"))
    img_bytes = kaptchaImage.screenshot_as_png
    with open("kaptchaImage.png", 'wb') as f:
        f.write(img_bytes)
    res = Docr.docr_decoder("kaptchaImage.png")
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          res)

    # validateCode
    validateCode = driver.find_element_by_id("validateCode")
    validateCode.send_keys(res)

    # 登录
    button = driver.find_element_by_class_name("bu_c")
    button.click()

    # 获取 cookie
    cookies_new = driver.get_cookies()
    sel_write_cookies(cookies_new)
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          user_name + "成功登录！")
    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          cookies_new)

def sel_select_course(driver):
    courses = []
    for index in range(1, 20):
        time.sleep(3)
        courses = driver.find_elements_by_class_name("ouchnPc_index_course_div")
        if len(courses) > 0:
            break
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "等科目刷出")

    for course in courses:
        tag = course.find_element_by_tag_name("p")
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          "报考科目: " + tag.text)
        if tag.text.strip() == "形势与政策":
            href = course.find_element_by_tag_name("a").get_attribute("href")
            print(href)
            driver.get(href)
            time.sleep(1)
            break


def sel_collect_completeness(driver, user_name):
    time.sleep(3)
    for index in range(1, 60):
        collapsed = driver.find_elements_by_class_name("expand-collapse-all-button")
        if len(collapsed) > 0:
            time.sleep(2)
            try:
                collapsed[0].click()
            except:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "点击expend 按钮失败，继续")
                continue
            break
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "等expend按钮刷出")
        time.sleep(3)

    for index in range(1, 60):
        activity_summaries = driver.find_elements_by_class_name("activity-summary.ng-scope")
        if len(activity_summaries) > 0:
            time.sleep(3)
            break
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "等待科目刷出")
        time.sleep(3)

    list_video_text = []
    list_exam_text = []
    for activity_summary in activity_summaries:
        ng_switch_when = activity_summary.get_attribute("ng-switch-when")
        if ng_switch_when == "online_video":
            title = activity_summary.find_element_by_class_name("activity-title")
            title_short = title.find_element_by_class_name("title.ng-binding.ng-scope")
            list_video_text.append(title_short.text.strip())
        elif ng_switch_when == "exam":
            title = activity_summary.find_element_by_class_name("activity-title")
            title_short = title.find_element_by_class_name("title.ng-binding")
            list_exam_text.append(title_short.text.strip())

    # 视频
    for activity_summary in activity_summaries:
        ng_switch_when = activity_summary.get_attribute("ng-switch-when")
        if ng_switch_when == "online_video":
            title = activity_summary.find_element_by_class_name("activity-title")
            title_short = title.find_element_by_class_name("title.ng-binding.ng-scope")
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "video: " + title_short.text)

            # completeness part or  completeness none
            completeness = activity_summary.find_element_by_class_name("completeness")
            status = completeness.get_attribute("tipsy-literal").strip()
            if status.find("部分完成") >= 0 or status.find("未完成") >= 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      status)
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      title_short.text)
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "未完成")
                activity_summary.click()
                sel_play_video(driver=driver, list_video_text=list_video_text, user_name=user_name)
                break

    # 考试
    for activity_summary in activity_summaries:
        ng_switch_when = activity_summary.get_attribute("ng-switch-when")
        if ng_switch_when == "exam":
            title = activity_summary.find_element_by_class_name("activity-title")
            title_short = title.find_element_by_class_name("title.ng-binding")
            score_port = ""
            try:
                score = activity_summary.find_element_by_class_name("score.ng-scope")
                score_port = score.text.strip()
            except:
                nothing = 0
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "exam: " + title_short.text  + " " + score_port)
            # completeness part or  completeness none
            completeness = activity_summary.find_element_by_class_name("completeness")
            status = completeness.get_attribute("tipsy-literal").strip()
            if status.find("部分完成") >= 0 or status.find("未完成") >= 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      title_short.text)
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "未完成/部分完成")
                activity_summary.click()
                sel_start_exam(driver=driver, list_exam_text=list_exam_text, user_name=user_name)
                break

# 开始考试
def sel_start_exam(driver, list_exam_text=[], user_name=""):
    for i in range(1, 600):
        time.sleep(5)
        for item in range(1, 600):
            time.sleep(3)
            start_btn = driver.find_elements_by_class_name("button.button-green.take-exam")
            if len(start_btn) > 0:
                try:
                    start_btn[0].click()
                    break
                except:
                    continue

        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                          "勾选同意书")

        time.sleep(3)
        try:
            pop_dlg = driver.find_element_by_class_name("reveal-modal.popup-area.confirmation-popup.popup-600.ng-scope.open")
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  pop_dlg.get_attribute("style"))

            if pop_dlg.get_attribute("style").find("display: block;") >= 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "display: block")
                checkbox = driver.find_element_by_xpath("/html/body/div[11]/div/div/div[2]/div[2]/input")
                checkbox.click()
                btn_c = driver.find_element_by_xpath("/html/body/div[11]/div/div/div[3]/div/button[1]")
                btn_c.click()
        except:
            FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "勾选出错")

        FuncPrint._func_out_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        sel_parse_paper(driver, list_exam_text)



# 读取选择题题目，并且选择正确答案
def sel_parse_paper(driver, list_exam_text=[]):
    # 获取题目的数量
    for item in range(1, 300):
        single_selections = driver.find_elements_by_class_name("subject.ng-scope.single_selection")
        print("题目的总数为：" + len(single_selections).__str__())
        if len(single_selections) > 0:
            break
        time.sleep(3)

    true_or_falses = driver.find_elements_by_class_name("subject.ng-scope.true_or_false")
    for i in true_or_falses:
        single_selections.append(i)

    if len(single_selections) < 0:
        FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "没有选择题")
        return

    for index, single_selection in enumerate(single_selections):
        stem = single_selection.find_element_by_tag_name("p")
        print("题目" + index.__str__() + ":" + stem.text)
        correct_answers = sel_get_answer(stem.text)
        print("正确答案：" + correct_answers.__str__())
        try:
            subject_options = single_selection.find_element_by_class_name("subject-options")
            answerd_options = subject_options.find_elements_by_tag_name("label")
        except:
            print("没有 answer 选项")

        for index, answerd_option in enumerate(answerd_options):
            option_content = answerd_option.find_element_by_class_name("option-content")
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  index.__str__() + " :" + option_content.text.strip())
            for answer in correct_answers:
                if option_content.text.strip().find(answer) >= 0:
                    option_content.click()

    print("答题完成")


# 从题库中获取正确答案
def sel_get_answer(stem):
    main_file_path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
    txt_file_path = main_file_path + "\SelQuestionBank\/"
    course = "形势与政策"

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
    return correct_answer


# 获取试卷的正确答案并且存入题库
def sel_parse_correct_answer(driver):
    bank_a_paper = []
    for item in range(1, 300):
        single_selections = driver.find_elements_by_class_name("subject.ng-scope.single_selection")
        print("题目的总数为：" + len(single_selections).__str__())
        if len(single_selections) > 0:
            break
        time.sleep(3)

    true_or_falses = driver.find_elements_by_class_name("subject.ng-scope.true_or_false")
    for i in true_or_falses:
        single_selections.append(i)

    if len(single_selections) < 0:
        FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "没有选择题")
        return

    for index, single_selection in enumerate(single_selections):
        bank_a_topic = [index]
        bank_options = []
        bank_correct_options = []
        stem = single_selection.find_element_by_tag_name("p")
        print("题目" + index.__str__() + ":" + stem.text)
        bank_a_topic.append(stem.text.strip())
        try:
            subject_options = single_selection.find_element_by_class_name("subject-options")
            answerd_options = subject_options.find_elements_by_tag_name("label")
        except:
            print("没有 answer 选项")

        for index, answerd_option in enumerate(answerd_options):
            option_content = answerd_option.find_element_by_class_name("option-content")
            option_check = answerd_option.find_element_by_tag_name("input")
            checked = option_check.get_attribute("checked")
            print(checked)
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  index.__str__() + " :" + option_content.text.strip())

            bank_options.append(option_content.text.strip())  # 填入选项
            if checked is not None:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      index.__str__() + checked + " :" + option_content.text.strip())
                bank_correct_options.append(option_content.text.strip())  # 填入正确答案
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
    course = "形势与政策"
    ParseTxt.parse_list_to_json_file(txt_file_path + course + ".json", bank_a_paper)

#  判断当前是否是考试
def sel_is_exam_task(driver, list_video_text):
        FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        current_title= []
        for index in range(1, 20):
            time.sleep(3)
            current_title = driver.find_elements_by_class_name("exam-title.truncate-text.left")
            if len(current_title) > 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      current_title[0].text)
                break

        if len(current_title) <= 0:
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "没有找到 exam-title truncate-text left 这个标题")
            return 1

        for item in list_video_text:
            if current_title[0].text.find(item) >= 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "Match:" + item)
                return 0
        return 1


def sel_play_video(driver, list_video_text=[], user_name=""):
    for item in range(1, 600):
        time.sleep(3)
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              user_name)
        try:
            pop_dlg = driver.find_element_by_class_name("reveal-modal-bg")
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  pop_dlg.get_attribute("style"))

            if pop_dlg.get_attribute("style") == "display: block;":
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "display: block")
                btn_c = driver.find_element_by_xpath("/html/body/div[11]/div/div[3]/div/button")
                btn_c.click()
        except:
            nothing = 1

        if 0 == sel_is_video_task(driver, list_video_text):
            sel_start_player(driver)
        elif 1 == sel_is_video_task(driver, list_video_text):
            ret = sel_next_item(driver)
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                 "[" + user_name + "]" + "当前不是视频")
            if ret == -1:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "[" + user_name + "]" + "没有下一项")
                break
            else:
                continue
        else:
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "全部视频题目已经做完，没有找到下一个")
            return

        for index in range(1, 60 * 10 * 3):
            time.sleep(6)
            try:
                pop_dlg = driver.find_element_by_class_name("reveal-modal-bg")
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      pop_dlg.get_attribute("style"))

                if pop_dlg.get_attribute("style") == "display: block;":
                    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                          "display: block")
                    btn_c = driver.find_element_by_xpath("/html/body/div[11]/div/div[3]/div/button")
                    btn_c.click()
            except:
                nothing = 0

            try:
                pleyer = driver.find_element_by_class_name("child-player.first")
                pleyer.click()  #点击一下视频框，这样才会显示进度条
                time.sleep(1)
            except:
                FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "没有找到视频")
                continue

            try:
                mvp_time = driver.find_element_by_class_name("mvp-time-display")
                time_texts = mvp_time.text.split("/")
                for index, item in enumerate(time_texts):
                    time_texts[index] = item.strip()
                FuncPrint._func_logi_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "[" + user_name + "]" + str(time_texts), "\n")
            except:
                FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "没有找到进度条时间")
            if len(time_texts) > 1:
                # 播放下一个视频
                if time_texts[0].strip() == time_texts[1].strip():
                    time.sleep(1)
                    sel_next_item(driver)
                    break
                else:
                    stop_btns = driver.find_elements_by_class_name("mvp-fonts.mvp-fonts-play")
                    for stop_btn in stop_btns:
                        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                              "发现暂停")
                        try:
                            stop_btn.click()
                            break
                        except:
                            break


#  判断当前是否是视频
def sel_is_video_task(driver, list_video_text):
        FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        current_title= []
        for index in range(1, 20):
            time.sleep(3)
            current_title = driver.find_elements_by_class_name("title.ng-binding")
            if len(current_title) > 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      current_title[0].text)
                break

        if len(current_title) <= 0:
            FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                  "没有找到 title.ng-binding 这个标题")
            return 1

        for item in list_video_text:
            if current_title[0].text.find(item) >= 0:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      "Match:" + item)
                return 0
        return 1


def sel_start_player(driver):
    for index in range(1, 20):
        play_button = driver.find_elements_by_class_name("mvp-fonts.mvp-fonts-play")
        if len(play_button) > 0:
            # 点击播放
            try:
                play_button[0].click()
            except:
                print("click play fail")
                continue

            # 点击二倍速
            try:
                rate_btn = driver.find_element_by_class_name("mvp-play-rate-btn")
                rate_btn.click()
            except:
                print("click rate fail")
                continue
            rates = driver.find_elements_by_class_name("mvp-play-rate")
            for rate in rates:
                FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                      rate.text)
                if rate.text.strip() == "2.0X":
                    FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                          "打开 2X  播放")
                    try:
                        rate.click()
                    except:
                        break
                    break
            break  # 视频已经播放，不用重复
        FuncPrint._func_logd_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "等待视频")
        time.sleep(2)


# 进入下一个,并且返回是否为 视频任务
def sel_next_item(driver):
    try:
        time.sleep(5)
        next_item = driver.find_element_by_class_name("next.ng-binding.ng-scope")
        next_item.click()
        time.sleep(5)
        return 0
    except:
        FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "没有找到下一个")
        return -1

def main():
    FuncPrint._func_in_(sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    # Account.account_updata_excel_task2json()
    DEBUG = 0
    if DEBUG == 1:
        driver = sel_open_selrion()
        sel_login(driver, user_name="xieyifeng",
                  account="2090106461644",
                  password="Ouchn@2021")
        sel_select_course(driver)
        sel_collect_completeness(driver=driver, user_name="xieyif")
        sel_close_selrion(driver)
        return
    elif DEBUG == 2:
        driver = sel_open_selrion()
        enter_url = "test.html"
        driver.get(enter_url)
        sel_parse_correct_answer(driver)
        time.sleep(10000)
        sel_close_selrion(driver)

    doing_task = Account.account_update_json_next_task()
    driver = sel_open_selrion()
    sel_login(driver, user_name=doing_task["student_name"],
                      account=doing_task["student_number"],
                      password=doing_task["password"])
    sel_select_course(driver)
    sel_collect_completeness(driver=driver, user_name=doing_task["student_name"])
    sel_close_selrion(driver)

main()
import os
import copy
import json

topic_neuron = [["课程测验", "题干"],
                ["？", "【单项选择】", "单选 "],
                ["选择一项", "多项"],
                ["a. ", "A. ", "a.", "A、 ", "A. ", "A.", "a. ", "对", "错"]]

options_neuron = [["a. ", "b. ", "c. ", "d. ",
                   "A. ", "B. ", "C. ", "D. ",
                   "a. ", "b. ", "c. ", "d. ",
                   "a.", "b.", "c.", "d.",
                   "A、 ", "B、 ", "C、 ", "D、 ",
                   "A. ", "B. ", "C. ", "D. ",
                   "A.", "B.", "C.", "D.",
                   "e. ", "f. "],
                  ["对", "错"]]
correct_option_neuron = [["反馈"], ["正确的答案是", "正确答案是：", "正确答案为: ", "参考答案：", "正确答案是：", "参考答案："]]

# 打开一个 json 文件， 直接转化成列表
def parse_json_file_to_list(source_file):
    try:
        fi_json = open(source_file, 'r', encoding='utf-8')
        content = fi_json.read()
        json_list = json.loads(content)
        fi_json.close()
        return json_list
    except:
        print('没有这个文件: ' + source_file)
        return []


def parse_list_to_json_file(source_file, source_list):
    old_json_list = parse_json_file_to_list(source_file)

    pop_list = []
    for index, a_topic in enumerate(source_list):   # 查找新题库中的重复 的题目
        for o_index, o_a_topic in enumerate(old_json_list):
            if a_topic[0] == o_a_topic[0]:
                pop_list.append(index)
                break
    offset = 0
    for pop in pop_list:
        source_list.pop(pop - offset)  # 移除重复的题目
        offset += 1

    print("新增 " + len(source_list).__str__() + " 条题目到题库中")

    for index, a_topic in enumerate(source_list):   # 查找新题库中的重复 的题目
        old_json_list.append(a_topic)

    j_dump = json.dumps(old_json_list, ensure_ascii=False, indent=2)
    fo_json = open(source_file, 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()
    print('文件已经保存: ' + source_file)


# 打开一个 txt 文件， 通过算法解析出 题目，正确答案 和 相关选项
# source_file : 源文件。
# test_paper ： 函数返回值，列表类型 ，记录全部解析处来的题目
def parse_txt_file_to_list(source_file):
    try:
        fo = open(source_file, 'r', encoding='utf-8')
        lines = fo.readlines()
        fo.close()
    except:
        print("没有题库" + source_file)
        return []

    test_paper = []
    a_topic = []
    options_for_a_topic = []
    correct_options_for_a_topic = []
    multiple_score = 0
    for index, line in enumerate(lines):
        if 0 < index < len(lines) - 2:
            topic_score = 0
            for match in topic_neuron[0]:
                if lines[index-1].find(match) >= 0:
                    topic_score += 1
            for match in topic_neuron[1]:
                if lines[index].find(match) >= 0:
                    topic_score += 1

            for match in topic_neuron[1]:   # 如果找到
                if lines[index].find(match) >= 0:
                    topic_score += 1
                    for match_2 in topic_neuron[3]:
                        if lines[index + 1].find(match) >= 0:
                            topic_score += 1

            for match in topic_neuron[2]:
                if lines[index+1].find(match) >= 0:
                    topic_score += 1
                    multiple_score += 1
            for match in topic_neuron[3]:
                if lines[index+2].find(match) >= 0:
                    topic_score += 1

            # 判断为题目
            if topic_score >= 2:
                # 清除旧数据
                if correct_options_for_a_topic is not None and len(correct_options_for_a_topic) > 0:
                    a_topic.append(copy.deepcopy(correct_options_for_a_topic))
                    correct_options_for_a_topic.clear()
                if options_for_a_topic is not None and len(options_for_a_topic) > 0:
                    a_topic.append(copy.deepcopy(options_for_a_topic))
                    options_for_a_topic.clear()
                if a_topic is not None and len(a_topic) > 0:
                    test_paper.append(copy.deepcopy(a_topic))
                    a_topic.clear()

                # print("[识别的题目是]" + line.strip())
                a_topic.append(index)
                a_topic.append(line.strip())

            options_score = 0
            judgment_source = 0
            options_match_len = 0
            for match in options_neuron[0]:
                if lines[index-1].find(match) == 0:
                    options_score += 1
                    break
            for match in options_neuron[0]:
                if lines[index].find(match) == 0:
                    options_score += 2
                    options_match_len = len(match)
                    break
            for match in options_neuron[0]:
                if lines[index+1].find(match) == 0:
                    options_score += 1
                    break

            for match in options_neuron[1]:
                if lines[index - 1].find(match) == 0:
                    options_score += 1
                if lines[index].find(match) == 0:
                    options_score += 2
                    judgment_source += 1
                    options_match_len = len(match)
                if lines[index + 1].find(match) == 0:
                    options_score += 1

            #判断为题目选项
            # print(line.strip()  + "  score:" +options_score.__str__() + "match len:" + options_match_len.__str__())
            if options_score >= 3:
                # print(line[options_match_len - 1:].strip())
                if options_match_len > 1: #如果 出现对 错 选项，就不需要过来开头的字了
                    options_for_a_topic.append(line[options_match_len:].strip())
                else:
                    options_for_a_topic.append(line.strip())

            correct_options_score = 0
            correct_options_match_len = 0
            for match in correct_option_neuron[0]:
                if lines[index - 1].find(match) >= 0:
                    correct_options_score += 1
            for match in correct_option_neuron[1]:
                if lines[index].find(match) >= 0:
                    correct_options_score += 2
                    correct_options_match_len = len(match)

            #判断为正确答案
            #print(a_topic)
            #print(line  + " correct_options_score:" + correct_options_score.__str__() + " multiple_score:" + multiple_score.__str__())
            if correct_options_score >= 2:
                line = line[correct_options_match_len:].strip()
                # 多选题的正确答案 1:单选题 或判断题   2： 多选题
                if multiple_score >= 2:
                    correct_options_for_a_topic = line.split(", ")
                    #print(correct_options_for_a_topic)
                else:
                    option = []
                    for match in options_for_a_topic:
                        if line.strip().find(match) >= 0:
                            option.append(match)
                    # 获取最长的的选项作为最终答案
                    # 避免选到类似答案，列如： 'remove' 误选为 'move'
                    if len(option) <= 0:
                        option.append(match)
                    option_match = max(option, key=len, default='')
                    correct_options_for_a_topic.append(copy.deepcopy(option_match))

                #multiple_score 多项选择的标志， 用完清0
                multiple_score = 0
                # print("正确答案 :" + correct_options_for_a_topic.__str__())

                # 如果找到了正确答案，需要及时写入，以免后面找不到题目
                # 清除旧数据
                if correct_options_for_a_topic is not None and len(correct_options_for_a_topic) > 0:
                    a_topic.append(copy.deepcopy(correct_options_for_a_topic))
                    correct_options_for_a_topic.clear()
                if options_for_a_topic is not None and len(options_for_a_topic) > 0:
                    a_topic.append(copy.deepcopy(options_for_a_topic))
                    options_for_a_topic.clear()
                if a_topic is not None and len(a_topic) > 0:
                    test_paper.append(copy.deepcopy(a_topic))
                    a_topic.clear()

    return test_paper

# source_file: txt 的数据元
# output_file : 解析完后，输出的文件
# output_warning_file : 解析完之后，产生的错误数据
def parse_txt_file_to_txt(source_file, output_file, output_warning_file):
    # 解析txt 文件， 生产一个列表
    test_paper = parse_txt_file_to_list(source_file)

    #  删除旧数据
    if os.path.exists(output_file):
        os.remove(output_file)

    if os.path.exists(output_warning_file):
        os.remove(output_warning_file)

    f_o = open(output_file, 'w', encoding='utf-8')
    f_json = open(output_file + "json", 'w', encoding='utf-8')
    f_wo = open(output_warning_file, 'w', encoding='utf-8')

    # error_index 用于记录题目 不完整的，用于删除
    error_index = []
    error_count = 0
    total_count = 0
    for index, topic in enumerate(test_paper):
        total_count += 1
        if len(topic) < 4:
            f_wo.write(topic.__str__() + "\n")
            error_index.append(index)
            error_count += 1

    # 删除 test_paper 里面不符合规则的题目
    error_offset = 0
    for index in error_index:
        test_paper.pop(index - error_offset)
        error_offset += 1

    for index, topic in enumerate(test_paper):
        f_json.write(topic.__str__() + "\n")

    # 重新写一个标准的 txt
    option_head = ["a. ", "b. ", "c. ", "d. ", "e. ", "f. "]
    for index, topic in enumerate(test_paper):
        if len(topic) >= 4:
            f_o.write("题干" + "\n")
            f_o.write(topic[1] + "\n")
            f_o.write("选择一项")
            if len(topic[2]) > 1:
                f_o.write("或者多项")
            f_o.write("\n")

            for i_index, item in enumerate(topic[3]):
                if i_index < len(option_head):
                    f_o.write(option_head[i_index] + item + "\n")

            f_o.write("正确答案是：")
            for c_index, c_item in enumerate(topic[2]):
                if c_index >= 1:
                    f_o.write(", ")
                f_o.write(c_item)

        f_o.write("\n")
        f_o.write("\n")

    f_o.close()
    f_json.close()
    f_wo.close()
    print(source_file + " error_count: " + error_count.__str__() + "  total:" + total_count.__str__())


def parse_txts_file_to_txts(path, output_path):
    file_name_list = os.listdir(path)
    for index, i in enumerate(file_name_list):
        if i.endswith('.txt') and not i.startswith('~$'):
            name_ex = i
            name = name_ex.split(".", 1)[0]
            ex = name_ex.split(".", 1)[1]
            path_name_ex = path + name_ex
            out_path_name_ex = output_path + name + ".txt"
            out_warning_path_name_ex = output_path + "\warning\/" + name + ".txt"
            if os.path.exists(out_path_name_ex):
                os.remove(out_path_name_ex)

            if os.path.exists(out_warning_path_name_ex):
                os.remove(out_warning_path_name_ex)

            # print("path name ex: " + path_name_ex)
            # print("out path name ex:" + out_path_name_ex)
            # print("out waring path name ex:" + out_warning_path_name_ex)
            parse_txt_file_to_txt(path_name_ex, out_path_name_ex, out_warning_path_name_ex)

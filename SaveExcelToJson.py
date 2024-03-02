import os
import copy
import json
from openpyxl import load_workbook


def setj_save_stud_account_db(list_row):
    list_row.pop(0)
    pop_list = []
    for index, item in enumerate(list_row[1:]):
        if list_row[index][0] == list_row[index + 1][0]:
            pop_list.append(index + 1)

    offset = 0
    for pop in pop_list:
        list_row.pop(pop - offset)
        offset += 1

    stud_account_db = {}
    for item in list_row:
        stud_dict = {
            "password": item[3],
            "student_name": item[1],
            "student_number": item[0]
        }
        stud_account_db[stud_dict["student_number"]] = stud_dict

    j_dump = json.dumps(stud_account_db, ensure_ascii=False, indent=2)
    fo_json = open("stud_account_db.json", 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()


def setj_parse_excel(file_name):
    print(file_name)
    work_boot = load_workbook(file_name)
    # getthefirsesheet
    for work_sheet in work_boot._sheets:
        print("sheetname:" + work_sheet.title)
        list_row = []
        for row in work_sheet.rows:
            list_cell = []
            for cell in row:
                list_cell.append(cell.value)
            list_row.append(copy.deepcopy(list_cell))
            list_cell.clear()

        return list_row


def setj_main():
    print("In setj_main")
    file_path = os.path.abspath(os.path.dirname(__file__) + os.path.sep)
    excel_file_path = file_path + "\Excel"
    excel_file_name = excel_file_path + "\作业.xlsx"
    list = setj_parse_excel(excel_file_name)
    setj_save_stud_account_db(list)




import sys
import json
import FuncPrint

def js_file_to_dict(js_file_name):
    try:
        fi_json = open(js_file_name, 'r', encoding='utf-8')
        content = fi_json.read()
        dict = json.loads(content)
        fi_json.close()
        return dict
    except:
        FuncPrint._func_loge_(sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                              "No found " + js_file_name)
        return {}


def js_dict_to_file(js_file_name, dict):
    j_dump = json.dumps(dict, ensure_ascii=False, indent=2)
    fo_json = open(js_file_name, 'w', encoding='utf-8')
    fo_json.write(j_dump)
    fo_json.close()


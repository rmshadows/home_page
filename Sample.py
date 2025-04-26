#!/usr/bin/python3

import json
import sys


def loadConfJSON(filepath):
    json_dict = {}
    with open(filepath, 'r', encoding="utf-8") as f:
        json_dict = json.load(f)
    print("加载配置文件 {} ： {}".format(filepath, json_dict))
    return json_dict


def initJSON(module):
    """
    生成json配置文件
    :param module_path: 模型文件名称(不包含扩展名)
    """
    # 临时字典
    tmp = {}
    # 临时列表字典
    tmp_list_dict = {}
    # 临时列表字典名称
    tmp_list_name = ""

    with open(module+".html", 'r', encoding="utf-8") as m:
        # 是否是列表项
        ListFlag = False
        for line in m.readlines():
            if "{^START^}" in line:
                # 清空临时列表字典
                tmp_list_dict = {}
                tmp_list_name = ""
                ListFlag = True
            elif "{^END^}" in line:
                tmp[tmp_list_name] = [tmp_list_dict]
                ListFlag = False
            else:
                pass
            # 有参数
            t_p = line.split(">}")
            # 可能一行多个参数
            for i in t_p:
                # 有参数才执行
                if "{<" in i:
                    b = i.index("{<") + 2
                    param_path = i[b:]
                    # 获取注释
                    if "#" in param_path:
                        comment = param_path.split("#")[1]
                        param_path = param_path.split("#")[0]
                    else:
                        comment = ""
                    if "." in param_path:
                        # 最多仅支持二级目录
                        param_path = param_path.split(".")
                        if len(param_path) != 2:
                            sys.exit("最多仅支持两级")
                        # 处理字典
                        if not ListFlag:
                            # 普通赋值
                            if param_path[0] not in tmp.keys():
                                tmp[param_path[0]] = {param_path[1]: comment}
                            else:
                                tmp[param_path[0]][param_path[1]] = comment
                        else:
                            tmp_list_name = param_path[0]
                            tmp_list_dict[param_path[1]] = comment
                    else:
                        tmp[param_path] = comment
    # print(str(tmp).replace("\'", "\""))
    tmp = str(tmp).replace("\'", "\"")
    params = json.loads(tmp)
    print(params)
    with open("{}.conf".format(module), "w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False, indent=4)


def getPage(sample_html, json_conf):
    """
    生成页面
    :return:
    """
    # 最终页面
    page_lines = []
    # 临时行
    tmp_line = ""
    # 临时列表重复段落
    tmp_par = []
    # 要删除的字段
    full_del = ""

    with open(sample_html+".html", "r", encoding="utf-8") as f:
        # 是否是列表项
        list_flag = False
        for line in f.readlines():
            tmp_line = ""
            # 字段名
            tmp_p = ""
            line = line.replace("\r\n", "").replace("\n", "")
            # print(line)
            if "{^START^}" in line:
                # 清空临时列表
                tmp_par = []
                list_flag = True
                continue
            elif "{^END^}" in line:
                # 获取字段
                for j in tmp_par:
                    if "{<" in j:
                        b = j.index("{<")+2
                        e = j.index(">}")
                        # print(j[b:e])
                        tmp_p = j[b:e].split(".")[0]
                # 获取json 每个json
                for j in json_conf[tmp_p]:
                    # 每个循环段
                    for line in tmp_par:
                        tmp_line = ""
                        # 循环处理
                        t_p = line.split(">}")
                        # 可能一行多个参数
                        for e in t_p:
                            # 有参数才执行
                            if "{<" in e:
                                tmp_line += e
                                b = e.index("{<") + 2
                                param_path = e[b:]
                                # 获取字段全名
                                full_del = "{{<{0}".format(param_path)
                                # print(full_del)
                                # 去掉注释
                                if "#" in param_path:
                                    param_path = param_path.split("#")[0]
                                param_path = param_path.split(".", 1)[1]
                                # print(param_path)
                                if "." in param_path:
                                    sys.exit("多余的参数？")
                                tmp_line = tmp_line.replace(full_del, j[param_path])
                            else:
                                # 一行多参数
                                tmp_line += e
                        # print(tmp_line)
                        page_lines.append(tmp_line)
                list_flag = False
                continue
            else:
                if list_flag:
                    # 添加重复段落待处理
                    tmp_par.append(line)
                else:
                    # 有参数
                    t_p = line.split(">}")
                    # 可能一行多个参数
                    for i in t_p:
                        # 有参数才执行
                        if "{<" in i:
                            tmp_line += i
                            b = i.index("{<") + 2
                            param_path = i[b:]
                            # 获取字段全名
                            full_del = "{{<{0}".format(param_path)
                            # print(full_del)
                            if "#" in param_path:
                                param_path = param_path.split("#")[0]
                            if "." in param_path:
                                # 最多仅支持二级目录
                                param_path = param_path.split(".")
                                if len(param_path) != 2:
                                    sys.exit("最多仅支持两级")
                                # 处理字典
                                if not list_flag:
                                    # 普通赋值
                                    # 替换full_del为目标
                                    tmp_line = tmp_line.replace(full_del, json_conf[param_path[0]][param_path[1]])
                                else:
                                    tmp_par.append(line)
                            else:
                                # 替换full_del为目标
                                tmp_line = tmp_line.replace(full_del, json_conf[param_path])
                        else:
                            tmp_line += i
            if not list_flag:
                page_lines.append(tmp_line)
    # for i in page_lines:
    #     print(i)
    return page_lines


if __name__ == '__main__':
    # 生成初始化配置文件
    # initJSON("sample")

    home_page_conf = loadConfJSON("index.conf")
    page_html = getPage("sample", home_page_conf)
    with open("index.html", "w", encoding="utf-8") as f:
        for i in page_html:
            f.write("{}\n".format(i))

#该文件定义和实现了一些通用的系统函数

import os

def pardir(path):#返回指定目录的父目录,默认返回当前目录的父目录
    return os.path.abspath(os.path.join(path,".."))

def match(str):#检查字符串的括号是否合法
    s=[]
    for i in range(len(str)):
        if(str[i]=='('):
            s.append('(')
        elif(str[i]==')'):
            if(len(s)==0):
                return False
            s.pop()
    return (len(s)==0)
            
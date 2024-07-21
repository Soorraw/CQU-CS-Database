#该文件定义和实现数据库和关系模式的删除

import os
import shutil
import re
from System import pardir

def excute(root,path,sql):
    mat=re.match("[a-z]+ ?",sql)#匹配"Drop"关键词后的第一个英文单词
    if(mat):
        key=mat.group()
        sql=sql.replace(key,"")
        if(key=="database "):#如果是"Database",则删除数据库
            if(path==root):
                dropDB(path,sql)
            else:
                print("Drop Error:Exit the current database first.")
        elif(key=="table "):#如果是"Table",则创建关系模式
            if(pardir(path)==root):    
                dropTB(path,sql)
            else:print("Drop Error:Table could only be dropped under database!")
        else:print('Syntax Error:Keyword "'+key+'"after "Drop" out of SQL criteria,try "Database" or "Table".')
    else:
        print('Syntax Error:Invalid expression after "Drop".')

def dropDB(path,db_name):
    db_name=db_name.replace(" ","")
    target=os.path.join(path,db_name)
    if(os.path.exists(target)):#数据库存在
        shutil.rmtree(target)
        print('Database "'+db_name+'" has been removed.')
    else:print('Database "'+db_name+'" does not exist.')

def dropTB(path,tb_name):
    tb_name=tb_name.replace(" ","")
    target=os.path.join(path,tb_name)
    if(os.path.exists(target)):#关系模式存在
        shutil.rmtree(target)
        print('Table "'+tb_name+'" has been removed.')
    else:print('Table "'+tb_name+'" does not exist.')
        
#该文件定义和实现数据库和关系模式的创建

import re
import os
import pandas as pd
import numpy as np
from System import pardir,match
from BPlusTree import BPlusTree as BPT

def excute(root,path,capacity,sql):
    mat=re.match("[a-z]+ ",sql)#匹配"Create"关键词后的第一个英文单词
    if(mat):
        key=mat.group()
        sql=sql.replace(key,"")
        if(key=="database "):#如果是"Database",则创建数据库
            if(path==root):
                return createDB(path,sql)
            else:
                print("Create Error:Already in database!")
        elif(key=="table "):#如果是"Table",则创建关系模式
            if(pardir(path)==root):    
                createTB(path,capacity,sql)
            else:print("Create Error:Table could only be created under database!")
        else:print('Syntax Error:Keyword "'+key+'"after "Create" out of SQL criteria,try "Database" or "Table".')
    else:
        print('Syntax Error:Invalid expression after "Create".')
    return path

def createDB(path,db_name):#创建数据库
    target=os.path.join(path,db_name)
    if(not os.path.exists(target)):#如果指定数据库不存在,则创建
        os.mkdir(target)
        print('Database "'+db_name+'" has been created.')
        return target
    else:
        print('Database "'+db_name+'" already exists,you could input "cd '+db_name+'" to re-enter it.')
        return path

def createTB(path,capacity,sql):
    idx=sql.find('(')#查询语法中是否含有括号,以及括号数量是否匹配
    if(idx==-1):
        print("Syntax Error:No left bracket after Table.")
        return
    if(not match(sql)):
        print("Syntax Error:Invalid brackets after Table.")
        return

    tb_name=sql[:idx]#获取关系模式名称
    tb_name=tb_name.replace(" ","")
    target=os.path.join(path,tb_name)#获取即将创建上述关系模式的文件夹路径
    if(os.path.exists(target)):#如果关系模式已存在
        print('Create Error:Table "'+tb_name+'" already exists.')
        return
    
    primary_key=""#主码
    name=[]#属性
    datatype=[]#数据类型
    types=[]#基础数据类型
    constraints=[]#属性上的约束

    sql=sql[idx+1:-1]
    phrases=sql.split(',')#以','为分隔符获取各个属性或约束的描述
    for phrase in phrases:
        if(phrase[:11]=="primary key"):#如果描述的是主码约束
            if(primary_key==""):#如果主码不存在,则获取主码
                if(phrase[12]=='('):
                    primary_key=phrase[13:-1]
                else:primary_key=phrase[12:-1]
            else:print("Constraint Error:Mutiple primary key.")
        else:
            sp1=phrase.find(' ')#以' '为分隔符获取各个属性描述的细节
            sp2=phrase.find(' ',max(sp1+1,0))
            if(sp1==-1):
                print("Syntax Error:Invalid attribute expression "+phrase+".")
                return
            name.append(phrase[:sp1])#获取第一个细节:属性名
            if(sp2==-1):
                if(phrase[sp1+1:]=="int"):
                    types.append("int")
                elif(phrase[sp1+1:].__contains__("varchar")):
                    types.append("varchar")
                else:
                    print('Type Error:Datatype could only be "int" or "varchar",instead of "'+phrase[sp1+1:]+'" .')
                    return
                datatype.append(phrase[sp1+1:])#获取第二个细节:属性的数据类型
                constraints.append(None)#获取第三个细节:属性上的约束(optional)
            else:
                if(phrase[sp1+1:sp2]=="int"):
                    types.append("int")
                elif(phrase[sp1+1:sp2].__contains__("varchar")):
                    types.append("varchar")
                else:
                    print('Type Error:Datatype could only be "int" or "varchar",instead of "'+phrase[sp1+1:sp2]+'" .')
                    return
                datatype.append(phrase[sp1+1:sp2])
                constraints.append(phrase[sp2:])

    if(primary_key not in name):#主码描述的属性不存在
        print('Create Error:Primary key "'+primary_key+'" not found in attributes.')
        return
    if(primary_key==""):#未指定主码
        print('Create Error:Keyword "primary key" not found.')
        return
    
    pos=name.index(primary_key)#记录主码是关系模式中的第pos个属性
    os.mkdir(target)#以文件夹形式在当前数据库文件夹下创建关系模式
    
    table=pd.DataFrame([["" for attr in name] for i in range(capacity)],columns=name)
    table.to_csv(os.path.join(target,"Table.csv"))#在关系模式文件夹下以.csv格式创建空的关系模式表,用行坐标模拟存储地址

    target_index=os.path.join(target,"Index")
    os.mkdir(target_index)#在关系模式文件夹下创建索引文件夹

    np.save(os.path.join(target_index,"Empty.npy"),set(i for i in range(capacity)))#在索引文件夹下记录不含有效记录(元组)的存储地址
    for attr in name:
        np.save(os.path.join(target_index,attr+".npy"),BPT())#为每个属性创建空的B+树索引
    
    #记录元数据:主码(primary),主码下标(position),属性数(Property),最大存储容量(Capacity)
    meta=pd.concat([pd.DataFrame({"Description":["Primary","Position","Property","Capacity"]}),pd.DataFrame({" ":[primary_key,pos,len(name),capacity]})],axis=1)
    #属性名(Attribute),数据类型(Datatype),基本数据类型(Basictype),属性上的约束(Constraints)
    meta=pd.concat([meta,pd.DataFrame({"Attribute":name}),pd.DataFrame({"Datatype":datatype}),pd.DataFrame({"Basictype":types}),pd.DataFrame({"Constraints":constraints})],axis=1)
    meta.to_csv(os.path.join(target,"Meta.csv"),index=False)#以.csv格式在关系模式文件夹下存储元数据
    print('Table "'+tb_name+'" has been created.')

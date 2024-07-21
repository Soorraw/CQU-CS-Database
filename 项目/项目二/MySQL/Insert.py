#该文件定义和实现了向指定关系模式的元组插入操作

import os
import pandas as pd
import numpy as np
from BPlusTree import value

def excute(path,sql):
    if(sql[0:5]!="into "):#检查关键词
        print('Syntax Error:Invalid expression after "Insert".')
        return
    if(not sql.__contains__(" values")):
        print('Syntax Error:Keyword "values" not found after "Insert into".')
        return  
    
    sql=sql.replace("'","")#排列顺序一致时单引号或双引号不是必要的
    sql=sql.replace('"','')
    idx=sql.find(" values")
    idx1=sql.find('(')
    idx2=sql.find(')')

    tb_name=sql[5:idx]#获取关系模式名称
    tb_name=tb_name.replace(" ","")
    values=sql[idx1+1:idx2].replace(" ","").split(',')#以','为分隔符获取各个属性值

    if(len(values)==0):#无有效属性值
        print('Syntax Error:Values equal to zero.')

    target=os.path.join(path,tb_name)#获取指定关系模式的文件夹路径
    if(not os.path.exists(target)):#如果指定关系模式不存在
        print('Insert Error:Table "'+tb_name+'" does not exist.')
        return

    meta=pd.read_csv(os.path.join(target,"Meta.csv"))#读取元数据
    size=int(meta[" "].iloc[2])#属性数
    attr=[]
    for a in meta["Attribute"]:#属性名
        if(type(a)!=float):
            attr.append(a)
        else:break
    basic=meta["Basictype"]#数据类型
    primary=meta[" "].iloc[0]#主码
    pos=int(meta[" "].iloc[1])#主码下标

    if(len(values)>size):#如果插入的属性数大于关系模式属性数
        print("Insert Error:Values number ",len(values)," larger than attribute numbers ",size,"!")
        return

    table=pd.read_csv(os.path.join(target,"Table.csv"),index_col=0)#读取关系模式
    
    target_index=os.path.join(target,"Index")#获取指定关系模式的索引文件夹路径
    index={attr[i]:np.load(os.path.join(target_index,attr[i]+".npy"),allow_pickle=True).item() for i in range(len(attr))}#读取索引
    Empty=np.load(os.path.join(target_index,"Empty.npy"),allow_pickle=True).item()#读取空闲的存储地址
    if(len(Empty)==0):#如果没有空闲的存储地址
        print("Insert Error:The storage capacity has reached the maximum limit.")
        return

    idx=Empty.pop()#模拟操作系统,以伪随机的方式获取当前元组被分配的存储地址
    for i in range(len(values)-1):
        if(basic.iloc[i]=="int"):
            values[i]=int(values[i])#将属性值的数据类型转变为真实数据类型(str->Any)
    table.iloc[idx]=values#将元组写入关系模式表
    

    if(index[primary].find(values[pos])!=None):#如果主码对应属性的属性值已记录
        print("Insert Error:Violation of primary key constraints!")
        return
    
    for i in range(len(values)):
        index[attr[i]].insert(value(values[i],values[pos]),idx)#插入复合搜索码

    meta.to_csv(os.path.join(target,"Meta.csv"),index=False)#写回元数据
    table.to_csv(os.path.join(target,"Table.csv"))#写回关系模式
    
    np.save(os.path.join(target_index,"Empty.npy"),Empty)#写回空闲地址
    for i in range(len(attr)):
        np.save(os.path.join(target_index,attr[i]+".npy"),index[attr[i]])#写回索引
    
    print("Insert excuted.")
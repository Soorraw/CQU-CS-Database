#该文件定义和实现了从指定关系模式中删除符合特定条件的元组的操作

import os
import shutil
import pandas as pd
import numpy as np
from BPlusTree import BPlusTree as BPT
from BPlusTree import value

def excute(path,capacity,sql):
    if(sql[0:5]!="from "):#检查关键词
        print('Syntax Error:Invalid expression after "Delete".')
        return
    
    idx=sql.find(" where ")
    if(idx==-1):
        tb_name=sql[5:]
    else:tb_name=sql[5:idx]
    tb_name=tb_name.replace(" ","")

    target=os.path.join(path,tb_name)#获取指定关系模式的文件夹路径
    if(not os.path.exists(target)):#如果指定关系模式不存在
        print('Insert Error:Table "'+tb_name+'" does not exist.')
        return

    meta=pd.read_csv(os.path.join(target,"Meta.csv"))#读取元数据
    attributes=[]
    for a in meta["Attribute"]:#属性名
        if(type(a)!=float):
            attributes.append(a)
        else:break
    target_index=os.path.join(target,"Index")

    if(idx==-1):#如果不含'WHERE'关键词
        os.remove(os.path.join(target,"Table.csv"))
        table=pd.DataFrame([["" for j in range(len(attributes))] for i in range(capacity)],columns=attributes)
        table.to_csv(os.path.join(target,"Table.csv"))#在关系模式文件夹下以.csv格式重新创建空的关系模式表
        
        shutil.rmtree(target_index)#完全删除所有索引
        os.mkdir(target_index)#在关系模式文件夹下创建索引文件夹
        np.save(os.path.join(target_index,"Empty.npy"),set(i for i in range(capacity)))#在索引文件夹下重新初始化不含有效记录(元组)的存储地址
        for attr in attributes:
            np.save(os.path.join(target_index,attr+".npy"),BPT())#为每个属性重建空的B+树索引
        print("Delete excuted.")
        return
    
    sql=sql[idx+7:]
    Empty=np.load(os.path.join(target_index,"Empty.npy"),allow_pickle=True).item()#读取空闲的存储地址
    index={attributes[i]:np.load(os.path.join(target_index,attributes[i]+".npy"),allow_pickle=True).item() for i in range(len(attributes))}#读取索引

    result=set(i for i in range(capacity))#初始化结果集合
    search=sql.split(" and ")
    for sear in search:
        sear=sear.replace(" ","")
        if(sear.__contains__('>=')):#对每个谓词检查需求
            cmp='>='
            key_value=sear.split('>=')
        elif(sear.__contains__('<=')):
            cmp='<='
            key_value=sear.split('<=')
        elif(sear.__contains__('!=')):
            cmp='!='
            key_value=sear.split('!=')
        elif(sear.__contains__('>')):
            cmp='>'
            key_value=sear.split('>')
        elif(sear.__contains__('<')):
            cmp='<'
            key_value=sear.split('<')
        elif(sear.__contains__('<>')):
            cmp='<>'
            key_value=sear.split('<>')
        elif(sear.__contains__('=')):
            cmp='='
            key_value=sear.split('=')
        else:
            print('Delete Error:No comparison operator like ">",">=","<","<=","=","!=" or "<>" found in "'+sear+'"!')
            return
        key=key_value[0]#分割属性和属性值
        if(key not in attributes):
            print('Delete Error:Attribute "'+key+'" not contained in "'+tb_name+'".')
            return
        val=key_value[1]
        if((val[0]=="'" and val[-1]=="'") or (val[0]=='"' and val[-1]=='"')):#判断数据类型
            val=val[1:-1]
        else:val=int(val)
        if(cmp=='>'):
            res=index[key].findgt(val)
        elif(cmp=='>='):
            res=index[key].findge(val)
        elif(cmp=='<'):
            res=index[key].findlt(val)
        elif(cmp=='<='):
            res=index[key].findle(val)
        elif(cmp=='='):
            res=index[key].find(val)
        else:
            res=index[key].findne(val)
        if(res==None):
            result=None
            break
        result=result & set(res)#求检索结果的交集
    
    if(result==None):#集合为空则不进行任何删除
        print("Delete excuted.")
        return
     
    primary=meta[" "].iloc[0]#主码
    pos=int(meta[" "].iloc[1])#主码下标
    basic=meta["Basictype"]#数据类型
    table=pd.read_csv(os.path.join(target,"Table.csv"),index_col=0)#读取关系模式

    Empty=Empty | result#更新可存储地址
    for res in result:#更新索引
        if(basic.iloc[pos]=="int"):
            extra=int(table[primary].iloc[res])
        else:extra=table[primary].iloc[res]#获取主码
        for i in range(len(attributes)):
            attr=attributes[i]
            if(basic.iloc[i]=="int"):
                v=int(table[attr].iloc[res])
            else:v=table[attr].iloc[res]
            index[attr].delete(value(v,extra))#组合为唯一性复合搜索码,执行索引删除操作
    for res in result:
        table.iloc[res]=["" for attr in attr]#从关系模式中删除数据
    
    table.to_csv(os.path.join(target,"Table.csv"))#写回关系模式
    np.save(os.path.join(target_index,"Empty.npy"),Empty)#写回空闲地址
    for attr in attributes:
        np.save(os.path.join(target_index,attr+".npy"),index[attr])#写回索引
    print("Delete excuted.")

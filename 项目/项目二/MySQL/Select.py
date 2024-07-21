#该文件定义和实现了在指定关系模式上的查询操作

import os
import numpy as np
import pandas as pd

# def CrossJoin(A,B):#返回两个关系模式的笛卡尔积
#     resultA=pd.concat([A,pd.DataFrame({"Key":[0 for i in range(len(A))]})],axis=1)
#     resultB=pd.concat([B,pd.DataFrame({"Key":[0 for i in range(len(A))]})],axis=1)
#     return resultA.merge(resultB,on="Key").drop("Key",axis=1)

def excute(path,capacity,sql):
    idxf=sql.find(" from ")
    if(idxf==-1):
        print('Syntax Error:Keyword "From" not found.')
        return
    select=sql[:idxf].replace(" ","").split(",")#检索投影属性

    idxw=sql.find(" where ")#检查"Where"关键词的存在性
    if(idxw==-1):
        tb_name=sql[idxf+6:]#获取数据库名称
    else:tb_name=sql[idxf+6:idxw]
    tb_name=tb_name.replace(" ","")

    if(tb_name.__contains__(',')):#局限性
        print("'Limitation:Query on multiple relation schemas not supported.")
        return
    
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
    index={attributes[i]:np.load(os.path.join(target_index,attributes[i]+".npy"),allow_pickle=True).item() for i in range(len(attributes))}#读取索引

    result=set(i for i in range(capacity))#初始化结果集合
    search=sql[idxw+7:].split(" and ")#根据"Where"条件筛选
    for sear in search:
        sear=sear.replace(" ","")
        if(sear.__contains__('>=')):
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
            print('Select Error:No comparison operator like ">",">=","<","<=","=","!=" or "<>" found in "'+sear+'"!')
            return
        key=key_value[0]
        if(key not in attributes):
            print('Select Error:Attribute "'+key+'" not contained in "'+tb_name+'".')
            return
        val=key_value[1]
        if((val[0]=="'" and val[-1]=="'") or (val[0]=='"' and val[-1]=='"')):
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
        result=result & set(res)

    print("\nResult:")

    if(result==None):#集合为空则结果为空
        print()
        return
        
    table=pd.read_csv(os.path.join(target,"Table.csv"),index_col=0)#读取关系模式
    for sel in select:#打印属性列表
        print(sel,end="\t")
    print()
    for res in result:#打印符合条件的属性值
        for sel in select:
            print(table[sel].iloc[res],end="\t")
        print()
    print()

    index["name"].draw()
    print()
    index["age"].draw()
    print()
    index["sex"].draw()
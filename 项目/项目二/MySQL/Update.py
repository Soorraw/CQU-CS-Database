#该文件定义和实现了在指定关系模式上更新符合特定条件的元组的操作

import os
import numpy as np
import pandas as pd
from BPlusTree import value

def excute(path,capacity,sql):
    idx1=sql.find(" set ")
    if(idx1==-1):
        print('Syntax Error:Keyword "Set" not found after "Update".')
        return
    
    tb_name=sql[:idx1]
    tb_name=tb_name.replace(" ","")
    target=os.path.join(path,tb_name)#获取指定关系模式的文件夹路径
    if(not os.path.exists(target)):#如果指定关系模式不存在
        print('Update Error:Table "'+tb_name+'" does not exist.')
        return
    
    idx2=sql.find(" where ")#检索where关键词
    if(idx2==-1):
        reset=sql[idx1+5:]
    else:
        reset=sql[idx1+5:idx2]
        sql=sql[idx2+7:]

    meta=pd.read_csv(os.path.join(target,"Meta.csv"))#读取元数据
    attributes=[]
    for a in meta["Attribute"]:#属性名
        if(type(a)!=float):
            attributes.append(a)
        else:break
    target_index=os.path.join(target,"Index")
    index={attributes[i]:np.load(os.path.join(target_index,attributes[i]+".npy"),allow_pickle=True).item() for i in range(len(attributes))}#读取索引
    
    result=set(i for i in range(capacity))#初始化结果集
    if(idx2!=-1):
        search=sql.split(" and ")
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
                print('Update Error:No comparison operator like ">",">=","<","<=","=","!=" or "<>" found in "'+sear+'"!')
                return
            key=key_value[0]
            if(key not in attributes):
                print('Update Error:Attribute "'+key+'" not contained in "'+tb_name+'".')
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
                print("Update excuted.")
                break
            result=result & set(res)
    
    if(result==None):#集合为空则不进行任何更新
        print("Update excuted.")
        return

    reset=reset.replace(" ","")
    key_value=reset.split('=')
    key=key_value[0]
    val=key_value[1]
    idx=attributes.index(key)#更新属性下标
    if(idx==-1):
        print('Update Error:Attribute "'+key+'" not contained in the table "'+tb_name+'".')
        return
    
    primary=meta[" "].iloc[0]#主码
    pos=int(meta[" "].iloc[1])#主码下标
    basic=meta["Basictype"]#数据类型  
    table=pd.read_csv(os.path.join(target,"Table.csv"),index_col=0)#读取关系模式
    
    nvk=(not val.__contains__(key))#检索是否是自运算
    if(nvk):
        if(basic.iloc[idx]=="int"):#不是则直接得到更新值
            tv=int(val)
        else:
            tv=val.replace("'","")
            tv=tv.replace('"','')
    elif(basic.iloc[idx]=="int"):#否则检索自运算的操作符
        op=val.find('+')
        if(op==-1):
            op=val.find('-')
        if(op==-1):
            op=val.find('*')
        if(op==-1):
            op=val.find('/')
        if(op!=-1):
            dv=int(val[op+1:])
        else:
            print('Update Error:"+","-","*" and "/" not found.')
            return
    else:            
        print('Update Error:"+","-","*" and "/" not supported on attribute "'+key+'" with type "str".')
        return

    for res in result:#将索引更新拆分为旧索引的删除和新索引的插入
        if(basic.iloc[pos]=="int"):
            extra=int(table[primary].iloc[res])#计算唯一化属性
        else:extra=table[primary].iloc[res]
        if(basic.iloc[idx]=="int"):
            v=int(table[key].iloc[res])
        else:v=table[key].iloc[res]
        index[key].delete(value(v,extra))#删除更新前的索引
        
        if(not nvk):#计算自运算的结果
            if(val[op]=='+'):
                tv=int(table[key].iloc[res])+dv
            elif(val[op]=='-'):
                tv=int(table[key].iloc[res])-dv
            elif(val[op]=='*'):
                tv=int(table[key].iloc[res])*dv
            else:tv=int(table[key].iloc[res])/dv
        row=[vals for vals in table.iloc[res]]
        row[idx]=tv
        table.iloc[res]=row#更新关系模式
        index[key].insert(value(tv,extra),res)#插入更新后的索引
    
    table.to_csv(os.path.join(target,"Table.csv"))#写回关系模式
    for attr in attributes:
        np.save(os.path.join(target_index,attr+".npy"),index[attr])#写回索引
    print("Update excuted.")
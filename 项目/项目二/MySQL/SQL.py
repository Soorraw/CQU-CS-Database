#该文件定义了SQL指令的读取和部分处理操作

import os
import re
import Create,Drop,Insert,Delete,Update,Select
from System import pardir

class MySQL:
    def __init__(self,capacity=100):
        self.capacity=capacity
        self.root=os.path.join(pardir(os.getcwd()),"Database")#数据库根目录
        #print(os.path.abspath(self.root))
        if(not os.path.exists(self.root)):#根目录不存在时则自动新建
            os.mkdir(self.root)
        self.path=self.root#当前路径,默认为根路径
    
    def cksys(self,cmd):#检查是否是系统指令
        cmd=str.lower(cmd)
        if(cmd=="list"):
            print(os.listdir(self.path))
            return True
        elif(cmd=="cd."):
            if(self.path!=self.root):
                self.path=pardir(self.path)
            return True
        elif(cmd[0:3]=="cd "):
            if(self.path!=self.root):
                print('System Error:No access to the target file')
                return True
            if(len(cmd)<3):
                print('System Error:No valid expression after "cd".')
                return True
            db_name=cmd[3:]
            target=os.path.join(self.path,db_name)
            if(os.path.exists(target)):
                self.path=target
            else:print('System Error:No such Database called "'+db_name+'",try "Create Database" first.')
            return True
        #elif(cmd=="help"):
        return False
        
    def Run(self):
        while(True):
            sql=self.Get()
            if (sql=="exit"):
                print("Exited")
                break
            if(sql=="sys"):
                continue
            self.Analyze(sql)
                
    def Get(self):
        print(self.path+":")
        sql=input()
        if(sql.lower().__contains__("exit")):
            return "exit"
        if(self.cksys(sql)):
            return "sys"
        sql=sql.rstrip()
        
        while(not sql.endswith(';')):
            sql+=' '+input()
            sql=sql.rstrip()
        return sql

    def Analyze(self,sql):
        #预处理
        sql=sql.lstrip()#删除前导空格
        sql=re.sub("\\s{2,}"," ",sql)#将所有多空格转换为单空格
        sql=re.sub(" ;",";",sql)#删除;前的空格
        sql=sql.lower()#转换为小写
        sql=sql.replace(";","")#删除分号

        mat=re.match("[a-z]+ ",sql)
        if(mat):
            key=mat.group()
            sql=sql.replace(key,"")#根据首个关键词执行对应SQL操作
            if(key=="create "):#Create
                self.path=Create.excute(self.root,self.path,self.capacity,sql)
            elif(key=="drop "):#Drop
                Drop.excute(self.root,self.path,sql)
            elif(self.path==self.root):
                print("System Error:Current SQL sentences must be excuted under certain database!")
            elif(key=="insert "):#Insert
                Insert.excute(self.path,sql)
            elif(key=="delete "):#Delete
                Delete.excute(self.path,self.capacity,sql)
            elif(key=="update "):#Update
                Update.excute(self.path,self.capacity,sql)
            elif(key=="select "):#Select
                Select.excute(self.path,self.capacity,sql)
            else:print("Syntax Error:SQL keyword not found.")
        else:print("Syntax Error:Invalid SQL expression.")



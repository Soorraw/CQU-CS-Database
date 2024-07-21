#该文件定义和实现复合搜索码(value),B+树(BPlusTree)及其节点(Node)
#具体的技术原理见"数据库系统概念"-"索引"-"B+树"部分,此处不作赘述

import queue as que

class value:#复合搜索码(非唯一性搜索码)
    def __init__(self,v,extra):
        self.v=v#原始搜索码值
        self.extra=extra#唯一化属性

    #运算符重载
    def __lt__(self,t):#小于
        if(type(t)!=value):
            return self.v<t
        if(self.v==t.v):
            return self.extra<t.extra
        return self.v<t.v
    def __le__(self,t):#小于等于
        if(type(t)!=value):
            return self.v<=t
        if(self.v==t.v):
            return self.extra<=t.extra
        return self.v<t.v
    def __gt__(self,t):#大于
        if(type(t)!=value):
            return self.v>t
        if(self.v==t.v):
            return self.extra>t.extra
        return self.v>t.v
    def __ge__(self,t):#大于等于
        if(type(t)!=value):
            return self.v>=t
        if(self.v==t.v):
            return self.extra>=t.extra
        return self.v>t.v
    def __eq__(self,t):#等于
        if(type(t)!=value):
            return self.v==t
        return self.v==t.v and self.extra==t.extra
    def __ne__(self,t):#不等于
        if(type(t)!=value):
            return self.v!=t
        return self.v!=t.v or self.extra!=t.extra

class Node:#B+树节点
    def __init__(self,K,P,size=0,isleaf=False):
        self.K=K#搜索码值
        self.P=P#指针
        self.size=size#搜索码数量
        self.isleaf=isleaf#是否是叶子结点
        self.par=None#父节点
        self.parp=None#父节点指向该节点的指针的下标
    
    def set(self,K,P,size):#设置节点属性
        self.K=K
        self.P=P
        self.size=size

class BPlusTree:#B+树
    def __init__(self,n=4):
        self.root=None#根节点
        self.n=n#B+树节点的最大孩子数
    
    def lower_bound(self,it,v):#二分搜索,返回当前节点中大于等于当前搜素码的最小值下标;不存在时返回None
        l=0
        r=it.size-1

        if(it.K[r]<v):
            return None
        while(l<r):
            mid=(l+r)//2
            if(it.K[mid]>=v):
                r=mid
            else:l=mid+1
        return l

    def draw(self):#以BFS方式打印当前B+树
        if(self.root==None):
            print([])
            return
        
        dep=0
        q=que.Queue()
        q.put([self.root,1])

        while(not q.empty()):
            [it,d]=q.get()
            if(type(it.K[0])==value):#对于复合搜索码,只打印原始搜索码值
                kv=[k.v for k in it.K]
            else:kv=it.K
            if(d==dep):
                print(kv,end="")
            else:
                if(it==self.root):
                    print(kv,end="")
                else:
                    print()
                    print(kv,end="")
                dep+=1
            if(not it.isleaf):
                for p in it.P:
                    q.put([p,d+1])
        print()
            
    def findfirst(self,it,v):#返回B+树叶子层中含有搜索码值v的最左侧叶子节点
        if(it==None):
            return None
        if(it.isleaf):
            i=self.lower_bound(it,v)
            if(i==None):
                return None
            return it
        
        i=self.lower_bound(it,v)
        if(i==None):
            return self.findfirst(it.P[it.size],v)
        attempt=self.findfirst(it.P[i],v)
        if(attempt!=None):
            return attempt
        return self.findfirst(it.P[i+1],v)

    def find(self,v):#查询属性值等于指定搜索码值的元组的存储地址
        it=self.findfirst(self.root,v)
        if(it==None):
            return None

        result=[]
        i=self.lower_bound(it,v)

        done=False
        while(not done):
            if(i<it.size and it.K[i]==v):
                result.append(it.P[i])
                i+=1
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findRange(self,lb,ub):#查询属性值在指定搜索码值区间(lb<=v<=ub)的元组的存储地址
        it=self.findfirst(self.root,lb)
        if(it==None):
            return None

        result=[]
        i=self.lower_bound(it,lb)

        done=False
        while(not done):
            if(i<it.size and it.K[i]<=ub):
                result.append(it.P[i])
                i+=1
            elif(i<it.size and it.K[i]>ub):
                done=True
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findlt(self,ub):#查询属性值在指定搜索码值小于ub的元组的存储地址
        it=self.root
        if(it==None):
            return None
        
        while(not it.isleaf):
            it=it.P[0]

        result=[]
        i=0

        done=False
        while(not done):
            if(i<it.size and it.K[i]<ub):
                result.append(it.P[i])
                i+=1
            elif(i<it.size and it.K[i]>=ub):
                done=True
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findle(self,ub):#查询属性值在指定搜索码值小于等于ub的元组的存储地址
        it=self.root
        if(it==None):
            return None
        
        while(not it.isleaf):
            it=it.P[0]

        result=[]
        i=0

        done=False
        while(not done):
            if(i<it.size and it.K[i]<=ub):
                result.append(it.P[i])
                i+=1
            elif(i<it.size and it.K[i]>ub):
                done=True
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findgt(self,lb):#查询属性值在指定搜索码值大于lb的元组的存储地址
        it=self.findfirst(self.root,lb)
        if(it==None):
            return None

        result=[]
        i=self.lower_bound(it,lb)
        if(it.K[i]==lb):
            i=i+1

        done=False
        while(not done):
            if(i<it.size):
                result.append(it.P[i])
                i+=1
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findge(self,lb):#查询属性值在指定搜索码值大于等于lb的元组的存储地址
        it=self.findfirst(self.root,lb)
        if(it==None):
            return None

        result=[]
        i=self.lower_bound(it,lb)

        done=False
        while(not done):
            if(i<it.size):
                result.append(it.P[i])
                i+=1
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None
    
    def findne(self,v):#查询属性值在指定搜索码值不等于v的元组的存储地址
        it=self.root
        if(it==None):
            return None

        while(not it.isleaf):
            it=it.P[0]

        result=[]
        i=0

        done=False
        while(not done):
            if(i<it.size and it.K[i]!=v):
                result.append(it.P[i])
                i+=1
            elif(i<it.size and it.K[i]==v):
                i+=1
            elif(i==it.size and it.P[it.size]!=None):
                it=it.P[it.size]
                i=0
            else:done=True

        if(not len(result)==0):
            return result
        return None

    def insert(self,k,p):#向B+树索引中插入搜索码值为k,对应元组存储地址为p的键值对
        if(self.root==None):
            it=self.root=Node([],[None],isleaf=True)
            #很令人迷惑的特性:如果类的某个属性的默认参数是[],当新建一个对象时,python不会真的拿[]去初始化该属性,
            #而是使用上一次实例化这类对象的对应属性去初始化该属性。以Node类为例,不能写作def __init__(self,K=[]),it=Node()
            #而只能写作def __init__(self,K),并在调用时写作it=Node(K=[])
        else:
            it=self.root
            while(not it.isleaf):
                i=self.lower_bound(it,k)
                if(i==None):
                    it.P[it.size].par=it
                    it=it.P[it.size]
                else:
                    it.P[i].par=it
                    it=it.P[i]
        if(it.size<self.n-1):
            self.insert_in_leaf(it,k,p)
        else:
            t=Node(it.K,it.P[:it.size+1],it.size)
            self.insert_in_leaf(t,k,p)
            that=Node(t.K[(t.size+1)//2:t.size],t.P[(t.size+1)//2:t.size+1],t.size-(t.size+1)//2,True)
            it.set(t.K[:(t.size+1)//2],t.P[:(t.size+1)//2]+[that],(t.size+1)//2)
            self.insert_in_parent(it,that.K[0],that)

    def insert_in_leaf(self,it,k,p):#在插入过程中更新B+树索引的叶子层,由insert函数自行调用
        if(it.size==0):
            it.K.append(k)
            it.P.insert(0,p)
        elif(it.K[0]>k):
            it.K.insert(0,k)
            it.P.insert(0,p)
        else:
            i=self.lower_bound(it,k)
            if(i==None):
                it.K.append(k)
                it.P.insert(it.size,p)
            else:
                it.K.insert(i,k)
                it.P.insert(i,p)
        it.size+=1

    def insert_in_parent(self,it,k,that):#在插入过程中更新B+树索引的内部结点,由insert函数自行调用
        if(it==self.root):
            self.root=Node([k],[it,that],1)
            return
        par=it.par
        if(par.size+1<self.n):
            i=self.lower_bound(par,k)
            if(i==None):
                par.K.append(k)
                par.P.append(that)
            else:
                par.K.insert(i,k)
                par.P.insert(i+1,that)
            par.size+=1
        else:
            t=Node(par.K,par.P,par.size)
            i=self.lower_bound(t,k)
            if(i==None):
                t.K.append(k)
                t.P.append(that)
            else:
                t.K.insert(i,k)
                t.P.insert(i+1,that)
            t.size+=1
            par.set(t.K[:(t.size+1)//2],t.P[:(t.size+1)//2+1],(t.size+1)//2)
            k=t.K[(t.size+1)//2]
            part=Node(t.K[(t.size+1)//2+1:t.size],t.P[(t.size+1)//2+1:t.size+1],t.size-(t.size+1)//2-1)
            self.insert_in_parent(par,k,part)
    
    def delete(self,k):#删除B+树索引中搜索码值为k的键值对(此时的搜索码是唯一性搜索码)
        it=self.root
        while(not it.isleaf):
            i=self.lower_bound(it,k)
            if(i==None):
                it.P[it.size].par=it
                it.P[it.size].parp=it.size
                it=it.P[it.size]
            elif(it.K[i]==k):
                it.P[i+1].par=it
                it.P[i+1].parp=i+1
                it=it.P[i+1]
            else:
                it.P[i].par=it
                it.P[i].parp=i
                it=it.P[i]
        
        self.delete_entry(it,k)

    def delete_entry(self,it,k,offset=0):#在删除过程中更新B+树索引的内部节点,由delete函数自行调用
        i=self.lower_bound(it,k)
        del it.K[i]
        del it.P[i+offset]
        it.size-=1

        if(it==self.root and it.size==0):
            self.root=it.P[0]
            del it
            return

        if((it.isleaf and it.size<self.n//2) or (not it.isleaf and it.size<(self.n-1)//2)):
            if(it==self.root):
                return
            par=it.par
            i=it.parp
            if(i==par.size):
                left=par.P[i-1]
                right=None
            elif(i==0):
                left=None
                right=par.P[i+1]
            else:
                left=par.P[i-1]
                right=par.P[i+1]
            
            if(left!=None and left.size+it.size<self.n):
                k=par.K[i-1]
                if(not it.isleaf):
                    left.set(left.K+[k]+it.K,left.P+it.P,left.size+it.size+1)
                else:left.set(left.K+it.K,left.P[:left.size]+it.P,left.size+it.size)
                self.delete_entry(par,k,1)
                del it
            elif(right!=None and it.size+right.size<self.n):
                k=par.K[i]
                if(not right.isleaf):
                    it.set(it.K+[k]+right.K,it.P+right.P,it.size+right.size+1)
                else:it.set(it.K+right.K,it.P[:it.size]+right.P,it.size+right.size)
                self.delete_entry(par,k,1)
                del right
            else:
                if(left!=None):
                    k=par.K[i-1]
                    left.size-=1
                    lastk=left.K.pop()
                    if(not it.isleaf):
                        lastp=left.P.pop()                      
                        it.K=[k]+it.K
                    else:
                        lastp=left.P.pop(left.size-1)
                        it.K=[lastk]+it.K
                    it.P=[lastp]+it.P
                    par.K[i-1]=lastk
                else:
                    k=par.K[i]
                    right.size-=1
                    firstk=right.K.pop(0)
                    firstp=right.P.pop(0)
                    if(not it.isleaf):
                        it.K=it.K+[k]
                        it.P.append(firstp)
                    else:
                        it.K=it.K+[firstk]
                        it.P.insert(it.size,firstp)
                    par.K[i]=firstk
                it.size+=1

#唯一性搜索码测试数据
# it=BPlusTree()
# it.insert("Gold",23)
# it.insert("Califieri",53)
# it.insert("Einstein",12)
# it.insert("Mozart",77)
# it.insert("Adaks",131)
# it.insert("Brandt",92)
# it.insert("Crick",8)
# it.insert("Katz",9)
# it.insert("Kim",101)
# it.insert("Singh",31)
# it.insert("Wu",67)
# it.insert("Yu",84)
# it.insert("Zhu",191)
# it.insert("El Said",287)
# it.insert("Srinivasan",81)
# print(it.findne("Wu"))
# it.draw()


#非唯一性搜索码唯一化测试数据
# it=BPlusTree()
# it.insert(value("Gold",0),23)
# it.insert(value("Califieri",1),53)
# it.insert(value("Einstein",2),12)
# it.insert(value("Mozart",3),77)
# it.insert(value("Adaks",4),131)
# it.insert(value("Brandt",5),92)
# it.insert(value("Crick",6),8)
# it.insert(value("Katz",7),9)
# it.insert(value("Kim",8),101)
# it.insert(value("Singh",9),31)
# it.insert(value("Wu",10),67)
# it.insert(value("Yu",11),84)
# it.insert(value("Zhu",12),191)
# it.insert(value("El Said",13),287)
# it.insert(value("Srinivasan",15),81)
# it.draw()
# it.insert(value("Srinivasan",14),80)
# it.insert(value("Srinivasan",16),82)
# it.draw()

#删除和查询测试数据
# print(it.find("Srinivasan"))
# it.draw()
# print(it.findRange("Sri","Srj"))
# it.delete("Wu")
# it.draw()
# print(it.findRange("Adaks","Zhu"))
# it.delete("Zhu")
# it.draw()
# it.delete("Gold")
# it.draw()
# it.delete("Yu")
# it.delete("Srinivasan")
# it.draw()
# it.delete("Kim")
# it.draw()
# print(it.find("Einstein"))
# it.delete("Mozart")
# it.draw()
# it.delete("Crick")
# it.draw()
# it.delete("El Said")
# it.draw()
# it.delete("Adaks")
# it.draw()
# it.delete("Einstein")
# it.draw()
# it.delete("Kate")
# it.draw()
# it.delete("Califieri")
# it.draw()
# it.delete("Brandt")
# it.delete("Singh")
# it.draw()
# print(it.findRange("Adaks","Zhu"))
# print(it.find("Einstein"),it.find("Brandt"))
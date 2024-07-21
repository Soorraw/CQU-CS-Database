3.使用手册
3.1基本设置
1)大小写不敏感
2)数据类型暂时只支持"int"和"varchar",后者的实际长度未作约束
3)字符串以" "或' '标识
4)暂时仅支持单一属性作为主码并支持主码约束的检测,暂不支持外码,属性集上的约束暂时只能记录为元数据
5)暂时仅支持单个关系模式上的数据筛选(Select)
6)下述”拒绝支持”一般意味着程序本身而非Python会打印对应的错误信息

3.2支持的指令
支持的指令如下(双引号内的内容代表用户在此处的输入值为一个自定义变量,且双引号本身不必输入):

1)System类(以下不必以';'结尾)
(1)"list":
打印当前目录。

(2)"cd 'name'":
进入名称为"name"的指定子目录。只允许从Database目录进入某个子目录(即某个数据库),非法访问将被拒绝。

(3)"cd.":
返回当前目录的父目录。只允许从Database的某个子目录(即某个数据库)返回Database目录,非法返回将被无效化。

(4)"exit":
退出程序。

2)Create类
(1)"Create Database 'db_name';":
创建名为"db_name"的数据库。该指令强制在Database目录下执行,在非法的目录下创建数据库会被拒绝(如在数据库中创建数据库)。

(2)"Create Database 'tb_name'(attribute1 datatype1 constraint1,attribute2 datatype2,...,primary key(attribute));":
创建关系模式"tb_name"。"Attribute","Datatype"和"Constraint"分别表示属性名,属性的数据类型和属性上的约束,其中属性上的约束是可选的(可写可不写)。"primary key"(主码)是必选的。
该指令强制在Database的某个子目录(即某个数据库)下执行,在非法的目录下创建关系模式会被拒绝(如在Database目录下创建关系模式)。
以下内容将被拒绝执行:指定数据库或关系模式已经存在/"Create"关键词后的对象不属于"Database"或"Table"中的任意一种/括号不匹配/声明多个主码/未声明主码。

3)Drop类
(1)"Drop Database 'db_name';":
删除名为"db_name"的数据库。该指令强制在Database目录下执行,在非法的目录下删除数据库会被拒绝(如在数据库中删除数据库)。

(2)"Drop Database 'tb_name';":
删除名为"tb_name"的关系模式。该指令强制在Database的某个子目录(即某个数据库)下执行,在非法的目录下删除关系模式会被拒绝(如在Database目录下删除关系模式)。此后的指令均遵守这一原则,故不再赘述。
 以下内容将被拒绝执行:指定数据库或关系模式不存在/"Drop"关键词后的对象不属于"Database"或"Table"中的任意一种。

4)Insert类
(1)"Insert into 'tb_name' values(value1,value2);":
在名为"tb_name"的关系模式中插入一个元组,元组属性值的排列顺序和关系模式中对应属性的排列顺序一致。
以下内容将被兼容执行:元组属性值的数量小于等于关系模式(自动填充null)。
 以下内容将被拒绝执行:违反主码约束/元组属性的数量大于关系模式/指定关系模式不存在/关键词"into"或"values"缺失/元组属性值的数据类型不符合对应的关系模式属性值的数据类型。

5)Delete类
(1)"Delete from 'tb_name';":
删除名为"tb_name"的关系模式中的所有元组,但保留关系模式本身。

(2)"Delete from 'tb_name' where attribute1=value1 and attribute2>=value2 and...;":
删除名为"tb_name"的关系模式中的符合条件的元组。
作为首个涉及"where"关键词的指令,目前暂时只支持用"and"关键词所连接的下列检索条件之一或任意组合:"=","!="(<>),">",">=","<","<="。此后的指令均符合这一前提。
以下内容将被拒绝执行:指定的关系模式不存在/"Drop"关键词后缺少"from"关键词/"where"关键词后的检索条件无法支持/检索的属性不存在。

6)Update类
(1)"Update 'tb_name' set attribute=value;":
更新名为"tb_name"的关系模式中的所有元组的指定属性。
"set"关键词后的"attribute=expression"中的表达式expression可以为常量value(int或string型)或包含attribute本身和常量值value的组合式,支持的组合式为下列组合式之一:attribute=attribute+value,attribute=attribute-value,
attribute=attribute*value,attribute=attribute/value。

(2)"Update 'tb_name' set attribute=value; where attribute1=value1 and attribute2>=value2 and...;":
更新名为"tb_name"的关系模式中的符合条件的元组。"set"关键词的相关内容同上。
以下内容将被拒绝执行:指定的关系模式不存在/"Update"关键词后缺少"set"关键词/表达式expression不合法/"where"关键词后的检索条件无法支持/检索的属性不存在。

7)Select类
(1)"Select attribut1,attribut2,...from 'tb_name';"
选择名为"tb_name"的关系模式中的所有元组的对应属性并打印在控制台。
尽管程序提供了笛卡尔积(Cross Join)的函数,但由于笛卡尔积通常需要和自然连接(Natural Join)和嵌套查询等相对更加高级的语法组合使用,单纯打印庞大的笛卡尔积结果是效率低下且一般没有实际意义的,因此在本次实验中暂不使用该函数,也因此暂不提供多个关系模式上的查询。

(2)"Select attribut1,attribut2,...from 'tb_name' where attribute1=value1 and attribute2>=value2 and...;"
选择名为"tb_name"的关系模式中的符合条件的元组的对应属性并打印在控制台。
以下内容将被拒绝执行:指定的关系模式不存在/"Select"关键词后缺少"from"关键词/"where"关键词后的检索条件无法支持/检索的属性不存在。

3.3索引
程序将在关系模式创建时隐式的为每个属性使用主码作为唯一化属性创建B+树索引,其插入,删除和更新是隐式执行的。
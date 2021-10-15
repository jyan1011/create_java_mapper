# 前言
本项目最初是由于工作需要，方便生成springboot项目的Mapper和Model类而写的一个工具类，现在经过优化后拿出来与各位分享，暂时只支持Mysql数据库。

# 使用要求
- Python3环境
- pymysql插件
```bash
# 需先安装python3环境与pip工具后在终端控制台执行以下命令来安装pymysql
pip3 insall pymysql
```

# 使用方法
## 下载
1. Github下载：https://github.com/jyan1011/create_java_mapper/archive/master.zip
2. 百度网盘下载：

## 配置文件
1. 复制项目文件夹内的**config.py.template**文件，重命名为**config.py**
2. 进行数据库配置，配置详细如下：
```python
host = '127.0.0.1'  # 数据库地址
port = 3306 # 数据库端口，默认3306
user = 'dbuser' # 数据库用户名
pwd = 'dbpwd' # 数据库密码
db = 'test' # 数据库名称
# 指定导出的表，支持使用%通配，支持逗号分隔多表，留空默认查全表
# tables='tb_%,test_name'
tables = '%'

# 指定导出目录，不指定默认输出到当前目录
path = ''

# 指定model文件导出的包，会在指定导出目录下按照包结构生成文件夹
model = 'com.cn.model'
# model文件是否启用lombok @Data注解
lombok = True
# 指定mapper文件导出的包，会在指定导出目录下按照包结构生成文件夹
mapper = 'com.cn.mapper'
```

## 运行
1. Mac、Linux系统下直接在工具目录的终端运行
```bash
python3 create_java_mapper.py
```
2. Windows系统可直接双击目录下的`run.bat`执行

---
# 问题反馈与打赏
1. 如有疑问或发现问题，欢迎在本人小破站留言回复或直接提Issues
2. 如果您觉得此工具对您有用，欢迎打赏，本人博客地址：[Joeyの技术小栈](https://yanjiayu.cn)
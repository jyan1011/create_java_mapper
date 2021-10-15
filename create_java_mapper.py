import os
import re
from string import Template

import pymysql

import config


# 转换mysql数据类型为java数据类型
def getMysqlType(key):
    mysqlType = {'int': 'Integer', 'bigint': 'Long', 'varchar': 'String', 'decimal': 'Double', 'float': 'Double',
                 'double': 'Double', 'decimal': 'Double', 'date': 'Date', 'datetime': 'Date', 'timestamp': 'Date',
                 'longtext': 'String'}
    key = key.split('(')[0]
    if (key in mysqlType):
        return mysqlType[key]
    else:
        print('typeError')
        return 'String'


# 驼峰命名转换
def underline2hump(underline_str):
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


# 首字母大写
def upperFirst(str):
    return str[0].upper() + str[1:]


# 获取模板文件内容
def getTemplate(fileName):
    file = 'template/' + fileName
    with open(file, 'r') as f:
        return f.read()


# 根据表名获取所有字段，类型，注释
def getAllColumns(cursor, tableName):
    # 根据数据库以及表名获取所有字段和备注
    sql = "select COLUMN_NAME,COLUMN_TYPE,column_comment from INFORMATION_SCHEMA.Columns where table_name = '%s' and table_schema = '%s' order by ORDINAL_POSITION"
    cursor.execute(sql % (tableName, config.db))
    return cursor.fetchall()


# 获取所有表
def getAllTables(cursor):
    sql = "show tables"
    if len(config.tables) > 0:
        tables = config.tables.split(",")
        where = ""
        columnName = "Tables_in_" + config.db
        for table in tables:
            if len(where) == 0:
                where += " where " + columnName + " like '" + table + "'"
            else:
                where += " or " + columnName + " like '" + table + "'"
        sql += where
    cursor.execute(sql)
    return cursor.fetchall()


# 创建实体类内容
def createModel(packageName, tableName, columns, lombok):
    # 设定包名，引用包，类名，对象名，get、set方法
    class_name = upperFirst(underline2hump(tableName))  # 类名
    propertys = ''  # 对象
    methods = ''  # get/set方法
    import_package = ''  # 是否有其他引入包
    lombok_annotation = ''  # lombok注解
    for c in columns:
        temp = ''  # 对象临时值
        javaType = getMysqlType(c[1])  # 对象Java类型
        if (javaType == 'Date'):
            import_package = 'import java.util.Date;'
        if (c[2]):
            temp += '    /**\n    * %s\n    */\n' % (c[2])
        temp += '    private %s %s;' % (javaType, underline2hump(c[0])) + "\n"
        propertys += temp
        p1 = '    public %s get%s() {\n        return this.%s;\n    }\n\n' % (
            javaType, upperFirst(underline2hump(c[0])), underline2hump(c[0]))
        p2 = '    public void set%s(%s %s) {\n        this.%s = %s;\n    }\n' % (
            upperFirst(underline2hump(c[0])), javaType, underline2hump(c[0]), underline2hump(c[0]),
            underline2hump(c[0]))
        if not lombok:
            methods += p1 + p2
    # 获取模板
    template = Template(getTemplate('model.template'))
    # lombok配置
    if lombok:
        import_package += 'import lombok.Data;'
        lombok_annotation = '@Data'
    # 替换模板内容
    packageName += ';\n\n' + import_package
    result = template.substitute(package=packageName, class_name=class_name, property=propertys, method=methods,
                                 lombok=lombok_annotation)
    return result;


# 创建mapper内容
def createMapper(packageName, tableName, columns, model_package):
    # 设定包名,类名，getById（），saveOne(),updateOne()
    package = packageName
    class_name = upperFirst(underline2hump(tableName)) + "Mapper"  # 类名
    table_name = tableName
    hump_name = underline2hump(tableName)
    model_name = upperFirst(underline2hump(tableName))
    column_result = ''
    insert_method = ''
    insert_pre = '"insert into `%s`  <trim prefix=\'(\' suffix=\')\' suffixOverrides=\',\' > "\n    ' % (table_name)
    insert_back = '+ "<trim prefix=\'values (\' suffix=\')\' suffixOverrides=\',\'>"\n    '
    update_method = '"update `%s` <set> "\n    ' % (table_name)

    for c in columns:
        if not (c[0] == 'id'):
            column_result += '@Result(column = "%s", property = "%s"),\n    ' % (c[0], underline2hump(c[0]))
            insert_pre += '+ "<if test=\'item.%s != null\' > %s, </if> " \n    ' % (underline2hump(c[0]), c[0])
            insert_back += '+ "  <if test=\'item.%s != null\'> #{item.%s}, </if>" \n    ' % (
                underline2hump(c[0]), underline2hump(c[0]))
            update_method += '+ "<if test=\'item.%s != null\'> %s = #{item.%s}, </if>" \n    ' % (
                underline2hump(c[0]), c[0], underline2hump(c[0]))

    insert_method = insert_pre + '+" </trim>"\n    ' + insert_back + '+ "</trim>" \n    '
    update_method += '+ "</set> where id = #{item.id}" \n    '
    column_result = column_result[:-1]
    # 获取模板
    template = Template(getTemplate('mapper.template'))
    # 替换模板内容
    result = template.substitute(package=package, hump_name=hump_name, column_result=column_result,
                                 class_name=class_name, table_name=table_name, insert_method=insert_method,
                                 update_method=update_method, model_name=model_name, model_package=model_package)
    return result


# 导出
def createJavaFile(filePath, fileName, fileContent):
    print(filePath, fileName)
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    with open((filePath + "/" + fileName), 'w', encoding='utf-8') as f:
        f.write(fileContent)


if __name__ == '__main__':
    print('start')
    conn = pymysql.connect(host=config.host, port=config.port, user=config.user, password=config.pwd, db=config.db)
    cursor = conn.cursor()
    for t in getAllTables(cursor):
        tableName = t[0]
        column = getAllColumns(cursor, tableName)
        # 创建model对象
        createJavaFile(config.path + config.model.replace('.', '/'),
                       (upperFirst(underline2hump(tableName)) + '.java'),
                       createModel(config.model, tableName, column, config.lombok))
        # 创建mapper对象
        createJavaFile((config.path + config.mapper.replace('.', '/')),
                       (upperFirst(underline2hump(tableName)) + 'Mapper.java'),
                       createMapper(config.mapper, tableName, column, config.model))
    conn.close()
    print('end')

import re
import pandas as pd
from io import StringIO
import csv

# 读取SQL文件内容
with open('F:\试卷\剑桥英语\word.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 正则匹配所有INSERT语句
insert_pattern = re.compile(
    r'INSERT INTO `word` VALUES\s*\((.*?)\);',
    re.IGNORECASE | re.DOTALL
)
matches = insert_pattern.findall(sql_content)

# 定义列名（根据CREATE TABLE语句的字段顺序）
columns = [
    'id', 'word', 'english_pronunciation', 'america_pronunciation',
    'GQS', 'GQFC', 'XZFC', 'FS', 'meaning', 'example',
    'vc_frequency', 'vc_study_user_count', 'announce'
]

data = []

# 解析每条INSERT语句的值
for values_str in matches:
    # 处理换行符和多余空格
    values_str = values_str.replace('\n', ' ').strip()
    
    # 使用更稳健的方式解析字段（考虑字段内可能包含逗号）
    # 1. 按逗号分割，但忽略引号内的逗号
    # 2. 使用正则匹配字段
    field_pattern = re.compile(
        r'''((?:[^,'"]|'(?:\\.|[^'])*'|"(?:\\.|[^"])*")+)''',
        re.IGNORECASE | re.DOTALL
    )
    fields = [f.strip() for f in field_pattern.split(values_str) if f.strip() and f.strip() != ',']
    
    # ...（前面的代码保持不变，直到 fields = ... 部分）

    # 检查字段数量是否匹配
    if len(fields) < len(columns):
        # 补全缺失的字段为NULL
        fields += [None] * (len(columns) - len(fields))
    elif len(fields) > len(columns):
        print(f"警告：跳过字段过多的行（预期 {len(columns)}，实际 {len(fields)}）")
        continue

    processed_row = []
    for field in fields:
        if field is None or field.upper() == 'NULL':
            processed_row.append(None)
        else:
            if (field.startswith("'") and field.endswith("'")) or \
               (field.startswith('"') and field.endswith('"')):
                field = field[1:-1]
            processed_row.append(field)
    data.append(processed_row)

# 创建DataFrame并导出Excel
if data:
    df = pd.DataFrame(data, columns=columns)
    df.to_excel('word_export.xlsx', index=False, engine='openpyxl')
    print(f"导出成功！共 {len(data)} 条数据，保存为 word_export.xlsx")
else:
    print("未解析到有效数据，请检查SQL文件格式！")

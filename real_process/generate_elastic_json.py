#%%
import csv
import json

# 文件路径
input_csv_file = "../dataset/PP_recipes.csv"  # 输入 CSV 文件路径
output_bulk_file = "../dataset/elastic_bulk_recipes.json"  # 输出 Elasticsearch Bulk 文件路径
index_name = "ingredient"  # Elasticsearch 索引名

# 处理 CSV 文件并生成 Bulk 文件
try:
    with open(input_csv_file, mode="r", encoding="utf-8") as csvfile, open(output_bulk_file, mode="w", encoding="utf-8") as outfile:
        reader = csv.DictReader(csvfile)
        
        for doc_id, row in enumerate(reader, start=1):  # 从 1 开始生成 `_id`
            try:
                # 写入 Bulk API 的操作行
                action_line = {"index": {"_index": index_name, "_id": doc_id}}
                outfile.write(json.dumps(action_line, ensure_ascii=False) + "\n")
                
                # 写入文档内容
                document = {
                    "id": int(row["id"]),  # 转换为整数
                    "ingredient_ids": json.loads(row["ingredient_ids"]),  # 将字符串解析为列表
                }
                outfile.write(json.dumps(document, ensure_ascii=False) + "\n")
            
            except KeyError as e:
                print(f"KeyError processing document with _id {doc_id}: Missing column {e}")
            except (ValueError, SyntaxError) as e:
                print(f"Error processing document with _id {doc_id}: {e}")
    
    print(f"Bulk JSON 文件已成功生成: {output_bulk_file}")

except FileNotFoundError:
    print(f"错误：未找到输入文件 '{input_csv_file}'。")
except Exception as e:
    print(f"发生未知错误：{e}")

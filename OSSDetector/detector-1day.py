import os
import pandas as pd

# 读取cve-version.xlsx文件
cve_df = pd.read_excel('cve-version.xlsx')

def check_version(repo_name, version):
    repo_rows = cve_df[cve_df['repoName'] == repo_name]
    # print(repo_rows)
    if not repo_rows.empty:
        repo_versions_str = repo_rows['versions'].iloc[0]  # 获取版本号字符串
        repo_versions_list = repo_versions_str.strip("[]").replace("'", "").split(", ")
        # print(repo_versions_list)
        if version in repo_versions_list or (version == repo_name and repo_versions_str == "[]"):
            return True
    return False


# 创建一个空的 DataFrame 用于存储匹配的数据
matched_data = []

# 遍历res-ssdeep-centris目录下的文件
centris_directory = 'res-ssdeep-centris/'
for filename in os.listdir(centris_directory):
    with open(centris_directory + filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            items = line.strip().split('\t')
            repo_name = items[1]
            version = items[2]
            if check_version(repo_name, version):
                cve_info = cve_df[cve_df['repoName'] == repo_name].iloc[0]
                matched_data.append({
                    'Item': items[0],
                    'repo_name': repo_name,
                    'version': version,
                    'cve_id': cve_info['cve_id'],
                    'cwe_id': cve_info['cwe_id'],
                    'base_score': cve_info['base_score']
                })

# 将匹配的数据转换为 DataFrame
matched_df = pd.DataFrame(matched_data)

# 将匹配的数据写入到新的Excel文件
matched_df.to_excel('matched_data.xlsx', index=False)

import datetime as dt
import os
import sys
#sys.path.insert(0, "../osscollector")
#import OSS_Collector
import subprocess
import re
import shutil
import json
import time


"""GLOBALS"""
currentPath		= os.getcwd()
theta1 = 0.003
theta2 = 0.5
theta3 = 0.8
theta4 = 0.2
resultPath		= currentPath + "/res_dataset-demo/"
repoFuncPath	= "../osscollector/repo_functions/"
verIDXpath		= currentPath + "/../pre/verIDX_ours/"
initialDBPath	= currentPath + "/../pre/initialSigs_ours/"
finalDBPath		= currentPath + "/../pre/componentDB_ours_6.0/"
metaPath		= currentPath + "/../pre/metaInfos_ours_6.0/"
aveFuncPath		= metaPath + 'aveFuncs'
weightPath		= metaPath + "weights_ours_6.0/"
ctagsPath		= "/usr/local/bin/ctags"
datasetPath     = currentPath + "/../sample"
datePath		= '../repo-date/'
log = 'shiyandemo'


shouldMake 	= [resultPath]
for eachRepo in shouldMake:
    if not os.path.isdir(eachRepo):
        os.mkdir(eachRepo)
class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.terminal.flush()  # 不启动缓冲,实时输出
        self.log.flush()

    def flush(self):
        pass

# Generate TLSH
def computeTlsh(string):
    string 	= str.encode(string)
    hs 		= tlsh.forcehash(string)
    return hs


def removeComment(string):
    # Code for removing C/C++ style comments. (Imported from VUDDY and ReDeBug.)
    # ref: https://github.com/squizz617/vuddy
    c_regex = re.compile(
        r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)',
        re.DOTALL | re.MULTILINE)
    return ''.join([c.group('noncomment') for c in c_regex.finditer(string) if c.group('noncomment')])

def normalize(string):
    # Code for normalizing the input string.
    # LF and TAB literals, curly braces, and spaces are removed,
    # and all characters are lowercased.
    # ref: https://github.com/squizz617/vuddy
    return ''.join(string.replace('\n', '').replace('\r', '').replace('\t', '').replace('{', '').replace('}', '').split(' ')).lower()

def hashing(repoPath):
    # This function is for hashing C/C++ functions
    # Only consider ".c", ".cc", and ".cpp" files
    possible = (".c", ".cc", ".cpp")

    fileCnt  = 0
    funcCnt  = 0
    lineCnt  = 0

    resDict  = {}

    for path, dir, files in os.walk(repoPath):
        for file in files:
            filePath = os.path.join(path, file)

            if file.endswith(possible):
                try:
                    # Execute Ctgas command
                    functionList 	= subprocess.check_output(ctagsPath + ' -f - --kinds-C=* --fields=neKSt "' + filePath + '"', stderr=subprocess.STDOUT, shell=True).decode()

                    f = open(filePath, 'r', encoding = "UTF-8")

                    # For parsing functions
                    lines 		= f.readlines()
                    allFuncs 	= str(functionList).split('\n')
                    func   		= re.compile(r'(function)')
                    number 		= re.compile(r'(\d+)')
                    funcSearch	= re.compile(r'{([\S\s]*)}')
                    tmpString	= ""
                    funcBody	= ""

                    fileCnt 	+= 1

                    for i in allFuncs:
                        elemList	= re.sub(r'[\t\s ]{2,}', '', i)
                        elemList 	= elemList.split('\t')
                        funcBody 	= ""

                        if i != '' and len(elemList) >= 8 and func.fullmatch(elemList[3]):
                            funcStartLine 	 = int(number.search(elemList[4]).group(0))
                            funcEndLine 	 = int(number.search(elemList[7]).group(0))

                            tmpString	= ""
                            tmpString	= tmpString.join(lines[funcStartLine - 1 : funcEndLine])

                            if funcSearch.search(tmpString):
                                funcBody = funcBody + funcSearch.search(tmpString).group(1)
                            else:
                                funcBody = " "

                            funcBody = removeComment(funcBody)
                            funcBody = normalize(funcBody)
                            funcHash = computeTlsh(funcBody)

                            if len(funcHash) == 72 and funcHash.startswith("T1"):
                                funcHash = funcHash[2:]
                            elif funcHash == "TNULL" or funcHash == "" or funcHash == "NULL":
                                continue

                            storedPath = filePath.replace(repoPath, "")
                            if funcHash not in resDict:
                                resDict[funcHash] = []
                            resDict[funcHash].append(storedPath)

                            lineCnt += len(lines)
                            funcCnt += 1

                except subprocess.CalledProcessError as e:
                    print("Parser Error:", e)
                    continue
                except Exception as e:
                    print ("Subprocess failed", e)
                    continue

    return resDict, fileCnt, funcCnt, lineCnt

def getAveFuncs():
    aveFuncs = {}
    with open(aveFuncPath, 'r', encoding = "UTF-8") as fp:
        aveFuncs = json.load(fp)
    return aveFuncs


def readComponentDB():
    componentDB = {}
    jsonLst 	= []

    for OSS in os.listdir(finalDBPath):
        try:
            componentDB[OSS] = []
            with open(finalDBPath + OSS, 'r', encoding = "UTF-8") as fp:
                jsonLst = json.load(fp)

                for eachHash in jsonLst:
                    hashval = eachHash["hash"]
                    componentDB[OSS].append(hashval)
        except Exception as e:
            # handle any other exceptions
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # 获取错误的行号
            line_number = exc_traceback.tb_lineno
            # 打印错误行号和异常信息
            print("Error at line1", line_number, ":", e)
    return componentDB

def readAllVers(repoName):
    allVerList 	= []
    idx2Ver		= {}

    with open(verIDXpath + repoName + "_idx", 'r', encoding = "UTF-8") as fp:
        tempVerList = json.load(fp)

        for eachVer in tempVerList:
            allVerList.append(eachVer["ver"])
            idx2Ver[eachVer["idx"]] = eachVer["ver"]

    return allVerList, idx2Ver

def readWeigts(repoName):
    weightDict = {}

    with open(weightPath + repoName + "_weights", 'r', encoding = "UTF-8") as fp:
        weightDict = json.load(fp)

    return weightDict
def read_tag_dates(repoName):
    file_path = datePath + repoName
    tag_dates = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split('(')
            if len(parts) > 1:
                date_str = parts[0].strip()
                tags = parts[1].replace(')','')
                tags = tags.split(', ')
                date_obj = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
                for tag_part in tags:
                    if 'tag' in tag_part:
                        tag = tag_part.strip().replace('tag:', '').strip()
                        if tag:
                            tag_dates[tag] = date_obj
    return tag_dates


# def read_tag_dates(repoName):
# 	file_path = datePath + repoName
# 	tag_dates = {}
#     with open(file_path, 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#         for line in lines:
#             parts = line.split('(tag:')
#             if len(parts) > 1:
#                 date_str = parts[0].strip()
#                 tags = parts[1].split(')')
#                 date_obj = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
#                 for tag_part in tags:
#                     tag = tag_part.strip().replace('tag:', '').strip()
#                     if tag:
#                         tag_dates[tag] = date_obj
#     return tag_dates

def detector(inputDict, inputRepo,componentDB):
    result_file_path = resultPath + "result_" + inputRepo
    if os.path.exists(result_file_path):
        print(f'{result_file_path} exist')
    else:
        fres = open(result_file_path, 'w', encoding='utf-8')
        # fres1 = open(resultPath + "result1_" + inputRepo, 'w')

        print('Creation completed')

        aveFuncs = getAveFuncs()
        cnt = 0
        keys_to_remove = []
        results = {}
        paths = {}
        for OSS in componentDB:
            commonFunc = []

            repoName = OSS[:-4]
            if repoName in aveFuncs:
                totOSSFuncs = float(aveFuncs[repoName])
            else:
                print('reponame:', repoName)
                continue
            if totOSSFuncs == 0.0:
                continue
            comOSSFuncs = 0.0
            for hashval in componentDB[OSS]:
                if hashval in inputDict:
                    commonFunc.append(hashval)
                    comOSSFuncs += 1.0

            if (comOSSFuncs > 5 and (comOSSFuncs / totOSSFuncs) >= theta1) or (
                    comOSSFuncs <= 5 and (comOSSFuncs / totOSSFuncs) >= theta3):
                if comOSSFuncs >= 3:
                    # if comOSSFuncs == totOSSFuncs:
                    if OSS not in results:
                        results[OSS] = []
                        paths[OSS] = []
                    results[OSS].extend(commonFunc)
            # else:
            #     if OSS not in results:
            #         results[OSS] = []
            #         paths[OSS] = []
            #     results[OSS].extend(commonFunc)
        # if (comOSSFuncs / totOSSFuncs) > theta1:
        #     if OSS not in results:
        #         results[OSS] = []
        #         paths[OSS] = []
        #     results[OSS].extend(commonFunc)

        inputRepo = inputRepo + '_sig'
        # print('results:',results.keys())
        for OSS in results:
            for hashFunction in results[OSS]:
                paths[OSS].append(str(inputDict[hashFunction]))
        # print('path:',paths)
        for OSS1 in paths:
            # print(f'OSS1 {OSS1}:',set(paths[OSS1]))
            OSS1_sig = OSS1.replace('_sig', '')
            if inputRepo != OSS1:
                for OSS2 in paths.keys():
                    # print(f'OSS2 {OSS2}:', set(paths[OSS2]))
                    OSS2_sig = OSS2.replace('_sig', '')
                    if inputRepo != OSS2 and OSS1 != OSS2:
                        if set(paths[OSS1]) == set(paths[OSS2]):

                            if len(results[OSS2]) < len(results[OSS1]):
                                keys_to_remove.append(OSS2)
                            # print('remove OSS2:', OSS2)  # 添加要删除的键到列表
                            else:
                                keys_to_remove.append(OSS1)
                            # print('remove OSS1:', OSS1)  # 添加要删除的键到列表

        for key in set(keys_to_remove):
            # print('remove:', key)
            if key in results:
                del results[key]
            else:
                print(f"Key '{key}' not found in the 'results' dictionary.")

        # result_file_path = os.path.join(resultPath, "result_" + inputRepo.replace('_sig',''))  # 使用os.path.join来构建文件路径
        # #print(result_file_path)
        # if os.path.exists(result_file_path):
        #     existing_oss = set()
        #     with open(result_file_path, 'r', encoding='utf-8') as existing_file:
        #         for line in existing_file:
        #             if line.startswith("OSS"):
        #                 existing_oss.add(line.strip().split("OSS: ")[1])
        # else:
        #     print('no')
        #     existing_oss = set()  # 如果文件不存在，初始化为空集合
        # #print(existing_oss)

        for OSS in results:
            try:
                print(OSS)
                # if OSS not in existing_oss:  # 如果OSS不在已存在的列表中，才写入文件
                verPredictDict 	= {}
                repoName = OSS[:-4]
                allVerList, idx2Ver = readAllVers(repoName)
                # print('allVerList:',allVerList,'idx2ver:',idx2Ver)

                for eachVersion in allVerList: #初始化预测版本
                    verPredictDict[eachVersion] = 0.0

                weightDict 		= readWeigts(repoName) #读取每个函数权重
                # print(weightDict)

                with open(initialDBPath + OSS, 'r', encoding = "UTF-8") as fi:
                    jsonLst = json.load(fi)
                    for eachHash in jsonLst:
                        hashval = eachHash["hash"]
                        verlist = eachHash["vers"] #verlist是因为函数被多个版本拥有，记录的是idx
                        # print('hashval:',hashval,'verlist:',verlist)

                        if hashval in results[OSS]:
                            # print('cunzai')
                            for addedVer in verlist:
                                # print('weight:',weightDict[hashval])
                                verPredictDict[idx2Ver[addedVer]] += weightDict[hashval] #给拥有这个函数的版本都加上这个函数的hash值

                min_score_difference = 0.1

                sortedByWeight = sorted(verPredictDict.items(), key=lambda x: x[1],
                                        reverse=True)  # items() 函数以列表返回可遍历的(键, 值) 元组数组。sorted() 函数对所有可迭代的对象进行排序操作
                # print('sortesByWeight:', sortedByWeight)
                # 比较每个版本的分数，选择分数差距较大的版本
                # 比较每个版本的分数，选择分数差距较大的版本
                # 获取 sortedByWeight[0][0] 的分数
                if sortedByWeight and sortedByWeight[0] or repoName == inputDict:
                    # print(sortedByWeight)
                    for version, score in sortedByWeight:
                        if version != '':
                            baseline_version, baseline_score = version, score
                            break


                    # 筛选出分数较小且比 baseline_score 小的版本，不包括 baseline_version
                    filtered_versions = [version for version, score in sortedByWeight if
                                         version != baseline_version and baseline_score - score < min_score_difference and version != '']
                    # print('filtered_versions:',filtered_versions)

                        # 获取每个版本的发布时间并比较

                    try:
                        selected_version = baseline_version
                        selected_date = None
                        latest_release_date = None
                        new_version = None
                        new_date = None

                        release_date = read_tag_dates(repoName)
                        if release_date:
                            # print(release_date)
                            new_version = list(release_date.keys())[0]
                            new_date = release_date[new_version]
                            if baseline_version in release_date:
                                latest_release_date = release_date[baseline_version]
                            # print('latest_release_date:',latest_release_date)
                            else:
                                latest_release_date = None

                        for version in filtered_versions:
                            try:
                                version = str(version)
                                # print('release_date[version]:',release_date[version])
                                if latest_release_date is None or (release_date[version] is not None and release_date[version] > latest_release_date):
                                    selected_version = version
                                    selected_date = release_date[version]
                                    latest_release_date = release_date[version]
                            except Exception as e:
                                # handle any other exceptions
                                # exc_type, exc_value, exc_traceback = sys.exc_info()
                                # # 获取错误的行号
                                # line_number = exc_traceback.tb_lineno
                                # # 打印错误行号和异常信息
                                # print("Error at line2", line_number, ":", e)
                                continue
                    except Exception as e:
                        # handle any other exceptions
                        # exc_type, exc_value, exc_traceback = sys.exc_info()
                        # # 获取错误的行号
                        # line_number = exc_traceback.tb_lineno
                        # # 打印错误行号和异常信息
                        # print("Error at line3", line_number, ":", e)
                        continue

                    predictedVer = selected_version
                    print('new_date:',new_date)

                    print('selected_version:',selected_version)
                    if new_date is not None and selected_date is not None:
                        time_diff = (new_date - selected_date).total_seconds()
                    else:
                        new_version = predictedVer
                        time_diff = 0.0

                else:
                    predictedVer = 'master'
                    new_version = predictedVer
                    time_diff = 0.0

                print("Predicted Version:", str(predictedVer))
                fres.write('\t'.join([inputRepo, repoName, str(predictedVer),str(new_version),str(time_diff)]) + '\n')
            except Exception as e:
                # handle any other exceptions
                # exc_type, exc_value, exc_traceback = sys.exc_info()
                # # 获取错误的行号
                # line_number = exc_traceback.tb_lineno
                # # 打印错误行号和异常信息
                # print("Error at line3", line_number, ":", e)
                continue
        fres.close()


def main(inputPath, inputRepo, componentDB, testmode):
    if testmode == 1:
        inputDict = {}
        with open(inputPath, 'r', encoding="UTF-8") as fp:
            body = ''.join(fp.readlines()).strip()
            for eachLine in body.split('\n')[1:]:
                hashVal = eachLine.split('\t')[0]
                hashPat = eachLine.split('\t')[1]
                inputDict[hashVal] = hashPat
    else:
        inputDict, fileCnt, funcCnt, lineCnt = hashing(inputPath)
        print('hash完成')

    detector(inputDict, inputRepo, componentDB)


""" EXECUTE """
if __name__ == "__main__":

    # testmode = 1
    #
    # if testmode:
    # 	inputPath = currentPath + "/crown"
    # else:
    # 	inputPath = sys.argv[1] #输入目标软件路径
    #
    # inputRepo = inputPath.split('/')[-1]
    #
    # main(inputPath, inputRepo)
    sys.stdout = Logger(f'./{log}.log', sys.stdout)
    sys.stderr = Logger(f'./{log}.log', sys.stderr)
    start_time = time.time()
    componentDB = readComponentDB()
    print('Read DB complete')

    testmode = 1
    #
    # if testmode:
    # 	inputPath = currentPath + "/fuzzy_4.7.0.hidx"
    # 	inputRepo = "fuzzy_4.7.0"
    # 	inputPath1 = currentPath + "/fuzzy_xenia-project@@xenia.hidx"
    # 	inputRepo1 = "fuzzy_xenia-project@@xenia"
    # else:
    OSSList = os.listdir(datasetPath)
    for repo in reversed(OSSList):
    # for repo in ['ioquake@@ioq3_fuzzy_.hidx']:
        try:
            inputPath = os.path.join(datasetPath, repo)
            inputRepo = repo.split('_fuzzy')[0]
            print('----------------------------------------------')
            print('repo:', inputRepo)

            main(inputPath, inputRepo, componentDB, testmode)
        except Exception as e:
            # handle any other exceptions
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # # 获取错误的行号
            # line_number = exc_traceback.tb_lineno
            # # 打印错误行号和异常信息
            # print("Error at line4", line_number, ":", e)
            continue

    end_time = time.time()
    run_time = end_time - start_time

    print(run_time)


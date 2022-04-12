#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from functools import cmp_to_key
from DictNovel import noveldict, cmp   #小说标签
from DictText import textdict          #正文关键词
from DictRace import racedict          #种族关键词
from FileOperate import findFile, openText, openText4, openDocx, openDocx4, monthNow, openNowDir
from config import cc1, cc2


def set2Text(set):
	text = str(set)
	text = text.replace("{", "")
	text = text.replace("}", "")
	text = text.replace("'", "")
	text = text.replace(",", "")
	return text


def sortTags(set, cmp):  # 按dict内顺序对转换后的标签排序
	text = ""
	li = list(set)
	li.sort(key=cmp_to_key(cmp))
	
	for i in range(len(li)):
		taglist = li[i].split()    # 一关键词匹配多标签
		for j in range(len(taglist)):
			tag = taglist[j]
			# print(tag)
			text += "#{} ".format(tag)
	return text


def addTags(text):  # 添加语言标签
	tags = ""
	list1 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	list2 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list3 = "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん ぁ ぃ ぅ ぇ ぉ".split(" ")
	list4 = "a b c d e f g h I j k l m n o p q r s t u v w x y z".split(" ")
	
	def countChar(list):
		j = 0
		for i in range(len(list)):
			char = list[i]
			num = text.count(char)
			if num >= 5:
				j += 1
		return j
	
	tags += " #txt #finished "
	if   countChar(list4) >= 0.4 * len(list4):
		tags += "#en"
	elif countChar(list3) >= 0.2 * len(list3):
		tags += "#ja"
	elif countChar(list2) >= 0.2 * len(list2):
		tags += "#zh_tw"
	elif countChar(list1) >= 0.2 * len(list1):
		tags += "#zh_cn"
	# print(tags)
	return tags


def translateTags(taglist):  # 获取英文标签
	tags2 = ""; s = set()
	for i in range(0, len(taglist)):
		tag = taglist[i]
		tag = tag.replace("#", "")
		tag = tag.replace(" ", "")
		tag = tag.replace("　", "")
		tag = noveldict.get(tag)  # 获取英文标签
		
		if tag != None:
			s.add(tag)  # 获取到的标签利用set去重
		else:
			tag = taglist[i]
			tags2 += tag + " "
	return s, tags2


def getTags(text):  # 获取可能存在的标签
	# 引入总字数作基数的话，如何避免无法获得剧情向小说色情标签？
	# 优势，色情标签过少可以添加 #剧情向标签
	
	s1 = set() ; s2 = set()
	list1 = list(textdict.keys())
	list2 = list(textdict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if num > 5:  # 数据未测试
			s1.add(list1[i])  # 汉字标签
			s2.add(list2[i])  # 英文标签
	return s2, s1  # 英文标签在前


def getRaceTags(text):  # 获取可能存在的标签
	s1 = set(); s2 = set()
	textnum = len(text)
	list1 = list(racedict.keys())
	list2 = list(racedict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if 10000 * num / textnum > 15:  #神奇的数据
			s1.add(list1[i])  # 汉字标签
			s2.add(list2[i])  # 英文标签
	return s2, s1  # 英文标签在前


def setSpilt(s):
	s = set2Text(s)
	s = s.split(" ")  # 允许一关键词对多标签，并拆分成处理
	s = set(s)
	return s


def getInfo(text, textlist):
	name = textlist[0]
	authro = textlist[1].replace("作者：", "")
	authro = "by #" + authro
	
	url = textlist[2].replace("网址：", "")
	url = url.replace("網址：", "")
	url = url.replace("链接：", "")
	# url = url + "\n"
	
	tags = textlist[3].replace("标签：", "")
	tags = tags.replace("標簽：", "")
	tags += addTags(text)  # 新增 #zh_tw 或 #zh_cn
	tags = cc1.convert(tags)  # 转简体，只处理简体标签
	list = tags.split()
	(tags1, tags2) = translateTags(list)  # 获取已翻译/未翻译的标签
	
	if "#zh_cn" in tags:
		name = cc2.convert(textlist[0])
	elif "#zh_tw" in tags:
		name = cc1.convert(textlist[0])
	
	text = cc1.convert(text)  # 按照简体文本处理关键词获取对应标签
	(unsure1, unsure2) = getRaceTags(text)
	(unsure3, unsure4) = getTags(text)
	s1 = unsure1.union(unsure3)
	s2 = unsure2.union(unsure4)
	
	unsuretag = ""
	if s1 != set():
		s1 = setSpilt(s1)
		tags1 = setSpilt(tags1)    # 拆分一关键词对多个标签
		s1 = s1.difference(tags1)  # 去重，获取作者未标注的标签
		s1 = sortTags(s1, cmp)
		s2 = sortTags(s2, cmp)
		unsuretag = "可能存在：" + s1 +"\n"+ s2
	
	tags1 = sortTags(tags1, cmp)
	if tags2 != "":
		tags2 = "特殊：{}\n".format(tags2)
	info = "{}{}{}\n{}{}\n{}".format(name, authro, tags1, tags2, unsuretag, url)
	return info


def printInfo(path):
	(dir, name) = os.path.split(path)
	(name, ext) = os.path.splitext(name)
	if ext == ".docx":
		textlist = openDocx4(path)
		text = openDocx(path)
	elif ext == ".txt":
		textlist = openText4(path)
		text = openText(path)
	
	if len(textlist) >= 4:
		info = getInfo(text, textlist)
	else:
		info = "【{}】未处理".format(name)
	
	print(info)
	return info


def getPath(path):
	j = 0
	dirstr = monthNow()  # 只处理本月的文件
	pathlist = findFile(path, ".docx", ".txt")
	for i in range(0, len(pathlist)):
		filepath = pathlist[i]
		if dirstr in filepath:
			j += 1
			printInfo(filepath)
	if j != 0:
		# openNowDir()
	# text = set2Text(s)
	# saveTextDesktop("tags.txt", text)
	# saveTextDesktop("文字.txt", chars)
		pass
	else:
		print("本月 " + dirstr + " 无新文档")


def main():
	print("本月文档如下：")
	print("\n")
	getPath(path)


if __name__ == "__main__":
	path = os.path.join(os.getcwd())
	path = path.replace("\工具", "")
	pathlist = []
	main()

#!/usr/bin/env python
#coding=utf-8
import json
import re
import os
import sys

#定义标准答案的格式,名字+手机+七级地址
class Result:
    name = ""
    phone = ""
    province = ""#直辖市/省(省级)
    city = ""#直辖市/市(地级)
    area = ""#区/县/县级市(县级)
    town = ""#街道/镇/乡(乡镇级)
    street = ""#路名
    number = ""#门牌号
    building = ""#详细地址
result = Result()
#用于输出的json
data={
    "姓名":"",
    "手机":"",
    "地址":[]
    }
jsondata = {}
filepath = os.path.split(os.path.realpath(__file__))[0]
filepath = filepath + "\\" + "pcas-code.json"
with open(filepath,"r+",encoding='utf-8_sig')as f:
    jsondata = json.load(f)#将已编码JSON字符串解码为Python字典
    
#获取电话
def getphone(s):
    pattern = re.compile(r'1\d{10}')
    match = pattern.search(s)
    try:
        phone = match.group(0)
    except AttributeError:
        print("输入的手机号格式不正确")
    return phone
#去除混杂在中间的电话,获取混合的地址
def getaddress(s,phone):
    addressList=s.split(phone)
    address=""
    address=address.join(addressList)
    address=address[:-1]#切片去除句点
    return address
#去除字符串头部指定的子串
def cutdown(origin,child):
    limit=len(child)
    i = 0
    while i < limit:
        if origin[i] != child[i]:
            break
        i = i + 1
    return origin[i:]
    
def segementFive(address):

    #直辖市/省(省级)
    match=address[:2]
    #print("匹配",match)
    for itemProvince in jsondata:
        if re.search(match,itemProvince["name"]):
            result.province = itemProvince["name"]
            cityList = itemProvince
            #print(result.province)
            address=cutdown(address,result.province)#混合地址去除省份

            #判断第一级是否为直辖市,若是,添加回字符串(第二级用
            for direct in ["北京","上海","天津","重庆"]:
                if direct == result.province:
                    address = result.province + address
            
            break
    if result.province == "":#目前台湾暂时没有数据
        return 
    #-------------------------------------------------------------------------        
    #直辖市/市(地级)
    flagCity=0#默认没有查找到
    match=address[:2]
    for itemCity in cityList["children"]:  
        if re.search(match,itemCity["name"]):
            flagCity=1
            result.city = itemCity["name"]
            #print(result.city)
            
            address = cutdown(address,result.city)
            areaList = itemCity
            break

    #-------------------------------------------------------------------------
    #区/县/县级市(县级)
    match=address[:2]
    flagArea=0
    if(flagCity==1):
        for itemArea in areaList["children"]:
            if re.search(match,itemArea["name"]):
                flagArea=1
                result.area=itemArea["name"]
                #print(result.area)
            
                address=cutdown(address,result.area)
                townList=itemArea
                break
    else:#处理市级缺失情况下的县级查找
        for itemCity in cityList["children"]:
            for itemArea in itemCity["children"]:
                if re.search(match,itemArea["name"]):
                    result.area=itemArea["name"]
                    #print(result.area)
                    address = cutdown(address,result.area)
                    townList=itemArea
                    flagArea=1
                    break
            else:
                continue
            break

    #---------------------------------------------------------------------
    #街道/镇/乡(乡镇级)
    match=address[:2]
    if (flagArea==1):
        for itemTown in townList["children"]:
            if re.search(match,itemTown["name"]):
                result.town = itemTown["name"]
                #print(result.town)
                address=cutdown(address,result.town)
                break
    else:#处理县级缺失情况下的乡镇级查找
        for itemArea in areaList["children"]:
            for itemTown in itemArea["children"]:
                if re.search(match,itemTown['name']):
                    result.town=itemTown["name"]
                    #print(result.town)
                    address=cutdown(address,result.town)
                    break
            else:
                continue
            break
    #---------------------------------------------------------------------
    result.street=address#在五级地址中使用street作为详细地址
    
def segementSeven(detail):    
    address=detail
    pattern=re.compile(r'(.*?[街])|(.*?[道])|(.*?[路])|(.*?[巷])|(.*?[大街])|(.*?[街道])')
    #pattern= re.compile(r'.+(路|街|巷|桥|道){1}')
    match = pattern.search(address)
    if(match):
        result.street = match.group(0)
    else:#可能存在缺失街道
        result.street = ""
    #print(result.street)
    address = cutdown(address,result.street)
    
    pattern=re.compile(r'(.*?[号])')
    #pattern = re.compile(r'.+(号){1}')
    match = pattern.search(address)
    if(match):
        result.number = match.group(0)
    else:#可能存在缺失门牌号
        result.number = ""
    #print(result.number)
    address = cutdown(address,result.number)
    result.building = address
    #print(result.building)

def enhancement(address):
    
    #直辖市/省(省级)
    match=address[:2]
    #print("匹配",match)
    flagProvince=0#默认省级没有找到
    for itemProvince in jsondata:
        if re.search(match,itemProvince["name"]):
            flagProvince=1
            result.province = itemProvince["name"]
            cityList = itemProvince
            address=cutdown(address,result.province)#混合地址去除省份

            #判断第一级是否为直辖市,若是,添加回字符串(第二级用
            for direct in ["北京","上海","天津","重庆"]:
                if direct == result.province:
                    address = result.province + address
            
            break
    
    #-------------------------------------------------------------------------        
    #直辖市/市(地级)
    flagCity=0#默认没有查找到
    match=address[:2]
    if(flagProvince==1):
        for itemCity in cityList["children"]:  
            if re.search(match,itemCity["name"]):
                flagCity=1
                result.city = itemCity["name"]
                address = cutdown(address,result.city)
                areaList = itemCity
                break
    else:#处理省级缺失情况下的市级查找
        for itemProvince in jsondata:
            for itemCity in itemProvince["children"]:
                if re.search(match,itemCity["name"]):
                    flagCity=1
                    flagProvince=1
                    result.province=itemProvince["name"]
                    result.city=itemCity["name"]
                    address=cutdown(address,result.city)
                    areaList=itemCity
    #-------------------------------------------------------------------------
    #区/县/县级市(县级)
    match=address[:2]
    flagArea=0
    if(flagCity==1):
        for itemArea in areaList["children"]:
            if re.search(match,itemArea["name"]):
                flagArea=1
                result.area=itemArea["name"]
                address=cutdown(address,result.area)
                townList=itemArea
                break
    elif(flagCity==0 and flagProvince==1):#处理省级不缺失但是市级缺失情况下的县级查找
        for itemCity in cityList["children"]:
            for itemArea in itemCity["children"]:
                if re.search(match,itemArea["name"]):
                    flagCity=1
                    flagArea=1
                    result.city=itemCity["name"]
                    result.area=itemArea["name"]
                    address = cutdown(address,result.area)
                    townList=itemArea
                    break
            else:
                continue
            break
    else:#(flagCity==0 and flagProvince==0):#处理省级缺失并且市级缺失情况下的县级查找
        for itemProvince in jsondata:
            for itemCity in itemProvince["children"]:
                for itemArea in itemCity["children"]:
                    if re.search(match,itemArea["name"]):
                        flagProvince=1
                        flagCity=1
                        flagArea=1
                        result.province=itemProvince["name"]
                        result.city=itemCity["name"]
                        result.area=itemArea["name"]
                        address=cutdown(address,result.area)
                        townList=itemArea
                        break
                else:
                    continue
                break
            if(flagProvince==1):
                break
    #---------------------------------------------------------------------
    #街道/镇/乡(乡镇级)
    match=address[:2]
    flagTown=0#默认没有查找到
    if (flagArea==1):
        for itemTown in townList["children"]:
            if re.search(match,itemTown["name"]):
                result.town = itemTown["name"]
                #print(result.town)
                address=cutdown(address,result.town)
                break
    elif(flagArea==0 and flagCity==1):#处理市级不缺失但县级缺失情况下的乡镇级查找
        for itemArea in areaList["children"]:
            for itemTown in itemArea["children"]:
                if re.search(match,itemTown['name']):
                    result.area=itemArea["name"]
                    result.town=itemTown["name"]
                    #print(result.town)
                    address=cutdown(address,result.town)
                    break
            else:
                continue
            break
    else:#(flagArea==0 and flagCity==0)处理市级缺失并且县级缺失情况下的乡镇级查找
        for itemCity in cityList["children"]:
            for itemArea in itemCity["children"]:
                for itemTown in itemArea["children"]:
                    if re.search(match,itemTown["name"]):
                        flagCity=1
                        flagArea=1
                        flagTown=1
                        result.city=itemCity["name"]
                        result.area=itemArea["name"]
                        result.town=itemTown["name"]
                        address=cutdown(address,result.town)
                        break
                else:
                    continue
                break
            if(flagCity==1):
                break
    #---------------------------------------------------------------------
    pattern=re.compile(r'(.*?[街])|(.*?[道])|(.*?[路])|(.*?[巷])|(.*?[大街])|(.*?[街道])')
    #pattern= re.compile(r'.+(路|街|巷|桥|道){1}')
    match = pattern.search(address)
    if(match):
        result.street = match.group(0)
    else:#可能存在缺失街道
        result.street = ""
    #print(result.street)
    address = cutdown(address,result.street)
    
    pattern=re.compile(r'(.*?[号])')
    #pattern = re.compile(r'.+(号){1}')
    match = pattern.search(address)
    if(match):
        result.number = match.group(0)
    else:#可能存在缺失门牌号
        result.number = ""
    #print(result.number)
    address = cutdown(address,result.number)
    result.building = address
    #print(result.building)
def formatFive():
    data["姓名"]=result.name
    data["手机"]=result.phone
    data["地址"].append(result.province)
    data["地址"].append(result.city)
    data["地址"].append(result.area)
    data["地址"].append(result.town)
    data["地址"].append(result.street)
    

def formatSeven():
    formatFive()
    data["地址"].append(result.number)
    data["地址"].append(result.building)
def solution(source):
	
    s = ""
    s=source
    level = s.split("!")[0]#获取本条输入的难度
    level=eval(level)
    #print(level)

    s=s.split("!")[1]#原始输入去掉"难度!"
    result.name = s.split(",")[0]#获取姓名
    #print(result.name)

    s=s.split(",")[1]#原始输入剩余电话与地址
    phonenumber = getphone(s)#获取电话
   
    #print(phonenumber)

    result.phone = phonenumber
    address=getaddress(s,phonenumber)#address为初步的混合地址
    #print(address)
    
    if level==1:
        segementFive(address)
        formatFive()
    elif level==2:
        segementFive(address)
        segementSeven(result.street)
        formatSeven()
    else:
        enhancement(address)
        formatSeven()
    jsonresult=json.dumps(data,ensure_ascii=False)
    print(jsonresult)
    
def main():
    while 1:
        try:
            inputraw=input();
            if(inputraw=="END"):
                break
        except EOFError:
            break
        solution(inputraw)

main()


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
    
def segementFive(add,res,jd):

    #直辖市/省(省级)
    match=add[:2]
    #print("匹配",match)
    for itemProvince in jd:
        if re.search(match,itemProvince["name"]):
            res.province = itemProvince["name"]
            cityList = itemProvince
            #print(res.province)
            add=cutdown(add,res.province)#混合地址去除省份

            #判断第一级是否为直辖市,若是,添加回字符串(第二级用
            for direct in ["北京","上海","天津","重庆"]:
                if direct == res.province:
                    add = res.province + add
            
            break
    #-------------------------------------------------------------------------        
    #直辖市/市(地级)
    flagCity=0#默认没有查找到
    match=add[:2]
    for itemCity in cityList["children"]:  
        if re.search(match,itemCity["name"]):
            flagCity=1
            res.city = itemCity["name"]
            #print(res.city)
            
            add = cutdown(add,res.city)
            areaList = itemCity
            break

    #-------------------------------------------------------------------------
    #区/县/县级市(县级)
    match=add[:2]
    flagArea=0
    if(flagCity==1):
        for itemArea in areaList["children"]:
            if re.search(match,itemArea["name"]):
                flagArea=1
                res.area=itemArea["name"]
                #print(res.area)
            
                add=cutdown(add,res.area)
                townList=itemArea
                break
    else:#处理市级缺失情况下的县级查找
        for itemCity in cityList["children"]:
            for itemArea in itemCity["children"]:
                if re.search(match,itemArea["name"]):
                    res.area=itemArea["name"]
                    #print(res.area)
                    add = cutdown(add,res.area)
                    townList=itemArea
                    flagArea=1
                    break
            else:
                continue
            break

    #---------------------------------------------------------------------
    #街道/镇/乡(乡镇级)
    match=add[:2]
    if (flagArea==1):
        for itemTown in townList["children"]:
            if re.search(match,itemTown["name"]):
                res.town = itemTown["name"]
                #print(res.town)
                add=cutdown(add,res.town)
                break
    else:#处理县级缺失情况下的乡镇级查找
        for itemArea in areaList["children"]:
            for itemTown in itemArea["children"]:
                if re.search(match,itemTown['name']):
                    res.town=itemTown["name"]
                    #print(res.town)
                    add=cutdown(add,res.town)
                    break
            else:
                continue
            break
    #---------------------------------------------------------------------
    res.street=add#在五级地址中使用street作为详细地址
    
def segementSeven(detail,res):    
    add=detail
    pattern=re.compile(r'(.*?[街])|(.*?[道])|(.*?[路])|(.*?[巷])|(.*?[大街])|(.*?[街道])|(.*?[委会])')
    #pattern= re.compile(r'.+(路|街|巷|桥|道){1}')
    match = pattern.search(add)
    if(match):
        res.street = match.group(0)
    else:#可能存在缺失街道
        res.street = ""
    #print(res.street)
    add = cutdown(add,res.street)
    
    pattern=re.compile(r'(.*?[号])')
    #pattern = re.compile(r'.+(号){1}')
    match = pattern.search(add)
    if(match):
        res.number = match.group(0)
    else:#可能存在缺失门牌号
        res.number = ""
    #print(res.number)
    add = cutdown(add,res.number)
    res.building = add
    #print(res.building)

def enhancement(add,res,jd):
    
    #直辖市/省(省级)
    match=add[:2]
    #print("匹配",match)
    flagProvince=0#默认省级没有找到
    for itemProvince in jd:
        if re.search(match,itemProvince["name"]):
            flagProvince=1
            res.province = itemProvince["name"]
            cityList = itemProvince
            add=cutdown(add,res.province)#混合地址去除省份

            #判断第一级是否为直辖市,若是,添加回字符串(第二级用
            for direct in ["北京","上海","天津","重庆"]:
                if direct == res.province:
                    add = res.province + add
            break
    
    #-------------------------------------------------------------------------        
    #直辖市/市(地级)
    flagCity=0#默认没有查找到
    match=add[:2]
    if(flagProvince==1):
        for itemCity in cityList["children"]:  
            if re.search(match,itemCity["name"]):
                flagCity=1
                res.city = itemCity["name"]
                add = cutdown(add,res.city)
                areaList = itemCity
                break
    else:#处理省级缺失情况下的市级查找
        for itemProvince in jd:
            for itemCity in itemProvince["children"]:
                if re.search(match,itemCity["name"]):
                    flagCity=1
                    flagProvince=1
                    res.province=itemProvince["name"]
                    res.city=itemCity["name"]
                    add=cutdown(add,res.city)
                    areaList=itemCity
    #-------------------------------------------------------------------------
    #区/县/县级市(县级)
    match=add[:2]
    flagArea=0
    if(flagCity==1):
        for itemArea in areaList["children"]:
            if re.search(match,itemArea["name"]):
                flagArea=1
                res.area=itemArea["name"]
                add=cutdown(add,res.area)
                townList=itemArea
                break
    elif(flagCity==0 and flagProvince==1):#处理省级不缺失但是市级缺失情况下的县级查找
        for itemCity in cityList["children"]:
            for itemArea in itemCity["children"]:
                if re.search(match,itemArea["name"]):
                    flagCity=1
                    flagArea=1
                    res.city=itemCity["name"]
                    res.area=itemArea["name"]
                    add = cutdown(add,res.area)
                    townList=itemArea
                    break
            else:
                continue
            break
    else:#(flagCity==0 and flagProvince==0):#处理省级缺失并且市级缺失情况下的县级查找
        for itemProvince in jd:
            for itemCity in itemProvince["children"]:
                for itemArea in itemCity["children"]:
                    if re.search(match,itemArea["name"]):
                        flagProvince=1
                        flagCity=1
                        flagArea=1
                        res.province=itemProvince["name"]
                        res.city=itemCity["name"]
                        res.area=itemArea["name"]
                        add=cutdown(add,res.area)
                        townList=itemArea
                        break
                else:
                    continue
                break
            if(flagProvince==1):
                break
    #---------------------------------------------------------------------
    #街道/镇/乡(乡镇级)
    match=add[:2]
    if (flagArea==1):
        for itemTown in townList["children"]:
            if re.search(match,itemTown["name"]):
                res.town = itemTown["name"]
                #print(res.town)
                add=cutdown(add,res.town)
                break
    elif(flagArea==0 and flagCity==1):#处理市级不缺失但县级缺失情况下的乡镇级查找
        for itemArea in areaList["children"]:
            for itemTown in itemArea["children"]:
                if re.search(match,itemTown['name']):
                    res.area=itemArea["name"]
                    res.town=itemTown["name"]
                    #print(res.town)
                    add=cutdown(add,res.town)
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
                        res.city=itemCity["name"]
                        res.area=itemArea["name"]
                        res.town=itemTown["name"]
                        add=cutdown(add,res.town)
                        break
                else:
                    continue
                break
            if(flagCity==1):
                break
    #---------------------------------------------------------------------
    pattern=re.compile(r'(.*?[街])|(.*?[道])|(.*?[路])|(.*?[巷])|(.*?[大街])|(.*?[街道])')
    #pattern= re.compile(r'.+(路|街|巷|桥|道){1}')
    match = pattern.search(add)
    if(match):
        res.street = match.group(0)
    else:#可能存在缺失街道
        res.street = ""
    #print(res.street)
    add = cutdown(add,res.street)
    
    pattern=re.compile(r'(.*?[号])')
    #pattern = re.compile(r'.+(号){1}')
    match = pattern.search(add)
    if(match):
        res.number = match.group(0)
    else:#可能存在缺失门牌号
        res.number = ""
    add = cutdown(add,res.number)
    res.building = add

def formatFive(res,dat):
    dat["姓名"]=res.name
    dat["手机"]=res.phone
    dat["地址"].append(res.province)
    dat["地址"].append(res.city)
    dat["地址"].append(res.area)
    dat["地址"].append(res.town)
    dat["地址"].append(res.street)

def formatSeven(res,dat):
    dat["姓名"]=res.name
    dat["手机"]=res.phone
    dat["地址"].append(res.province)
    dat["地址"].append(res.city)
    dat["地址"].append(res.area)
    dat["地址"].append(res.town)
    dat["地址"].append(res.street)
    dat["地址"].append(res.number)
    dat["地址"].append(res.building)
def solution(sourceStr,JD):#参数是原始字符串和js数据表
    #用于输出的json
    data={
        "姓名":"",
        "手机":"",
        "地址":[]
    }
    result = Result()#实例化结论格式
    s = ""
    s=sourceStr
    level = s.split("!")[0]#获取本条输入的难度
    level=eval(level)

    s=s.split("!")[1]#原始输入去掉"难度!"
    result.name = s.split(",")[0]#获取姓名

    s=s.split(",")[1]#原始输入剩余电话与地址
    phonenumber = getphone(s)#获取电话

    result.phone = phonenumber
    address=getaddress(s,phonenumber)#address为初步的混合地址
    
    if level==1:
        segementFive(address,result,JD)
        formatFive(result,data)
    elif level==2:
        segementFive(address,result,JD)
        segementSeven(result.street,result)
        formatSeven(result,data)
    else:
        enhancement(address,result,JD)
        formatSeven(result,data)
    jsonresult=json.dumps(data,ensure_ascii=False)
    print(jsonresult)
    
def main():
    jsondata = {}
    filepath = os.path.split(os.path.realpath(__file__))[0]
    filepath = filepath + "\\" + "pcas-code.json"
    with open(filepath,"r+",encoding='utf-8_sig')as f:
        jsondata = json.load(f)#将已编码JSON字符串解码为Python字典
    while 1:
        try:
            inputraw=input();
            if(inputraw=="END"):
                break
        except EOFError:
            break
        solution(inputraw,jsondata)
main()

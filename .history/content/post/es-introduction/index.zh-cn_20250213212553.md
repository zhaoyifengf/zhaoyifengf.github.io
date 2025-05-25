---
title: "ES Introduction"
description: 
slug: ES-introduction
date: 2025-02-10T22:34:00+08:00
image: cover.png
categories:
    - Kafka
tags:
    - Elasticsearch
weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## 利用倒排索引加速查询符合条件的文本

### 利用倒排索引加速查询
对于若干段文本，例如：1: "I hava an orange"，2: "I hava a banana"，3:  "I hava an apple"，想要查询"苹果"在哪条记录里需要便利所有文体，时间复杂度为O(n)。将文本进行切分，以切分后的文本作为键，文本ID作为值构成一个二维表格，这样可以大大降低查询时间。

| term | 文本id |
|--|--|
| I | 1、2、3 |
| have | 1、2、3 |
| an | 1、3 |
| a | 2 |
| orange | 1 |
| banana | 2 |
| apple | 3 |

但当词项增多，遍历这些词项仍需花费大量时间，对词项进行倒排并进行二分查找可将时间复杂度降低到O(logN)。

| Term  dictionary | Posting list |
|--|--|
| a | 2 |
| an | 1、3 |
| apple | 3 |
| banana | 2 |
| have | 1、2、3 |
| I | 1、2、3 |
| orange | 1 |

将排好的词项称为Term  dictionary，文档ID称为Posting list，构成的搜索结构称为inverted index（倒排索引）。

### 利用目录树进一步加速查询
将文本进行分词后得到的Term  dictionary数据量巨大，只能通过磁盘检索。检索磁盘耗时较长，基于Term  dictionary构建一颗字典树并将字段树放入内存将极大加速索引销量。

{"changeCode":"测试数据","opptyCode":"测试数据","customerAccountId":"测试数据","beforeOwner":"测试数据","beforeOwnerName":"测试数据","afterOwner":"测试数据","afterOwnerName":"测试数据","beforeOpptyStatus":0,"afterOpptyStatus":0,"beforeDeptId":0,"afterDeptId":0,"updateUser":"测试数据","updateUserName":"测试数据","deptId":0,"leadsCode":"测试数据","firstSource":"测试数据","firstSourceName":"测试数据","owner":"测试数据","ownerName":"测试数据","ownerDeptId":0,"ownerDeptName":"测试数据","opptyStatusCategory":0,"opptyStatus":0,"priority":0,"firstAssignTime":"2025-02-13T00:00:00+00:00","reopenFirstAssignTime":"2025-02-13T00:00:00+00:00","assignTime":"2025-02-13T00:00:00+00:00","firstAssignCategory":0,"assignCategory":0,"issueStoreTime":"2025-02-13T00:00:00+00:00","firstFollowUpTime":"2025-02-13T00:00:00+00:00","lastFollowUpTime":"2025-02-13T00:00:00+00:00","lastFollowUpContent":"测试数据","lastFollowUpUser":"测试数据","lastFollowUpUserName":"测试数据","lastFollowUpStatus":0,"intentionLevel":0,"closeTime":"2025-02-13T00:00:00+00:00","closeLostReason":"测试数据","createTime":"2025-02-13T00:00:00+00:00","createUser":"测试数据","createUserName":"测试数据","isDelete":0,"closeLostKey":0,"effective":0,"customerName":"测试数据","customerNameHash":"测试数据","customerPhone":"测试数据","customerPhoneHash":"测试数据","placeCityCode":"测试数据","placeCityName":"测试数据","phoneProvinceCode":"测试数据","phoneProvinceName":"测试数据","phoneCityCode":"测试数据","phoneCityName":"测试数据","placeProvinceCode":"测试数据","placeProvinceName":"测试数据","score":0,"lockRate":0,"placeCountyCode":"测试数据","placeCountyName":"测试数据","isRecycle":0,"recycleTime":"2025-02-13T00:00:00+00:00","lastOwner":"测试数据","lastAssignTime":"2025-02-13T00:00:00+00:00","recycleReasonCode":0,"rejectTime":"2025-02-13T00:00:00+00:00","isRestart":"1","beforeFocusOnCar":"测试数据","afterFocusOnCar":"测试数据","beforeAlternativeCar":"测试数据","afterAlternativeCar":"测试数据"}
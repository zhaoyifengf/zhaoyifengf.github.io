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
对于若干段文本，例如：1: "I hava an orange"，2: "I hava a banana"，3:  "I hava an apple"，想要查询"apple"在哪条记录里需要遍历所有文体，时间复杂度为O(n)。将文本进行切分，以切分后的文本作为键，文本ID作为值构成一个二维表格，这样可以大大降低查询时间。

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

### 利用Term index进一步加速查询
将文本进行分词后得到的Term  dictionary数据量巨大，只能通过磁盘检索。检索磁盘耗时较长，基于Term  dictionary构建一颗字典树（Term index）并将字段树放入内存将极大加速索引效率。

  ![](term_index.png)

### 利用Store Fileds存储文档

  ![](store_fileds.png)

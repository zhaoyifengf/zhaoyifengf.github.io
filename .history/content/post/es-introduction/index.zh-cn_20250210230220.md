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
对于若干段文本，例如：1: "我有一个苹果"，2: "我有一个香蕉"，3: "我有一个橘子"，想要查询"苹果"在哪条记录里需要便利所有文体，时间复杂度为O(n)。将文本进行切分，以切分后的文本作为键，文本ID作为值构成一个倒排索引，这样可以大大降低查询时间。

| 文件夹 | 作用 |
|--|--|
| 我 | 1、2、3 |
| 有 | 1、2、3 |
| 一个 | 1、2、3 |
| 苹果 | 1 |
| 香蕉 | 2 |
| 橘子 | 3 |
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
对于若干段文本，例如："我有一个苹果"，"我有一个香蕉"，"我有一个橘子"，想要查询"苹果"在哪条记录里需要便利所有文体，时间复杂度为O(n)。将文本进行切分，以切分后的文本作为键，文本ID作为值构成一个倒排索引，这样可以大大降低查询时间。

		| 文件夹 | 作用 |
		|--|--|
		| hooks | 包含客户端或服务端的勾子脚本 |
		| info | 保护一个全局性排除文件 |
		| logs | 保存日志信息 |
		| objects | 存储所有数据内容 |
		| refs | 存储指向数据的提交对象的指针 |
		| config | 包含项目特有的配置选项 |
		| description | 用来显示对仓库的描述 |
		| HEAD | 指示目前被检出的分支 |
		| index | 保存暂存区信息 |
---
title: "Distribution Transaction"
description: 
slug: Distribution Transaction
date: 2025-02-10T22:34:00+08:00
image: cover.png
categories:
    - Transaction
tags:
    - Transaction
weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

### 分布式事务理论知识
#### CAP（Consistency、Availability、Availability）理论
CAP理论：在分布式系统，不会同时具备CAP三个特性，只能同时具备其中两个。

1. 一致性
   
    用户对数据的写操作在所有数据副本要么都成功、要么都失败。

2. 可用性
    
    客户端访问数据时能够快速得到响应。

3. 分区容忍性
   
   分区：分布式系统中不同节点间通信出现了问题。分区容忍：在出现分区时系统仍然能对外提供服务。
   
#### 为什么CAP只能满足其中两个


#### BASE理论
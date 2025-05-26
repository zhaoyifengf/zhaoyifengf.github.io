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
#### CAP（Consistency、Availability、Partition Tolerance）理论
CAP理论：在分布式系统，不会同时具备CAP三个特性，只能同时具备其中两个。

1. 一致性
   
    用户对数据的写操作在所有数据副本要么都成功、要么都失败。

2. 可用性
    
    客户端访问数据时能够快速得到响应。

3. 分区容忍性
   
   分区：分布式系统中不同节点间通信出现了问题。分区容忍：在出现分区时系统仍然能对外提供服务。
   
#### 为什么CAP只能满足其中两个

首先需要明确的是一个分布式系统必需要满足分区容错，也就是CAP中的P。在分布式系统中分区是一定会出现的，没有人能够保证节点与节点之间的网络总是不出问题，也没有人能够保证单个节点始终运行正常。如果一个分布式系统出现分区整个系统就停止服务，那其与单体服务并无区别（分布式系统的初衷就是通过多节点部署来提高系统的可用性）。

在出现分区的情况下，一致性与可用性只能满足其一：

1. 若要满足一致性，在对数据的多副本进行写入时需要锁定资源，而出现分区导致无法确认所有副本都写入成功，客户端的访问也无法在有效时间内得到响应。
   
2. 若要满足可可用性，对任意节点的访问都需要在指定时间得到响应，当被访问节点数据写入成功而存在节点数据未写入成功或者被访问节点数据未写入成功而其余节点数据写入成功则可用性也无法得到满足。

#### BASE理论
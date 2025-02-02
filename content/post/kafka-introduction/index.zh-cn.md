---
title: "Kafka Introduction"
description: 
slug: kafka-introduction
date: 2025-01-27T00:28:09+08:00
image: cover.png
categories:
    - Kafka
tags:
    - Introduction
weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## 一步步看Kfka

  ### 直接调用接口的弊端
  ![](direct-send-msg.svg)

  - 系统耦合度提升
  - 当生产者的生产速度大于消费者的消费速度时会导致消费者来不及处理导致消息丢失

  ### 消费者添加消息队列实现消息缓冲
  <img src="add-queue-to-consumer.svg" width="60%" height="60%">

  很容想到在消费者中提供一个消息队列缓冲没有能够及时处理的消息，通过offset记录已经处理的消息。但这样做仍然会存在以下问题：

  - 在消费者重启后消息会丢失
  - 每个消费者都维护一个消息队列存在着重复造轮子的问题
  - 生产者何消费者耦合的问题并没有解决

  ### 将消息队列独立成一个服务

  <img src="simple-msg-queue.svg" width="60%" height="60%">

  将消息队列抽成一个单独的服务使其可以服务于各个业务避免了重复造轮子的问题，实现了生产者和消费者之间的结偶，并且消息持久化、防止消息丢失的逻辑都可在一个服务中实现，独立于业务逻辑。在消息队列服务中我们需要实现高性能、高扩展。

  ### 实现消息队列的高性能展性

  #### 根据topic定义多消息队列

  <img src="multi-producer-consumer.svg" width="60%" heigh="60%">

  通过增加生产者和消费者可以增加生产消息和消费消息的速度。单个消息队列将导致生产者和消费者竞争同一个队列，消息队列将成功性能的瓶颈。但不同业务下的消息并没有关联，也自然没有必要将所有的消息都通过一个消息队列处理。将同一个业务定义下的消息归纳到一个消息队列下（topic队列），这样就将消息队列中的一个消息队列拆分为多个topic队列，大大提升了消息的处理速度。

  <img src="topic-queue.svg" width="60%" height="60%">

  当一个topic消息量大时，当前的设计仍然无法满足高性能需求。

  #### 使用partition进一步提高并发度

  <img src="simple-partition.svg" width="60%" height="60%">
  
  对同一个topic再进行切分，每个partition对应着一个队列，不同消费者处理不同的消息队列。

  ####  consumer-group: 实现多消费者的业务隔离

  <img src="consumer-group.svg" width="60%" height="60%">

  在上面提到的优化策略中，多给消费者协作处理一个topic，也就是一个消息只能被一个消费者消费。在实际业务需求中，同一个消息需要被多个业务线处理，这样就引入了消费者组的概念，同一个消费者组中的消费者协作处理同一个消息（一个消息只能被消费者组中的一个消费者处理），不同消费者组互不影响。

  ### 实现消息队列的高扩展性

  在上面的步骤中，通过对消息队列切分再切分已经大大提高了消息队列的性能，但整个消息队列的性能仍受机器的限制，需要通过通过扩展机器提高整个消费队列服务的性能。

  <img src="simple-broker.svg" width="60%" height="60%">

  通过将同一个topic中的不同partition分布在不同的broker上，再将多个broker构成一个kafka集群，实现硬件能力的扩展，提高kafka的处理速度。

  ### 实现消息队列的高可用

  #### 解决单个broker宕机：一主多从

  <img src="one-leader-multi-follower.svg" width="60%" height="60%">

  对每个partition，创建一个主节点，多个从节点，主解决负责读写，从节点只负责从主节点拉去数据、作数据备份。当某个broker宕机后，重新选取partition作为主节点。

  #### 解决所有broker宕机：数据持久化与过期策略

  <img src="persistence.svg" width="60%" height="60%">

  如果数据都存储在内存中，当所有broker都宕机后未消费的消息将丢失，通过持久化并重启服务可实现服务宕机后的数据恢复。数据不断写入磁盘将会导致磁盘空间占满，需要一种过期策略剔除过期数据。

    
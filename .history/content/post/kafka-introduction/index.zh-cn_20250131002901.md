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

  ### 实现消息队列的高扩展性

  




    
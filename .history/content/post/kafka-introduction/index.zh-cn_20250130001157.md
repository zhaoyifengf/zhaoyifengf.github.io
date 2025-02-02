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

  通过增加生产者和消费者可以增加生产消息和消费消息的速度。

  <img src="multi-producer-consumer.svg" width="50%" heigh="50%">

  





    
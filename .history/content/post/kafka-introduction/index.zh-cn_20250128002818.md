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

  很容想到在消费者中条件一个消息队列缓冲没有能够及时处理的消息，单这样做仍然会存在以下问题：
  
  - 在消费者重启后消息会丢失
  - 每个消费者都维护一个消息队列存在着重复造轮子的问题


    
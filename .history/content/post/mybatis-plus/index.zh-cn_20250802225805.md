---
title: "Mybatisplus"
description: 
date: 2025-06-23T23:26:52+08:00
image: cover.png
math: 
license: 
hidden: false
comments: true
draft: true
categories:
    - Mybatisplus
tags:
    - Mybatisplus
---

## mybatisplus SQL执行流程

### 创建SqlSessionFactory

- 通过自动配置类创建MybatisSqlSessionFactoryBean
`mybatis-plus-boot-starter`包提供了`MybatisPlusAutoConfiguration`自动配置类，该自动配置类创建了MybatisSqlSessionFactoryBean对象并交由Spring管理，在创建MybatisSqlSessionFactoryBean时，sqlSessionFactory方法设置了DataScoure对象。自动配置类需要满足以下几个条件才会创建MybatisSqlSessionFactoryBean：
    -  MybatisPlusAutoConfiguration上的@ConditionalOnSingleCandidate指定了：被Spring管理的只有一个DataSource对象或者多个DataSource对指定了优先级（如通过@Primary注解指定）
    - sqlSessionFactory方法上@ConditionalOnMissingBean指定了：只有在不存在SqlSessionFactory时才会创建MybatisSqlSessionFactoryBean对象

- 

```
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({SqlSessionFactory.class, SqlSessionFactoryBean.class})
@ConditionalOnSingleCandidate(DataSource.class)
@EnableConfigurationProperties(MybatisPlusProperties.class)
@AutoConfigureAfter({DataSourceAutoConfiguration.class, MybatisPlusLanguageDriverAutoConfiguration.class})
public class MybatisPlusAutoConfiguration implements InitializingBean {

    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")
    @Bean
    @ConditionalOnMissingBean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        // TODO 使用 MybatisSqlSessionFactoryBean 而不是 SqlSessionFactoryBean
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        ........
    }
}

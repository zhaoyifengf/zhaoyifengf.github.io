---
title: "Mybatisplus"
description: 
date: 2025-06-23T23:26:52+08:00
image: 
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

### 服务启动时通过自动配置类创建MybatisSqlSessionFactoryBean
  

`mybatis-plus-boot-starter`包提供了`MybatisPlusAutoConfiguration`自动配置类，该自动配置类创建了MybatisSqlSessionFactoryBean对象并交由Spring管理，在创建MybatisSqlSessionFactoryBean时，sqlSessionFactory方法设置了DataScoure对象。自动配置类需要满足以下几个条件才会创建MybatisSqlSessionFactoryBean：

-  MybatisPlusAutoConfiguration上的@ConditionalOnSingleCandidate指定了：被Spring管理的只有一个DataSource对象或者多个DataSource对指定了优先级（如通过@Primary注解指定）
- sqlSessionFactory方法上@ConditionalOnMissingBean指定了：只有在不存在SqlSessionFactory时才会创建MybatisSqlSessionFactoryBean对象

```
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({SqlSessionFactory.class, SqlSessionFactoryBean.class})
@ConditionalOnSingleCandidate(DataSource.class)
@EnableConfigurationProperties(MybatisPlusProperties.class)
@AutoConfigureAfter({DataSourceAutoConfiguration.class, MybatisPlusLanguageDriverAutoConfiguration.class})
public class MybatisPlusAutoConfiguration implements InitializingBean {
	@Bean
    @ConditionalOnMissingBean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        // TODO 使用 MybatisSqlSessionFactoryBean 而不是 SqlSessionFactoryBean
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
		.....
	}
}
```

###  Spring对事务进行代理
执行Mybatisplus DML语句前，Spring对要执行的方法（加了@Transactiontional注解）进行代理，代理执行的逻辑在TransactionAspectSupport中的invokeWithinTransaction方法中。整体调用流程如下

TransactionInterceptor#invoke -> TransactionAspectSupport#invokeWithinTransaction执行开启事务、执行业务逻辑、提交事务三个步骤。
- 开启事务
   - TransactionAspectSupport#invokeWithinTransaction -> determineTransactionManager
   - TransactionAspectSupport#determineTransactionManager -> createTransactionIfNecessary
   - TransactionAspectSupport#createTransactionIfNecessary -> AbstractPlatformTransactionManager#getTransaction，getTransaction方法先尝试获取事务再开启事务：
     - 获取事务
       - AbstractPlatformTransactionManager#getTransaction -> DataSourceTransactionManager#doGetTransaction（doGetTransaction是个抽象方法，具体逻辑由实现类提供，我们在这里只讨论DataSourceTransactionManager的实现逻辑）
       - DataSourceTransactionManager#doGetTransaction，该方法做下如下操作：
         - 创建DataSourceTransactionObject对象
         - TransactionSynchronizationManager.getResource方法获取DataSourceTransactionManager中dataScoure对象绑定的ConnectionHolder对象（用来存储connection对象）。TransactionSynchronizationManager中维护了一个ThreadLocal属性resources，这是一个以dataScoure对象为key、ConnectionHolder对象为值的Map。TransactionSynchronizationManager用来管理每个线程中和dataScoure对象绑定的connection对象。
         - 将上一步获取的ConnectionHolder设置到DataSourceTransactionObject中
     - 开启事务
       - AbstractPlatformTransactionManager#getTransactio -> DataSourceTransactionManager#startTransaction
		- DataSourceTransactionManager#startTransactionn -> doBegin方法，实现如下操作（DataSourceTransactionManager#doGetTransaction对象返回的DataSourceTransactionObject中的ConnectionHolder为空时执行该步骤）：
         - 通过DataSourceTransactionManager中dataScoure对象获取connection
         - 将connection包装为ConnectionHolder对象
         - 通过TransactionSynchronizationManager.bindResource将ConnectionHolder对象和connection对象绑定并设置上面提到的TransactionSynchronizationManager中的ThreadLocal属性resources中
 - 执行业务逻辑 
   - TransactionAspectSupport#invokeWithinTransaction执行被代理方法，mybatisplus中的方法也会在在此被执行，具体流程我们方法下一个部分讨论。
 - 提交事务

```
@SuppressWarnings("serial")
public class TransactionInterceptor extends TransactionAspectSupport implements MethodInterceptor, Serializable {

	@Override
	@Nullable
	public Object invoke(MethodInvocation invocation) throws Throwable {
		// Work out the target class: may be {@code null}.
		// The TransactionAttributeSource should be passed the target class
		// as well as the method, which may be from an interface.
		Class<?> targetClass = (invocation.getThis() != null ? AopUtils.getTargetClass(invocation.getThis()) : null);

		// Adapt to TransactionAspectSupport's invokeWithinTransaction...
		return invokeWithinTransaction(invocation.getMethod(), targetClass, invocation::proceed);
	}
}

public abstract class TransactionAspectSupport implements BeanFactoryAware, InitializingBean {
	@Nullable
	protected Object invokeWithinTransaction(Method method, @Nullable Class<?> targetClass,
			final InvocationCallback invocation) throws Throwable {

		// If the transaction attribute is null, the method is non-transactional.
		TransactionAttributeSource tas = getTransactionAttributeSource();
		final TransactionAttribute txAttr = (tas != null ? tas.getTransactionAttribute(method, targetClass) : null);
		final TransactionManager tm = determineTransactionManager(txAttr);

		........ // 响应式事务处理逻辑

		PlatformTransactionManager ptm = asPlatformTransactionManager(tm);
		final String joinpointIdentification = methodIdentification(method, targetClass, txAttr);

		if (txAttr == null || !(ptm instanceof CallbackPreferringPlatformTransactionManager)) {
			// Standard transaction demarcation with getTransaction and commit/rollback calls.
			TransactionInfo txInfo = createTransactionIfNecessary(ptm, txAttr, joinpointIdentification);

			Object retVal;
			try {
				// This is an around advice: Invoke the next interceptor in the chain.
				// This will normally result in a target object being invoked.
				retVal = invocation.proceedWithInvocation();
			}
			catch (Throwable ex) {
				// target invocation exception
				completeTransactionAfterThrowing(txInfo, ex);
				throw ex;
			}
			finally {
				cleanupTransactionInfo(txInfo);
			}

			if (retVal != null && vavrPresent && VavrDelegate.isVavrTry(retVal)) {
				// Set rollback-only in case of Vavr failure matching our rollback rules...
				TransactionStatus status = txInfo.getTransactionStatus();
				if (status != null && txAttr != null) {
					retVal = VavrDelegate.evaluateTryFailure(retVal, txAttr, status);
				}
			}

			commitTransactionAfterReturning(txInfo);
			return retVal;
		}else {
			...... // 非回调事务处理逻辑
	}

	protected TransactionInfo createTransactionIfNecessary(@Nullable PlatformTransactionManager tm,
			@Nullable TransactionAttribute txAttr, final String joinpointIdentification) {
		...........
		TransactionStatus status = null;
		if (txAttr != null) {
			if (tm != null) {
				status = tm.getTransaction(txAttr);
			}
			.......
		}
		...........
	}
}

public abstract class AbstractPlatformTransactionManager implements PlatformTransactionManager, Serializable {
	@Override
	public final TransactionStatus getTransaction(@Nullable TransactionDefinition definition)
			throws TransactionException {
		...........................
		
		Object transaction = doGetTransaction();
		boolean debugEnabled = logger.isDebugEnabled();

		
		// No existing transaction found -> check propagation behavior to find out how to proceed.
		if (def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_MANDATORY) {
			.............
		}
		else if (def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRED ||
				def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW ||
				def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_NESTED) {
			SuspendedResourcesHolder suspendedResources = suspend(null);
			...............
			try {
				return startTransaction(def, transaction, debugEnabled, suspendedResources);
			}
			catch (RuntimeException | Error ex) {
				
			}
		}
		else {
			.........
		}
	}

	/**
	 * Start a new transaction.
	 */
	private TransactionStatus startTransaction(TransactionDefinition definition, Object transaction,
			boolean debugEnabled, @Nullable SuspendedResourcesHolder suspendedResources) {

		boolean newSynchronization = (getTransactionSynchronization() != SYNCHRONIZATION_NEVER);
		DefaultTransactionStatus status = newTransactionStatus(
				definition, transaction, true, newSynchronization, debugEnabled, suspendedResources);
		doBegin(transaction, definition);
		prepareSynchronization(status, definition);
		return status;
	}
}

public class DataSourceTransactionManager extends AbstractPlatformTransactionManager
		implements ResourceTransactionManager, InitializingBean {
	protected Object doGetTransaction() {
		DataSourceTransactionObject txObject = new DataSourceTransactionObject();
		txObject.setSavepointAllowed(isNestedTransactionAllowed());
		ConnectionHolder conHolder =
				(ConnectionHolder) TransactionSynchronizationManager.getResource(obtainDataSource());
		txObject.setConnectionHolder(conHolder, false);
		return txObject;
	}

	protected void doBegin(Object transaction, TransactionDefinition definition) {
		DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
		Connection con = null;

		try {
			if (!txObject.hasConnectionHolder() ||
					txObject.getConnectionHolder().isSynchronizedWithTransaction()) {
				Connection newCon = obtainDataSource().getConnection();
				if (logger.isDebugEnabled()) {
					logger.debug("Acquired Connection [" + newCon + "] for JDBC transaction");
				}
				txObject.setConnectionHolder(new ConnectionHolder(newCon), true);
			}

			txObject.getConnectionHolder().setSynchronizedWithTransaction(true);
			con = txObject.getConnectionHolder().getConnection();

			Integer previousIsolationLevel = DataSourceUtils.prepareConnectionForTransaction(con, definition);
			txObject.setPreviousIsolationLevel(previousIsolationLevel);
			txObject.setReadOnly(definition.isReadOnly());

			// Switch to manual commit if necessary. This is very expensive in some JDBC drivers,
			// so we don't want to do it unnecessarily (for example if we've explicitly
			// configured the connection pool to set it already).
			if (con.getAutoCommit()) {
				txObject.setMustRestoreAutoCommit(true);
				if (logger.isDebugEnabled()) {
					logger.debug("Switching JDBC Connection [" + con + "] to manual commit");
				}
				con.setAutoCommit(false);
			}

			prepareTransactionalConnection(con, definition);
			txObject.getConnectionHolder().setTransactionActive(true);

			int timeout = determineTimeout(definition);
			if (timeout != TransactionDefinition.TIMEOUT_DEFAULT) {
				txObject.getConnectionHolder().setTimeoutInSeconds(timeout);
			}

			// Bind the connection holder to the thread.
			if (txObject.isNewConnectionHolder()) {
				TransactionSynchronizationManager.bindResource(obtainDataSource(), txObject.getConnectionHolder());
			}
		}

		catch (Throwable ex) {
			if (txObject.isNewConnectionHolder()) {
				DataSourceUtils.releaseConnection(con, obtainDataSource());
				txObject.setConnectionHolder(null, false);
			}
			throw new CannotCreateTransactionException("Could not open JDBC Connection for transaction", ex);
		}
	}
}
```

## 执行mybatisplus DML与Select语句

以调用IService的saveBatch方法为例，其最初调用链路如下ServiceImpl#saveBatch -> ServiceImpl#executeBatch -> SqlHelper#executeBatch，
执行步骤如下：

- 获取SqlSessionFactory

	SqlHelper#executeBatch调用sqlSessionFactory方法，sqlSessionFactory对象中持有DataSource对象的引用。

- 调用上面一步获取的SqlSessionFactory的openSession方法（这里以DefaultSqlSessionFactory加以说明），需要注意的事这里的Transaction对象并不参与事务的执行，只是用来管理数据源，该方法执行了如下步骤：

	- 创建TransactionFactory对象
	- 通过TransactionFactory对象创建Transaction对象，并传入从configure（SqlSessionFactory持有）对象中获取的dataScoure对象
	- 创建Executor对象并传入Transaction对象
	- 创建DefaultSqlSession对象并传入Executor对象
  ```
  private SqlSession openSessionFromDataSource(ExecutorType execType, TransactionIsolationLevel level, boolean autoCommit) {
		Transaction tx = null;
		try {
		final Environment environment = configuration.getEnvironment();
		final TransactionFactory transactionFactory = getTransactionFactoryFromEnvironment(environment);
		tx = transactionFactory.newTransaction(environment.getDataSource(), level, autoCommit);
		final Executor executor = configuration.newExecutor(tx, execType);
		return new DefaultSqlSession(configuration, executor, autoCommit);
		} catch (Exception e) {
		closeTransaction(tx); // may have fetched a connection so lets call close()
		throw ExceptionFactory.wrapException("Error opening session.  Cause: " + e, e);
		} finally {
		ErrorContext.instance().reset();
		}
  }
  ```
	

- 调用SqlSession的insert方法
  - 调用链路SqlSession#insert -> SqlSession#update -> BaseExecutor#update -> BatchExecutor#doUpdate，BatchExecutor#doUpdate执行了如下步骤：
    - 获取Connection，调用BaseExecutor#getConnection -> Transaction.getConnection -> SpringManagedTransaction.getConnection -> SpringManagedTransaction.openConnection -> DataSourceUtils.getConnection -> DataSourceUtils.doGetConnection，从下面的代码可知道如果当前数据源绑定了Connection则获取绑定的Connection，如果没有绑定则调用DataScoure对象的getConnection方法获取新的connection方法
	```
	public static Connection doGetConnection(DataSource dataSource) throws SQLException {
		.......
		ConnectionHolder conHolder = (ConnectionHolder) TransactionSynchronizationManager.getResource(dataSource);
		if (conHolder != null && (conHolder.hasConnection() || conHolder.isSynchronizedWithTransaction())) {
			conHolder.requested();
			if (!conHolder.hasConnection()) {
				logger.debug("Fetching resumed JDBC Connection from DataSource");
				conHolder.setConnection(fetchConnection(dataSource));
			}
			return conHolder.getConnection();
		}
		// Else we either got no holder or an empty thread-bound holder here.

		logger.debug("Fetching JDBC Connection from DataSource");
		Connection con = fetchConnection(dataSource);
		........
		return con;
	}

	private static Connection fetchConnection(DataSource dataSource) throws SQLException {
		Connection con = dataSource.getConnection();
		if (con == null) {
			throw new IllegalStateException("DataSource returned null from getConnection(): " + dataSource);
		}
		return con;
	}
	```
    - 准备Statement，设置Connection为上一步获取的Connection
    - 执行SQL语句
  
## DataScoure：数据库链接的管理者

不论是在Spring事务还是mybatisplus执行SQL语句前获取connection，都会调用DataScoure#getConnection方法。如下，DataScoure只提供了两个获取connection方法，由此可知DataScoure最主要的功能就是进行Connection的管理。对DataSource的getConnection方法提供不同的实现可以提供不同的功能，最典型的莫过于连接池和动态数据源。

	```
		public interface DataSource  extends CommonDataSource, Wrapper {

		Connection getConnection() throws SQLException;

		Connection getConnection(String username, String password) throws SQLException;
		}
	```
### 连接池

### 动态数据源

我们以HikariCP为例，先介绍其在SpringBoot项目中如何使用，再介绍如何通过其获取Connection

- SpringBoot集成HikariCP

	- SpringBoot配置
		```
			spring:
				datasource:
				type: com.zaxxer.hikari.HikariDataSource
				url: jdbc:mysql://localhost:3306/test?useSSL=false
				username: root
				password: 123456
				driver-class-name: com.mysql.cj.jdbc.Driver
				hikari:
					pool-name: MyHikariCP
					minimum-idle: 5
					maximum-pool-size: 20
					idle-timeout: 600000
					max-lifetime: 1800000
					connection-timeout: 30000
					connection-test-query: SELECT 1
	  ```

## mybatisplus 执行 SQL时数据源问题总结

- 数据源DataScoure是一个关联数据库连接的对象，它与数据库连接是一对多的关联
- mybatisplus的数据源对象取自SqlSessionFactory对象，在满足第一节Mybatisplus自动配置MybatisSqlSessionFactoryBean的条件下，mybatisplus获取的是优先级最高的（加了@Primary）DataScoure对象
- 指定事务管理器的数据源只会影响@Transactional注解绑定Datasource对象和Connection方法的逻辑，并不会影响mybatisplus实际获取的数据源（mybatisplus从SqlSessionFactory中取的数据源）
	


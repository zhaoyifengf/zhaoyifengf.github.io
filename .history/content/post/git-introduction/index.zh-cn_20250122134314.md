---
title: Git Introduction
description: 
slug: git-introduction
date: 2025-01-03 22:04:00+0000
image: cover.png
categories:
    - Git
tags:
    - Introduction
weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## git版本控制的方式
### 两种版本控制方式
- 基于差异的版本控制（delta-based）
	这类版本控制将存储信息看作一组基本文件和每个文件随时间逐步积累的差异

	![图片描述](https://gitee.com/progit/figures/18333fig0104-tn.png)

- 基于快照的版本控制
	这类版本控制将存储信息看作对小型文件系统的一系列快照，在git中，每当提交更新或者保存项目状态时，就会基本上对当时的全部文件创建一个快照保存并保存这个快照的索引。

	![图片描述](https://gitee.com/progit/figures/18333fig0105-tn.png)

## git环境配置
### 基本命令
1. 设置全局配置
	```
	git config --global
	```
   - `config`：表示配置git
   - --global：表示全局配置

2. 设置用户名
	```
	git config --global user.name "用户名"
	```
3. 设置邮箱
	```
	git config --global user.email "邮箱"
	```
	用户名和邮箱是这台机器上git的唯一标志

## 获取git仓库
### 本地仓库的创建和初始化
#### 在已存在目录中创建和初始化
   1. 进入目录
		```
		cd 目录名
		```
   2. 初始化当前目录
		```
		git init
		```
		执行git init目录后出现如下结果：
		```
		zhaoyifeng@MacBook-Air-6 test % git init
		提示：使用 'master' 作为初始分支的名称。这个默认分支名称可能会更改。要在新仓库中
		提示：配置使用初始分支名，并消除这条警告，请执行：
		提示：
		提示：	git config --global init.defaultBranch <名称>
		提示：
		提示：除了 'master' 之外，通常选定的名字有 'main'、'trunk' 和 'development'。
		提示：可以通过以下命令重命名刚创建的分支：
		提示：
		提示：	git branch -m <name>
		已初始化空的 Git 仓库于 /Users/zhaoyifeng/Documents/LocalRepository/test/.git/
		```
   3. 查看仓库中的文件夹：
		```
		zhaoyifeng@MacBook-Air-6 test % ls -ah
		.	..	.git
		```
		.git文件夹默认处于隐藏状态，需要添加-ah参数才能查看所有文件
   4. 查看.git文件夹中的内容

		```
		zhaoyifeng@MacBook-Air-6 test % cd .git
		zhaoyifeng@MacBook-Air-6 .git % ls -ah
		.		..		HEAD		config		description	hooks		info		objects		refs
		```

		| 文件夹  | 作用  |
		|----------|----------|
		| hooks | 包含客户端或服务端的勾子脚本 |
		| info | 保护一个全局性排除文件 |
		| logs | 保存日志信息 |
		| objects | 存储所有数据内容 |
		| refs | 存储指向数据的提交对象的指针 |
		| config | 包含项目特有的配置选项 |
		| description | 用来显示对仓库的描述 |
		| HEAD | 指示目前被检出的分支 |
		| index | 保存暂存区信息 |
   5. git中的工作区、暂存区、版本库和仓库中文件夹的对应关系
   
		| git中的区域  | 文件夹  |
		|:----------|:----------|
		| 工作区    | 项目目录   |
		| 版本库    | .git文件夹，用来存放代码及历史版本   |
		| 暂存区   | .git下的index文件，用来存储临时文件（只是在index文件中添加一条操作记录，并没有将内容存放到index文件中）    |

#### 克隆现有的仓库
1. git克隆命令：`git clone <url> name`
会将远程仓库中的项目克隆到当前目录，然后初始化该项目，并进行add和commit

## git中的文件状态
   1. 未跟踪

		默认情况下，git仓库（执行`git init`命令的文件夹）下的文件处于未跟踪的状态，git无法对区进行跟踪管理。通过`add`命令可以将其由未跟踪变为已跟踪状态。
	
   2. 已跟踪
		添加到git仓库管理中的文件处于已跟踪的状态，git可以对其进行跟踪管理。已跟踪状态可以细分为：

      - 已暂存（Staged）：通过add命令将文件添加到暂存区后文件将处于Staged状态。
	
      - 已修改（Modified）：修改了已跟踪的文件后，将处于Modified状态

      - 未暂存（Committed）：将暂存区中的文件使用commit命令提交到git仓库后将处于Modified状态。
  
		![](https://gitee.com/progit/figures/18333fig0106-tn.png)

## 本地仓库的操作命令
   1. 创建本地仓库
      - 创建一个空文件夹
      - 进入该文件夹执行`git init`命令

   2. 添加文件到本地仓库
      1. 在创建的文件夹中新建一个文件
      2. 使用`git add xxx.xx`命令将工作区中的文件添加到暂存区，文件状态由未跟踪变为已跟踪。
			```
			zhaoyifeng@MacBook-Air-6 test % vim test.txt
			zhaoyifeng@MacBook-Air-6 test % git add test.txt
			```
			版本库只能跟踪和管理文本文件，视频、图片等文件虽然可由git管理，但git只能记录其大小而无法记录具体修改的内容。
			`git add .`将所有文件添加到暂存区。
      3. 取消暂存：`git reset HEAD 文件名`：取消暂存某一文件
      4. 使`git commit -m "xxxx"`将暂存区中的内容提交到本地仓库，`-m`后面的参数是本次提交的描述
			```
			zhaoyifeng@MacBook-Air-6 test % git commit -m "第一次提交"
			[master（根提交） f9de3df] 第一次提交
				1 file changed, 1 insertion(+)
				create mode 100644 test.txt
			```
			使用`git commit -m -a`进行先暂存再提交
      5. 在工作目录中回退到最近一次提交的版本：`git checkout -- <file>`
      6. 修改commit的注释
         	- 执行如下命令
         	```
         	git commit --amend
         	```
         	- 进入编辑器，修改注释信息

         	- 修改后输入 control + o 然后输入输入回车进行写入

         	- 退出编译器
   3. 忽略文件
		新建.gitignore文件，在里面添加需要忽略的文件

## 查看历史提交记录和当前状态
   1. 执行`git status`命令查看状态，使用`git status -s`或`git status --short`查看简短的状态。
   	```
   	zhaoyifeng@MacBook-Air-6 test % git status
   	位于分支 master
   	无文件要提交，干净的工作区
   	zhaoyifeng@MacBook-Air-6 test % 
   	```
   2. 执行`git log`查看历史记录
   
		```
		zhaoyifeng@MacBook-Air-6 test % git log
		commit bbf9be55393f4aaeb85909b9b4071973d21a2d50 (HEAD -> master)
		Author: zhaoyifeng <zhaoyifeng@lixiang.com>
		Date:   Wed Jul 5 17:14:36 2023 +0800
			The first time submit
		```

		- commit后面的字符串是这次提交的ID，（HEAD -> master)表示当前提交到了主分支，HEAD是一个指针
  
		- Author后面提交用户的信息
  
		- Date是提交时间
  
		- 最后一行是提交的描述信息
  
   3. 查看差异
      - `git diff`：查看尚未暂存的文件进行了那些修改
      - `git diff -- staged`：对比已暂存文件和最后一次提交文件的差异

## git中的分支
### 分支的本质
分支的本质：指向commit对象的可变指针（也可理解为执行数据快照的指针）
   1. commit对象：每次提交时都会保存一个commit对象，，包含指向暂存内容快照的指针、本次提交的作者等相关附属信息、零个或多个指向该提交对象的父对象指针：首次提交是没有直接祖先的，普通提交有一个祖先，由两个或多个分支合并产生的提交则有多个祖先。
   		
		![](https://gitee.com/progit/figures/18333fig0302-tn.png)

   2. git分支：指向commit对象的指针。git会默认创建一个master分支，在每次提交时都会自动向前移动。
   		
		![](https://gitee.com/progit/figures/18333fig0303-tn.png)
   3. 创建分支：本质上就是创建一个指针，`git branch testing`新建一个分支指针指向当前commit对象。也就是HEAD指针指向的分支指向的commit对象。
   		
		![](https://gitee.com/progit/figures/18333fig0304-tn.png)
   4. HEAD指针：指向当前所在的分支（HEAD不可直接指向commit对象）
   		
		![](https://gitee.com/progit/figures/18333fig0305-tn.png)
   5. 切换分支：改变HEAD指向的分支。`git checkout testing`切换到testing分支。
		> 当你切换分支的时候，Git 会重置你的工作目录，使其看起来像回到了你在那个分支上最后一次提交的样子。 Git 会自动添加、删除、修改文件以确保此时你的工作目录和这个分支最后一次提交时的样子一模一样。
		
		![](https://gitee.com/progit/figures/18333fig0306-tn.png)
		每提交一次后，HEAD都会随着当前分支一起移动。（HEAD指向的是分支指针，提交时分支指针不变，改变的只是分支指针指向的对象。）执行：
		```
		vim test rb
		git commit -a -m 'made a change'
		```
		得到如下结果：
		![](https://gitee.com/progit/figures/18333fig0307-tn.png)
		切换到一个分支时会将工作目录中的内容加载为该分支指向的快照中的内容，这会导致原来的工作目录中的内容丢失。
   6. 分支分叉：如果切换到master分支并在修改后进行提交那就会产生分支的分叉。
   
		```
		git checkout master
		vim test rb
		git commit -a -m 'made other change'
		```

		![](https://gitee.com/progit/figures/18333fig0309-tn.png)
   7. 分支的合并：
         - 未分叉分支的合并

         	![](https://gitee.com/progit/figures/18333fig0313-tn.png)
   			执行如下命令：
			```
			$ git checkout master
			$ git merge hotfix
			Updating f42c576..3a0874c
			Fast forward
			README | 1 -
			1 files changed, 0 insertions(+), 1 deletions(-)
			```
			可以发现出现了Fast forward也就是快进，这是因为要合并的分支在master的上游，只需要把master指向hotfix指向的commit对象即可。

		- 分叉分支的合并
			![](https://gitee.com/progit/figures/18333fig0315-tn.png)
			合并如图所示的分支，将iss53合并回master，执行如下命令
			```
			git checkout master
			git merge iss53
			```
			由于master指向的commit节点（C4）不是iss53指向的commit节点（C5）的直接祖先，因此会进行C4、C5和二者最近的共同祖先（C2）三个节点的简单三方合并的到一个新的简单快照，然后创建一个行的commit对象（C6）指向这个简单快照，然后master指向C6。

			![](https://gitee.com/progit/figures/18333fig0316-tn.png)

			![](https://gitee.com/progit/figures/18333fig0317-tn.png)

     	- 三种不同的合并方式
  
			![三种不同的合并方式](three_merge_explain.png)

			- git merge --ff(fast-forward): 如果能快进则快进分支即移动指针

			- git merge --no-ff(no-fast-forword): 即使能快进也会创建一个新的commit(内容和被合并分支的commit相同)

			- git merge --squash: 将被合并节点的修改的内容（保存删除操作）加载到工作区和暂存区，等待一次新的提交
   8. 合并时发生冲突：如果不同分支修改了同一部分，那合并时可能发生冲突。
		```
		git merge iss53
		Auto-merging index.html
		CONFLICT (content): Merge conflict in index.html
		Automatic merge failed; fix conflicts and then commit the result.
		```
		git作了合并但未提交，它会停下来等待解决冲突。打开发生冲突的文件index.html：
		```
		<<<<<<< HEAD:index.html
		<div id="footer">contact : email.support@github.com</div>
		=======
		<div id="footer">
		please contact us at support@github.com
		</div>
		>>>>>>> iss53:index.html
		```
		=======上面是当前分支文件中的内容，下面是iss53分支的内容。手动解决冲突，然后执行`git add index.html`，一旦进入暂存区就代表冲突已解决。再执行`git commit`。
   9.  删除分支：`git branch -d 分支名`，删除指定的分支。
   10. 分支的管理
		查看当前有哪些分支，其中*表示当前分支即HEAD指向的分支`git branch`
		```
		zhaoyifeng@MacBook-Air-6 test % git branch 
		* master
		testing
		```
		查看分支最后一次提交的信息`git branch -v`
		```
		zhaoyifeng@MacBook-Air-6 test % git branch -v
		* master  e13db42 Merge branch 'testing'
		testing ad69ccd testing第四次提交
		```
   11. 查看已合并到当前分支的分支：`git branch --merged`

   12. 查看未合并到当前分支的分支：`git branch --no-merged`

   13. 远程分支
       - 远程仓库的添加与查看
  
			添加远程仓库，url是远程仓库的地址，shorname是给url对应的远程仓库的命名。执行`git clone url`后会自动添加一个远程仓库并将其命名为origin，并且克隆这个远程仓库到本地。
			````
			git remote add <shortname> <url>	
			````
			查看远程仓库
			````
			zhaoyifeng@MacBook-Air-6 mytest % git remote
			origin
			````
			查看远程仓库和对应的URL，fetch表示拉取的链接，push表示推送的链接。
			````
			zhaoyifeng@MacBook-Air-6 mytest % git remote -v
			origin	https://gitee.com/zhao-jufeng/mytest/ (fetch)
			origin	https://gitee.com/zhao-jufeng/mytest/ (push)
			````
			查看某个远程仓库的具体信息

			````
			zhaoyifeng@MacBook-Air-6 mytest % git remote show origin
			* 远程 origin
			获取地址：https://gitee.com/zhao-jufeng/mytest/
			推送地址：https://gitee.com/zhao-jufeng/mytest/
			HEAD 分支：master
			远程分支：
			dev    已跟踪
			master 已跟踪
			为 'git pull' 配置的本地分支：ƒ
			master 与远程 master 合并
			为 'git push' 配置的本地引用：
			master 推送至 master (最新)
			````
	
       - 远程分支的查看：远程分支是存储在本地对应着远程数据库中分支的分支。

			`git branch`：只能查看本地分支

			`git branch -r`：查看远程分支

			远程仓库含有master和dev分支，执行`git clone https://gitee.com/zhao-jufeng/mytest/`命令后执行`git branch -r`可以得到：
				```
				zhaoyifeng@MacBook-Air-6 mytest % git branch -r
				origin/HEAD -> origin/master
				origin/dev
				origin/master
				```
			可以看到有两个远程分支，origin是远程仓库的名字，执行clone命令时默命名为origin。需要注意的是，这些分支也存储在本地，与远程仓库作一一映射。

			执行`tree .git`查看.git的目录结构：

				```
				zhaoyifeng@MacBook-Air-6 mytest % tree .git
				.git
				├── HEAD
				├── config
				├── description
				├── hooks
				│   ├── applypatch-msg.sample
				│   ├── commit-msg.sample
				│   ├── fsmonitor-watchman.sample
				│   ├── post-update.sample
				│   ├── pre-applypatch.sample
				│   ├── pre-commit.sample
				│   ├── pre-merge-commit.sample
				│   ├── pre-push.sample
				│   ├── pre-rebase.sample
				│   ├── pre-receive.sample
				│   ├── prepare-commit-msg.sample
				│   ├── push-to-checkout.sample
				│   ├── sendemail-validate.sample
				│   └── update.sample
				├── index
				├── info
				│   └── exclude
				├── logs
				│   ├── HEAD
				│   └── refs
				│       ├── heads
				│       │   └── master
				│       └── remotes
				│           └── origin
				│               └── HEAD
				├── objects
				│   ├── info
				│   └── pack
				│       ├── pack-d93bb5ea2faba296524bc440149ae8b102f490cf.idx
				│       ├── pack-d93bb5ea2faba296524bc440149ae8b102f490cf.pack
				│       └── pack-d93bb5ea2faba296524bc440149ae8b102f490cf.rev
				├── packed-refs
				└── refs
					├── heads
					│   └── master
					├── remotes
					│   └── origin
					│       └── HEAD
					└── tags
				```
			远程的refs中的内容被压缩到了packed-refs中，查看其内容可以看到两个远程分支。
				```
				cat .git/packed-refs
				# pack-refs with: peeled fully-peeled sorted 
				7eb1322ce1fa2104ac76d996c08eb1a861860cc1 refs/remotes/origin/dev
				7eb1322ce1fa2104ac76d996c08eb1a861860cc1 refs/remotes/origin/master
				```
			如果refs中含有远程分支，则该分支是最新的，packed-refs对远程分支的压缩有延迟。
			执行`git log`可以查看历史，master, origin/master, origin/dev, origin/HEAD都指向了一个commit对象。
			```
			zhaoyifeng@MacBook-Air-6 mytest % git log
			commit 7eb1322ce1fa2104ac76d996c08eb1a861860cc1 (HEAD -> master, origin/master, origin/dev, origin/HEAD)
			Author: 赵已峰 <zhaoyifeng@lixiang.com>
			Date:   Fri Jul 7 01:25:14 2023 +0000

				add test.txt.
			
				Signed-off-by: 赵已峰 <zhaoyifeng@lixiang.com>

			commit d6ce159ed51c87cd4e7531dfbbeb6015e5c22f1f
			Author: 赵已峰 <zhaoyifeng@lixiang.com>
			Date:   Fri Jul 7 01:24:38 2023 +0000

				Initial commit
			```
 
       - 同步远程仓库中的分支到本地：在远程分支（本地存储的远程仓库的分支并不是远程仓库中的分支）上修改后提交或者执行merge命令不会移动远程分支，只有通过`git fetch`或者`git pull`才会改变远程分支。这是为了保持远程分支和远程仓库中的分支的对应关系，避免在本地对远程分支进行修改。 

     	- `git fetch [remote-name]`：从远程仓库中拉取本地仓库没有的数据，这个操作会移动远程分支。

			```
			zhaoyifeng@MacBook-Air-6 mytest % git fetch
			remote: Enumerating objects: 4, done.
			remote: Counting objects: 100% (4/4), done.
			remote: Compressing objects: 100% (2/2), done.
			remote: Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
			展开对象中: 100% (3/3), 967 字节 | 193.00 KiB/s, 完成.
			来自 https://gitee.com/zhao-jufeng/mytest
			7eb1322..f20bd41  master     -> origin/master
			```

     	- `git pull `：`git fetch`和`git merge`命名的组合
			```
			git pull 远程仓库名 远程仓库分支名:本地分支名
			```
			拉取远程仓库中的分支在与本地分支merge（需要注意的是这会拉取远程仓库中的所有分支）
			如何入当前分支合并则可以省略本地分支名，简写为：
			```
			git pull 远程仓库名 远程仓库分支名
			```

		
       - 删除远程分支：

     		删除远程仓库中的分支再查看会出现如下提示：

			```
			zhaoyifeng@MacBook-Air-6 mytest % git remote show origin
			* 远程 origin
			获取地址：https://gitee.com/zhao-jufeng/mytest/
			推送地址：https://gitee.com/zhao-jufeng/mytest/
			HEAD 分支：master
			远程分支：
			master                  已跟踪
			refs/remotes/origin/dev 已过期（使用 'git remote prune' 来移除）
			为 'git pull' 配置的本地分支：
			master 与远程 master 合并
			为 'git push' 配置的本地引用：
			master 推送至 master (本地已过时)
			```

     		提示远程分支已过期，建议删除。执行如下命名删除：

			```
			zhaoyifeng@MacBook-Air-6 mytest % git remote prune origin
			修剪 origin
			URL：https://gitee.com/zhao-jufeng/mytest/
			* [已删除] origin/dev
			```
     		或者`git fetch --prune`先删远程仓库中没有的本地远程分支，然后再拉取远程仓库中的数据。

       - 本地仓库同步到远程仓库

         - `git push 远程仓库名 本地分支名:远程仓库中的分支名`：用本地仓库中的分支更新远程仓库的分支，这会让远程仓库的分支直接指向本地仓库的分支指向的commit，此外，与远程仓库中对应的远程分支也会指向本地分支指向的commit。注意，这并不要本地仓库中有远程仓库中对应的远程分支。

         - 如果本地分支名与远程仓库中的分支名相同，则可以简写为`git push 远程仓库名 分支名`

       - 跟踪分支：执行git push命令时需要同指定远程仓库名、本地分支名和远程分支名，而跟踪分支则可简化这个操作。
  
     		跟踪分支：本地分支和某个远程分支建立联系后那这个本地分支就变成一个跟踪分支。在跟踪分支上执行`git push`和`git pull`命令时无需指定远程仓库名、本地分支名和远程分支名。

       - 跟踪分支的创建
     	
     		- 在远程分支上创建分支时指定其为远程分支（建的本地分支名与远程分支名相同）：`$ git checkout --track 远程仓库名/远程分支名`

     		- 在远程分支上创建分支时指定其为远程分支（指定本地分支名）：`git checkout -b 本地分支名 远程仓库名/远程分支名`

     		- 指定已有的本地分支为莫哥远程分支的跟踪分支：`git branch -u 远程仓库名/远程分支名`

## git中的标签
### 什么是标签
  1. 标签的本质：一个指向commit对象的指针，类似于分支，但标签是一个静态指针，不会移动。
  2. 标签的作用：标记一个重要的commit。

### 打标签
   1. 给当前分支指向的commit打标签
      - 轻量标签：`git tag 标签名`
      - 附注标签：`git tag -a 标签名 -m "描述信息"`，相比轻量标签，附注标签可以添加描述信息

   2. 给某一次commit打标签：只需要在上面两种打标签的方式最后面添加要打标签的commit的Hash值即可
	
   3. 查看标签	
      - 查看有哪些标签`git tag`
      - 查看某一条标签的信息`git show 标签名`
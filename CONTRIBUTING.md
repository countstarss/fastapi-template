# 如何在此项目上进行开发

fastapi_template 欢迎社区的贡献。

**您需要 PYTHON3！**

本说明适用于 Linux 基础系统。（Linux、MacOS、BSD 等）
## 设置此 repo 的您自己的 fork。

- 在 github 界面上单击“Fork”按钮。
- 克隆此 repo 的 fork。`git clone git@github.com:YOUR_GIT_USERNAME/fastapi-template.git`
- 进入目录`cd fastapi-template`
- 添加上游 repo`git remote add upper https://github.com/countstarss/fastapi-template`

## 设置您自己的虚拟环境

运行“make virtualenv”以创建虚拟环境。
然后使用“source .venv/bin/activate”激活它。

## 以开发模式安装项目

运行“make install”以开发模式安装项目。

## 运行测试以确保一切正常

运行 `make test` 以运行测试。

## 创建一个新分支来处理您的贡献

运行 `git checkout -b my_contribution`

## 进行更改

使用您喜欢的编辑器编辑文件。（我们推荐使用 VIM 或 VSCode）

## 格式化代码

运行 `make fmt` 以格式化代码。

## 运行 linter

运行 `make lint` 以运行 linter。

## 测试您的更改

运行 `make test` 以运行测试。

确保代码覆盖率报告显示 `100%` 覆盖率，将测试添加到您的 PR。

## 在本地构建文档

运行 `make docs` 以构建文档。

确保您的新更改已记录在案。

## 提交更改

本项目使用 [常规 git 提交消息](https://www.conventionalcommits.org/en/v1.0.0/)。

示例：`fix(package): update setup.py 参数 🎉`（表情符号也可以）

## 将您的更改推送到您的 fork

运行 `git push origin my_contribution`

## 提交拉取请求

在 github 界面上，单击 `Pull Request` 按钮。

等待 CI 运行，其中一位开发人员将审查您的 PR。
## Makefile 实用程序

本项目附带一个 `Makefile`，其中包含许多有用的实用程序。

```bash
❯ make
用法：make <target>

目标：
help：## 显示帮助。
install：## 在开发模式下安装项目。
fmt：## 使用 black 和 isort 格式化代码。
lint：## 运行 pep8、black、mypy linters。
test：lint ## 运行测试并生成覆盖率报告。
watch：## 对每个更改运行测试。
clean：## 清理未使用的文件。
virtualenv：## 创建虚拟环境。
release：## 为发布创建新标签。
docs：## 构建文档。
switch-to-poetry：## 切换到 poetry 包管理器。
init：## 根据应用程序模板初始化项目。
```

## 创建新版本

该项目使用 [语义版本控制](https://semver.org/) 并使用 `X.Y.Z` 标记版本

每次创建新标签并将其推送到远程存储库时，github 操作将
自动在 github 上创建新版本并在 PyPI 上触发发布。

为了实现此功能，您需要在项目设置>机密中设置一个名为“PIPY_API_TOKEN”的机密，
此令牌可以在[pypi.org](https://pypi.org/account/)上生成。

要触发新版本，您需要做的就是。

1. 如果您有更改要添加到存储库
* 按照上述步骤进行更改。
* 按照[常规 git 提交消息](https://www.conventionalcommits.org/en/v1.0.0/)提交您的更改。
2. 运行测试以确保一切正常。
4. 运行“make release”以创建新标签并将其推送到远程存储库。

“make release”将询问您创建标签的版本号，例如：当系统询问您时，请输入“0.1.1”。

> **注意**：make release 将更改本地更改日志文件并提交您拥有的所有未暂存的更改。


# How to develop on this project


fastapi_template welcomes contributions from the community.

**You need PYTHON3!**

This instructions are for linux base systems. (Linux, MacOS, BSD, etc.)
## Setting up your own fork of this repo.

- On github interface click on `Fork` button.
- Clone your fork of this repo. `git clone git@github.com:YOUR_GIT_USERNAME/fastapi-template.git`
- Enter the directory `cd fastapi-template`
- Add upstream repo `git remote add upstream https://github.com/countstarss/fastapi-template`

## Setting up your own virtual environment

Run `make virtualenv` to create a virtual environment.
then activate it with `source .venv/bin/activate`.

## Install the project in develop mode

Run `make install` to install the project in develop mode.

## Run the tests to ensure everything is working

Run `make test` to run the tests.

## Create a new branch to work on your contribution

Run `git checkout -b my_contribution`

## Make your changes

Edit the files using your preferred editor. (we recommend VIM or VSCode)

## Format the code

Run `make fmt` to format the code.

## Run the linter

Run `make lint` to run the linter.

## Test your changes

Run `make test` to run the tests.

Ensure code coverage report shows `100%` coverage, add tests to your PR.

## Build the docs locally

Run `make docs` to build the docs.

Ensure your new changes are documented.

## Commit your changes

This project uses [conventional git commit messages](https://www.conventionalcommits.org/en/v1.0.0/).

Example: `fix(package): update setup.py arguments 🎉` (emojis are fine too)

## Push your changes to your fork

Run `git push origin my_contribution`

## Submit a pull request

On github interface, click on `Pull Request` button.

Wait CI to run and one of the developers will review your PR.
## Makefile utilities

This project comes with a `Makefile` that contains a number of useful utility.

```bash 
❯ make
Usage: make <target>

Targets:
help:             ## Show the help.
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test: lint        ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
release:          ## Create a new tag for release.
docs:             ## Build the documentation.
switch-to-poetry: ## Switch to poetry package manager.
init:             ## Initialize the project based on an application template.
```

## Making a new release

This project uses [semantic versioning](https://semver.org/) and tags releases with `X.Y.Z`
Every time a new tag is created and pushed to the remote repo, github actions will
automatically create a new release on github and trigger a release on PyPI.

For this to work you need to setup a secret called `PIPY_API_TOKEN` on the project settings>secrets, 
this token can be generated on [pypi.org](https://pypi.org/account/).

To trigger a new release all you need to do is.

1. If you have changes to add to the repo
    * Make your changes following the steps described above.
    * Commit your changes following the [conventional git commit messages](https://www.conventionalcommits.org/en/v1.0.0/).
2. Run the tests to ensure everything is working.
4. Run `make release` to create a new tag and push it to the remote repo.

the `make release` will ask you the version number to create the tag, ex: type `0.1.1` when you are asked.

> **CAUTION**:  The make release will change local changelog files and commit all the unstaged changes you have.

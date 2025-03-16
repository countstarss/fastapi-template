# 添加依赖
  pip install alembic

# 初始化 alembic
  alembic init migrations

# 添加数据库链接字符串
  # alembic.ini
  sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/luke

# 修改migrations/env.py文件
  - 在线迁移
  - 离线迁移

# 创建迁移
  alembic revision --autogenerate -m "Initial migration"

# 应用迁移
  alembic upgrade head




## 总结修复步骤

1. 修复了 `migrations/env.py` 文件中的导入问题：
   - 直接从 `sqlmodel` 包导入 `SQLModel` 类
   - 导入所有模型模块以确保它们被注册到 `SQLModel.metadata`

2. 在 `core/config.py` 中添加了数据库 URI 配置：
   - 添加了 `DATABASE_URI` 设置，默认值为 `sqlite:///./test.db`

3. 成功运行了 Alembic 迁移命令：
   - 生成了初始迁移脚本
   - 应用了迁移到数据库

现在您的项目已经配置好了数据库迁移功能，您可以使用 Alembic 来管理数据库架构变更。

## 使用 Alembic 的常用命令

以下是一些使用 Alembic 的常用命令：

1. 创建新的迁移：
   ```bash
   alembic revision --autogenerate -m "描述迁移的内容"
   ```

2. 应用迁移：
   ```bash
   alembic upgrade head  # 迁移到最新版本
   alembic upgrade +1    # 向前迁移一个版本
   ```

3. 回滚迁移：
   ```bash
   alembic downgrade -1  # 回滚一个版本
   alembic downgrade base  # 回滚到初始状态
   ```

4. 查看迁移历史：
   ```bash
   alembic history
   ```

5. 查看当前版本：
   ```bash
   alembic current
   ```

这些命令将帮助您管理数据库架构变更，使您的应用程序更加健壮和可维护。

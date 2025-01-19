# Git Commit 规范

本文档定义了项目的 Git Commit 消息规范，基于 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

## Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type 类型（必须）

commit 的类型必须是以下类型之一：

- **feat**: 新功能（feature）
- **fix**: 修复 bug
- **docs**: 文档更新
- **style**: 代码格式调整（不影响代码运行的变动）
- **refactor**: 代码重构（既不是新增功能，也不是修改 bug 的代码变动）
- **perf**: 性能优化
- **test**: 增加测试或更新现有测试
- **chore**: 构建过程或辅助工具的变动
- **ci**: 持续集成相关的改动

## Scope（可选）

scope 用于说明 commit 影响的范围，例如：

- **api**: API 相关改动
- **db**: 数据库相关改动
- **ui**: 用户界面相关改动
- **auth**: 认证相关改动
- **docs**: 文档相关改动

## Subject（必须）

subject 是 commit 目的的简短描述：

- 不超过 50 个字符
- 以动词开头，使用现在时
- 第一个字母小写
- 结尾不加句号

## Body（可选）

body 部分是对本次 commit 的详细描述：

- 可以分多行
- 说明代码变动的动机，以及与以前行为的对比

## Footer（可选）

footer 部分用于以下场景：

- 关联 Issue
- 标记是否有 Breaking Changes
- 关闭 Issue

## 示例

### 功能新增
```
feat(translation): add Chinese to English translation API

- Add new translation endpoint
- Implement language detection
- Add error handling for invalid inputs

Closes #123
```

### Bug 修复
```
fix(auth): resolve token expiration issue

Fixed JWT token not being refreshed properly when close to expiration.
Added automatic token refresh mechanism.

Breaking Change: Token format has been modified
```

### 测试相关
```
test(e2e): add translation service end-to-end tests

- Add SSE response handling
- Add error case testing
- Verify translation quality
```

## 最佳实践

1. **原子性**
   - 每个 commit 应该表达单一的改动意图
   - 避免在一个 commit 中混合多个不相关的改动

2. **提交前检查**
   - 使用 `git diff` 检查改动内容
   - 使用 `git commit -v` 在编辑器中编写详细的提交信息

3. **工具支持**
   - 使用 commitlint 等工具强制执行提交规范
   - 配置 git hooks 在提交前进行检查

4. **关联 Issue**
   - 在 commit 信息中关联相关的 Issue
   - 使用关键字（如 Closes, Fixes, Resolves）自动关闭 Issue

## 规范的好处

1. **自动化**
   - 可以自动生成 CHANGELOG
   - 便于版本管理和发布

2. **可维护性**
   - 快速理解代码变更历史
   - 方便进行代码审查
   - 提高项目的可维护性

3. **团队协作**
   - 统一的提交规范有助于团队协作
   - 提高代码审查的效率
   - 便于新成员快速理解项目历史

## 工具推荐

1. **Commitlint**: 检查 commit 消息是否符合规范
2. **Commitizen**: 交互式生成规范的 commit 消息
3. **Standard Version**: 自动生成 CHANGELOG 并管理版本号

## 参考资料

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)

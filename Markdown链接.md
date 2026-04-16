以下是 **GitHub Markdown** 中**指向子文件夹中文件**的完整正确写法（推荐使用**相对链接**）。

GitHub 会自动将相对路径转换为正确的仓库链接（根据当前分支、当前文件位置），这样无论在 GitHub 上查看还是本地 clone 后查看，都能正常工作。

### 1. 基本语法（推荐）

```markdown
[链接文字](子文件夹路径/文件名)
```

**注意**：
- 使用 **正斜杠** `/`（即使你在 Windows 上）。
- **不要** 在最前面加 `/`（加 `/` 会变成相对于仓库根目录的绝对路径）。
- 文件名要包含扩展名（如 `.md`、`.pdf`、`.png` 等）。
- 路径区分**大小写**。
- 如果文件夹名或文件名包含空格，建议用短横线 `-` 或下划线 `_` 替代，或者用 `%20` 编码（但推荐避免空格）。

### 2. 常见场景示例

假设你的仓库目录结构如下：

```
my-repo/
├── README.md                  ← 你正在编辑的文件
├── docs/
│   ├── guide.md
│   └── images/
│       └── screenshot.png
├── src/
│   └── main.py
└── examples/
    └── demo/
        └── example.md
```

#### 从根目录的 README.md 指向子文件夹中的文件

```markdown
- [使用指南](docs/guide.md)
- [查看截图](docs/images/screenshot.png)
- [主程序源码](src/main.py)
- [示例演示](examples/demo/example.md)
```

#### 从子文件夹中的 Markdown 文件指向另一个子文件夹

假设你在 `docs/guide.md` 中，想链接到：

- 同级文件：`docs/another.md`
- 子文件夹：`docs/images/photo.jpg`
- 父级目录的文件：`README.md`（仓库根目录）

```markdown
[另一个文档](./another.md)          <!-- 同级文件，推荐加 ./ -->
[查看图片](images/photo.jpg)        <!-- 子文件夹 -->
[返回项目首页](../README.md)        <!-- 返回上一级 -->
[返回根目录](../../README.md)       <!-- 返回两级 -->
```

**推荐写法总结**：
- 同级文件 → `[文字](filename.md)` 或 `[文字](./filename.md)`
- 子文件夹 → `[文字](folder/filename.md)`
- 父级目录 → `[文字](../filename.md)` 或 `[文字](../folder/filename.md)`

### 3. 指向文件夹本身（显示目录视图）

如果想链接到整个子文件夹（显示 GitHub 的树状文件列表），需要在路径最后加 `/`：

```markdown
[查看 docs 文件夹](docs/)
[查看 examples/demo 文件夹](examples/demo/)
```

### 4. 其他高级写法

- **使用 `./` 明确当前目录**（更清晰，推荐）：
  ```markdown
  [当前文件夹下的文件](./file.md)
  [子文件夹](./docs/guide.md)
  ```

- **链接到特定行**（代码文件）：
  ```markdown
  [查看 main.py 的第 10 行](src/main.py#L10)
  ```

- **链接到特定提交/分支**（不推荐日常使用）：
  ```markdown
  [旧版本指南](https://github.com/用户名/仓库名/blob/old-branch/docs/guide.md)
  ```

### 5. 常见错误及避免方法

| 错误写法                  | 问题                          | 正确写法                     |
|---------------------------|-------------------------------|------------------------------|
| `/docs/guide.md`          | 变成网站根目录                | `docs/guide.md`             |
| `docs\guide.md`           | Windows 反斜杠不支持          | `docs/guide.md`             |
| `docs/guide`（无扩展名）  | 可能无法正确识别              | `docs/guide.md`             |
| `Docs/Guide.md`（大小写错）| GitHub 对大小写敏感          | 严格匹配实际大小写          |

### 6. 图片链接也是同样规则

```markdown
![截图](docs/images/screenshot.png)
![截图](./images/screenshot.png)   <!-- 如果在 docs/ 文件夹内 -->
```

### 官方建议
GitHub 官方文档强烈推荐使用**相对链接**，因为：
- Clone 到本地后仍然有效
- 切换分支时自动适配
- 仓库移动或重命名后仍能工作

参考：https://docs.github.com/zh/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links

**小贴士**：
- 在 GitHub 编辑页面可以直接预览链接是否正确（切换到 Preview 标签）。
- 如果链接点击后 404，最常见原因是路径大小写错误或多了/少了 `/`。

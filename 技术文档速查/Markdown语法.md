# **GitHub Flavored Markdown (GFM)** 完整语法指南

- 官方参考：
  - GitHub 文档：基本写作和格式语法
  - GFM 规范：<https://github.github.com/gfm/>

## 1. 标题 (Headings)

使用 1~6 个 `#` 符号，后跟空格。

```markdown
# 一级标题 (H1)
## 二级标题 (H2)
### 三级标题 (H3)
#### 四级标题 (H4)
##### 五级标题 (H5)
###### 六级标题 (H6)
```

**效果：**

- 标题会自动生成目录（Outline），在文件头部点击即可查看。

另一种方式（仅 H1 和 H2）：

```markdown
一级标题
========

二级标题
--------
```

## 2. 文本强调 (Emphasis)

| 样式         | 语法                    | 示例              | 效果             |
|--------------|-------------------------|-------------------|------------------|
|   **粗体**   |`**文本**` 或 `__文本__` | `**粗体文本**`    | **粗体文本**     |
| *斜体*       | `*文本*` 或 `_文本_`    | `_斜体文本_`      | *斜体文本*       |
| ***粗斜体*** | `***文本***`            | `***粗斜体***`    | ***粗斜体***     |
| ~~删除线~~   | `~~文本~~`              | `~~删除线~~`      | ~~删除线~~       |

**注意**：GitHub 支持嵌套，如 `**粗体中_斜体_**` → **粗体中_斜体_**。

## 3. 段落与换行

- 段落之间空一行。
- 强制换行：在行尾输入两个空格 `  ` 或使用 `<br>`。

## 4. 引用 (Blockquotes)

```markdown
> 这是一级引用
>> 这是一级引用中的二级引用
>>> 三级引用
```

**效果：**
> 这是一级引用
>> 这是一级引用中的二级引用

## 5. 列表 (Lists)

**无序列表**：

```markdown
- 项目1
  - 子项目1
- 项目2
* 也可以用星号
+ 或者加号
```

**有序列表**：

```markdown
1. 第一项
2. 第二项
   1. 子项
5. 序号可以不连续，GitHub 会自动修正
```

**任务列表**（GFM 扩展，可交互复选框）：

```markdown
- [x] 已完成任务
- [ ] 未完成任务
  - [ ] 子任务
```

**效果**：

- [x] 已完成任务
- [ ] 未完成任务

## 6. 代码 (Code)

**行内代码**：用反引号 `` ` `` 包裹。

```markdown
使用 `git status` 查看状态。
```

**代码块**（推荐使用围栏代码块）：

```markdown
```python
def hello():
    print("Hello, GitHub!")
```

指定语言后 GitHub 会自动语法高亮。支持数百种语言（如 `javascript`、`java`、`bash`、`yaml`、`markdown` 等）。<!-- markdownlint-disable-line MD044 -->

## 7. 分隔线 (Horizontal Rule)

```markdown
---
***
___
```

**效果**：

---

## 8. 链接 (Links)

**行内链接**：

```markdown
[链接文字](https://github.com "可选标题")
```

**引用式链接**：

```markdown
[链接文字][1]

[1]: https://github.com "可选标题"
```

**自动链接**（GFM 扩展）：

- 直接写 URL：`https://github.com` 会自动变成可点击链接。
- 邮箱：`user@example.com` 也会自动链接。

**相对链接**（推荐用于仓库内）：

```markdown
[README](./README.md)
[图片](../images/pic.png)
```

## 9. 图片 (Images)

```markdown
![替代文字](图片URL "可选标题")
```

**示例**：

```markdown
![GitHub Logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png)<!-- markdownlint-disable-line MD044 -->
```

支持相对路径、GitHub 仓库内的图片、外部 URL。

## 10. 表格 (Tables) - GFM 扩展

```markdown
| 左对齐 | 居中 | 右对齐 |
| :----- | :--: | -----: |
| 内容   | 内容 | 内容   |
| 内容   | 内容 | 内容   |
```

**效果**：

| 左对齐 | 居中 | 右对齐 |
| :----- | :--: | -----: |
| 内容   | 内容 | 内容   |

- 第一行是表头。
- 第二行用 `:` 控制对齐（左：`:-`、居中：`:-:`、右：`-:`）。

## 11. 脚注 (Footnotes) - GFM 支持

```markdown
这是一个脚注引用[^1]。

[^1]: 这里是脚注的详细解释。
```

## 12. 忽略 Markdown 格式

用反引号或 `\` 转义：

```markdown
\* 这不会变成斜体 \*
```

## 13. HTML 支持

GitHub Markdown 允许有限的 HTML 标签（如 `<br>`、`<kbd>`、`<details>` 等），但出于安全原因会过滤危险标签。

**折叠内容示例**：

```html
<details>
<summary>点击展开</summary>

这里是隐藏内容。
</details>
```

## 14. 其他 GFM 特色功能

- **@提及**：`@用户名` 会通知对方。
- **Issue/PR 引用**：`#123` 会自动链接到本仓库的 Issue 123。
- **Emoji**：直接输入 `:smile:` → 😄（完整列表见 emoji cheat sheet）。
- **自动任务列表** 在 Issue/PR 中特别有用。

## 15. 高级/扩展用法

- **Mermaid 图表**（部分 GitHub 上下文支持）：

  ````markdown:disable-run
  ```mermaid
  graph TD;
      A-->B;
  ```
  ````

- **数学公式**（部分地方支持 KaTeX）：`$E=mc^2$` 或 `$$...$$`。

## 推荐资源

- GitHub 官方基本语法文档（中文）：<https://docs.github.com/zh/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax>
- GFM 完整规范：<https://github.github.com/gfm/>
- Markdown Cheat Sheet（英文）：<https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet>

**小贴士**：

- 在 GitHub 上编辑时，可以实时预览（Preview 标签）。
- 写 README 时，建议先写好结构（标题 + 目录 + 列表），再填充内容。
- 复杂表格推荐使用在线 Markdown 表格生成器辅助。

这个指南覆盖了 GitHub 上 99% 的日常使用场景。如果你有特定场景（如 README 模板、Mermaid 图表等）需要示例，随时告诉我，我可以提供更多细节！

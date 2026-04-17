
# Markdown 规则

## 1. 标题（Headings）相关规则

- MD001 heading-increment
  - 中文：标题层级递增规则
  - 解释：标题层级只能逐级递增（例如 # → ## → ###），不能跳级（如 # 直接接 ###）。
  - 作用：符合文档层次结构，便于阅读和无障碍访问（Accessibility）。修复：中间补上缺失的层级。
- MD003 heading-style
  - 中文：标题样式规则
  - 解释：文档中所有标题必须使用一致的样式（ATX #、ATX_closed # ... #、Setext === / --- 等）。默认要求一致。
  - 作用：保持全文档标题风格统一。
- MD018 no-missing-space-atx
  - 中文：ATX 标题后缺少空格
  - 解释：ATX 标题的 # 符号后必须有一个空格（如 # 标题 而不是 #标题）。
- MD019 no-multiple-space-atx
  - 中文：ATX 标题后多个空格
  - 解释：# 后只能有一个空格，不能有多个（如 #  标题 是错误的）。
- MD020 no-missing-space-closed-atx
  - 中文：闭合 ATX 标题内部缺少空格
  - 解释：闭合式标题（如 # 标题 #）的 # 符号内部必须有空格（前后各一个）。
- MD021 no-multiple-space-closed-atx
  - 中文：闭合 ATX 标题内部多个空格
  - 解释：闭合 # 内部不能有多余空格。
- MD022 blanks-around-headings
  - 中文：标题周围需空行
  - 解释：标题前后必须有空白行（除文档开头外）。
  - 作用：提升视觉分隔和可读性。
- MD023 heading-start-left
  - 中文：标题必须从行首开始
  - 解释：标题行不能有缩进，必须从最左侧开始。
- MD024 no-duplicate-heading
  - 中文：禁止重复标题内容
  - 解释：同一文档中不能出现内容完全相同的标题（不同层级也不行，除非配置允许嵌套差异）。
修复：在医学笔记中，相同药物或机制不要用相同标题，可加修饰词。
- MD025 single-title/single-h1
  - 中文：文档只能有一个一级标题（H1）
  - 解释：一个 Markdown 文件中只能有一个 # 标题（通常作为主标题）。
- MD026 no-trailing-punctuation
  - 中文：标题末尾禁止标点
  - 解释：标题末尾不应有句号、感叹号等标点（  - 中文环境下可根据需要配置关闭）。
- MD041 first-line-heading/first-line-h1
  - 中文：文件第一行应为一级标题
  - 解释：文件开头第一行最好直接是 # 主标题（常用于严格文档）。

## 2. 列表（Lists）相关规则

- MD004 ul-style
  - 中文：无序列表样式规则
  - 解释：无序列表符号必须一致（*、- 或 +），默认要求全文档统一。
- MD005 list-indent
  - 中文：同级列表项缩进不一致
  - 解释：同一层级的列表项缩进空格必须相同。
- MD007 ul-indent
  - 中文：无序列表缩进规则
  - 解释：无序列表子项默认缩进 2 个空格（可配置）。
- MD029 ol-prefix
  - 中文：有序列表前缀规则
  - 解释：有序列表编号风格（1.、1)、01. 等）必须一致。
- MD030 list-marker-space
  - 中文：列表标记后空格数量
  - 解释：列表符号（-、*、1.）后必须有且只有一个空格。
- MD032 blanks-around-lists
  - 中文：列表周围需空行
  - 解释：列表前后必须有空白行，与正文分隔。

## 3. 空格与空白（Whitespace）相关规则

- MD009 no-trailing-spaces
  - 中文：禁止行尾空格
  - 解释：每行末尾不能有多余空格（非常常见的问题）。
- MD010 no-hard-tabs
  - 中文：禁止使用硬制表符（Tab）
  - 解释：必须使用空格代替 Tab 键缩进。
- MD012 no-multiple-blanks
  - 中文：禁止多个连续空行
  - 解释：文档中最多允许一个连续空行（不能有两行以上空白）。
- MD013 line-length
  - 中文：行长度限制
  - 解释：单行字符数不能超过设定长度（默认 80，可配置为 120 或更高，适合  - 中文笔记）。表格和代码块可单独配置。

## 4. 引用与代码块相关规则

- MD014 commands-show-output
  - 中文：命令前使用 $ 但未显示输出
  - 解释：代码块中如果用 $ command，则应同时展示输出，否则去掉 $。
- MD027 no-multiple-space-blockquote
  - 中文：引用块符号后多个空格
  - 解释：> 后只能有一个空格。
- MD028 no-blanks-blockquote
  - 中文：引用块内禁止空行
  - 解释：严格模式下引用块内部不能有空行（可配置）。
- MD031 blanks-around-fences
  - 中文：代码围栏周围需空行
  - 解释：``` 代码块前后必须有空白行。
- MD040 fenced-code-language
  - 中文：代码围栏需指定语言
  - 解释：后应写语言（如markdown），便于语法高亮。
- MD046 code-block-style
  - 中文：代码块样式规则
  - 解释：代码块必须统一使用围栏式（```）或缩进式。
- MD047 single-trailing-newline
  - 中文：文件末尾需单个换行符
  - 解释：文件必须以一个换行符结束（Unix 标准）。
- MD048 code-fence-style
  - 中文：代码围栏符号样式
  - 解释：代码块围栏必须统一使用 ``` 或 ~~~。

## 5. 链接与图片相关规则

- MD011 no-reversed-links
  - 中文：禁止反向链接语法
  - 解释：链接不能写成反向形式（如 [text](url) 而不是 [url](text)）。
- MD034 no-bare-urls
  - 中文：禁止裸 URL
  - 解释：直接写网址应使用 <https://...> 或 [文本](url) 形式。
- MD039 no-space-in-links
  - 中文：链接文本内禁止空格
  - 解释：链接文字两端不能有多余空格（如 [ 文本 ]）。
- MD042 no-empty-links
  - 中文：禁止空链接
  - 解释：链接不能没有内容或 URL。
- MD045 no-alt-text
  - 中文：图片必须有替代文本（alt text）
  - 解释：图片 ![alt](url) 中的 alt 文字不能为空，提升可访问性。
- MD051 link-fragments
  - 中文：链接片段（锚点）必须有效
  - 解释：[text](#anchor) 中的 anchor 必须在文档中存在。<!-- markdownlint-disable-line MD051 -->
- MD052 reference-links-images
  - 中文：引用式链接/图片的标签必须已定义
  - 解释：使用 [text][label] 时，文档底部必须有对应的 [label]: url 定义。<!-- markdownlint-disable-line MD052 -->
- MD053 link-image-reference-definitions
  - 中文：引用式链接/图片定义必须被使用
  - 解释：定义了 [label]: url 但文档中未使用时触发。
- MD054 link-image-style
  - 中文：链接与图片样式规则
  - 解释：链接和图片必须使用一致的风格（行内式或引用式）。
- MD059 descriptive-link-text
  - 中文：链接文字应具有描述性
  - 解释：避免使用“点击这里”“这里”等无意义链接文字，应使用具体描述。

## 6. 其他格式规则

- MD033 no-inline-html
  - 中文：禁止内联 HTML
  - 解释：Markdown 中不应直接使用 HTML 标签（可配置允许部分）。
- MD035 hr-style
  - 中文：水平分隔线样式规则
  - 解释：---、***、___ 等分隔线必须风格一致。
- MD036 no-emphasis-as-heading
  - 中文：禁止用强调代替标题
  - 解释：不要用 粗体 或 斜体 来模拟标题，应使用真实标题语法。
- MD037 no-space-in-emphasis
  - 中文：强调标记内禁止空格
  - 解释：**粗体** 或 *斜体* 内部不能有空格（如 **粗体** 是错的）。
- MD038 no-space-in-code
  - 中文：行内代码内禁止空格
  - 解释：`代码` 内部两端不能有多余空格。
- MD043 required-headings
  - 中文：要求特定标题结构
  - 解释：可自定义文档必须包含某些标题层级（高级规则，默认关闭）。
- MD044 proper-names
  - 中文：专有名词大小写规则
  - 解释：指定专有名词必须使用正确的大小写（需在配置中列出单词列表）。
- MD049 emphasis-style
  - 中文：强调（斜体）样式规则
  - 解释：斜体必须统一用 * 或 _。
- MD050 strong-style
  - 中文：加粗样式规则
  - 解释：加粗必须统一用 ** 或 __。
- MD055 table-pipe-style
  - 中文：表格管道符样式
  - 解释：表格的  符号必须风格一致（是否首尾都有）。
- MD056 table-column-count
  - 中文：表格列数一致性
  - 解释：同一表格所有行的列数必须相同。
- MD058 blanks-around-tables
  - 中文：表格周围需空行
  - 解释：表格前后必须有空白行。
- MD060 table-column-style
  - 中文：表格列对齐样式
  - 解释：表格列的对齐方式（左、中、右）应保持一致。

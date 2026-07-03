# 番茄小说下载器

## 功能说明

用于下载番茄小说指定书籍的全部章节内容，支持从书籍链接或ID直接下载。

## 使用前提

⚠️ **本工具仅供已获得合法授权的用户使用**

使用本工具前，请确保您：
1. 已获得该小说的IP改编授权（如抖音短剧中心授权）
2. 或拥有其他合法获取该小说内容的权利

## 使用方法

### 命令行方式

```bash
python download.py <书籍链接或ID> [格式]
```

**示例：**

```bash
# 使用书籍ID
python download.py 7494874354086333464

# 使用完整链接
python download.py https://fanqienovel.com/page/7494874354086333464

# 保存为JSON格式
python download.py 7494874354086333464 json
```

### 交互式方式

直接运行脚本，按提示输入：

```bash
python download.py
```

### 代码调用方式

```python
from download import FanqieDownloader

downloader = FanqieDownloader(output_dir="downloads")
downloader.download_book("7494874354086333464", save_format="txt")
```

## 支持的输入格式

| 格式 | 示例 |
|------|------|
| 纯数字ID | `7494874354086333464` |
| 页面链接 | `https://fanqienovel.com/page/7494874354086333464` |
| 阅读链接 | `https://fanqienovel.com/reader/7494874354086333464` |

## 输出格式

### TXT格式（默认）
- 包含书名、作者信息
- 按章节顺序排列
- 适合人工阅读和后续处理

### JSON格式
- 结构化数据，包含完整元数据
- 适合程序化处理和分析

## 输出目录

下载的文件保存在 `downloads/` 目录下：
- `downloads/书名.txt` 或 `downloads/书名.json`

## 注意事项

1. **付费章节**：工具会自动跳过付费/锁定章节
2. **请求频率**：默认每章间隔0.5秒，避免对服务器造成压力
3. **网络问题**：如遇下载失败，可重新运行，已下载内容不会重复获取
4. **合法使用**：请确保您的使用符合相关法律法规和平台协议

## 依赖

- Python 3.7+
- requests

安装依赖：
```bash
pip install requests
```

## 常见问题

**Q: 下载速度很慢怎么办？**
A: 工具设置了0.5秒间隔以保护服务器，不建议修改。如需批量下载多部小说，建议排队处理。

**Q: 某些章节下载失败怎么办？**
A: 可能是网络波动或章节被锁定。可重新运行脚本，已下载内容会保留。

**Q: 如何获取书籍ID？**
A: 在番茄小说网页版打开书籍页面，URL中的数字串即为书籍ID。

# 星露谷物语资源工具箱

## 工具介绍

这个项目包含两个工具：

**星露谷Wiki图片批量下载器** - 一键下载游戏素材  
**像素图片无损放大工具** - 无损放大像素图片

## 快速开始

```bash
pip install -r requirements.txt
```

## 星露谷Wiki图片批量下载器

### 功能特性

- **批量下载** - 一次性下载所有游戏素材
- **智能分类** - 按游戏内容自动整理文件夹
- **断点续传** - 重新运行自动跳过已下载文件
- **去重处理** - 避免重复下载

### 使用方法

#### 按需下载（推荐）

```bash
# 下载成就图标（适合做攻略）
python stardew_image_scraper.py -u "https://stardewvalleywiki.com/Category:Achievement_images" -n "成就图标"

# 下载角色头像
python stardew_image_scraper.py -u "https://stardewvalleywiki.com/Category:NPC_images" -n "角色头像"

# 下载作物图片
python stardew_image_scraper.py -u "https://stardewvalleywiki.com/Category:Crop_images" -n "作物图片"

# 自定义线程数（建议不超过4个）
python stardew_image_scraper.py -u "分类URL" -w 2
```

#### 全量下载

```bash
python stardew_image_scraper.py
```

**注意**：全量下载会对服务器造成压力，建议优先使用按需下载。

### 文件结构

程序会创建 `stardew_images` 文件夹，素材按类别整理：

```
stardew_images/
├── Achievement_images/     # 成就图标
│   ├── 星星图标.png
│   └── 奖杯图标.png
├── Animal_images/          # 动物素材
│   ├── 可爱小鸡.png
│   └── 奶牛萌图.png
├── Crop_images/            # 作物图片
│   ├── 玉米.png
│   └── 草莓.png
└── 更多分类...
```

### 命令行参数

- `-d, --download-dir`: 下载文件夹名称（默认stardew_images）
- `-w, --max-workers`: 下载线程数
- `-u, --category-url`: 指定类别URL
- `-n, --category-name`: 指定类别名称

## 像素图片无损放大工具

### 功能介绍

- **像素艺术专用** - 专为像素风格优化
- **批量处理** - 一键处理整个文件夹
- **格式支持** - PNG

### 放大倍数建议

- **偶数倍数**（2倍、4倍、8倍）效果最佳
- **图标、成就** - 4倍或8倍
- **角色头像** - 2倍或4倍
- **大型素材** - 2倍

### 使用方法

#### 命令行模式

```bash
# 🖼️ 放大单张图片（4倍放大）
python pixel_upscaler.py input.png -s 4 -o output.png

# 📁 批量放大整个文件夹（效率神器）
python pixel_upscaler.py input_dir -b -s 2 -o output_dir
```

#### 参数说明
- `input`: 要处理的图片或文件夹路径
- `-o, --output`: 输出位置（不填会自动生成）
- `-s, --scale`: 放大倍数（建议2-8倍）
- `-b, --batch`: 批量模式开关

#### 使用示例

```bash
# 🚀 单图放大4倍（适合头像、图标）
python pixel_upscaler.py sprite.png -s 4

# 💫 批量处理文件夹（创作者必备）
python pixel_upscaler.py sprites/ -b -s 2 -o sprites_upscaled/

# 🎮 处理星露谷素材
python pixel_upscaler.py stardew_images/Achievement\ images/ -b -s 4
```

#### Python代码调用

```python
from pixel_upscaler import PixelUpscaler

# 创建放大器
upscaler = PixelUpscaler()

# 放大单张图片
upscaler.upscale_image(
    'input.png',      # 原图路径
    'output.png',     # 输出路径
    scale_factor=4    # 放大4倍
)

# 批量放大
upscaler.batch_upscale(
    'input_dir',      # 素材文件夹
    'output_dir',     # 输出文件夹
    scale_factor=2    # 放大2倍
)
```
## 完整使用流程

### 推荐流程

```bash
# 下载成就图标
python stardew_image_scraper.py -u "https://stardewvalleywiki.com/Category:Achievement_images" -n "成就图标"

# 放大成就图标
python pixel_upscaler.py "stardew_images/成就图标/" -b -s 4 -o "高清成就图标/"

# 下载并放大角色头像
python stardew_image_scraper.py -u "https://stardewvalleywiki.com/Category:NPC_images" -n "角色头像"
python pixel_upscaler.py "stardew_images/角色头像/" -b -s 2 -o "高清角色头像/"
```

## 项目结构

```
stardew_assets/
├── README.md
├── requirements.txt
├── stardew_image_scraper.py
├── pixel_upscaler.py
└── stardew_images/          # 运行stardew_image_scraper.py后生成
    ├── Achievement images/
    ├── Animal images/
    ├── NPC images/
    ├── Crop images/
    └── Building images/
```

## 常见问题

**Q: 支持哪些图片格式？**  
A: 支持PNG格式

**Q: 放大后画质怎么样？**  
A: 无损放大，保持像素完整

**Q: 最大能放大多少倍？**  
A: 建议2-8倍最佳

## 版权声明

- 游戏素材版权归 **ConcernedApe** 和 **星露谷物语** 官方所有
- 仅供个人学习、研究和非商业创作使用
- 严禁商业用途

## 使用建议

- ✅ 个人攻略制作、学习分享
- ✅ 非盈利的粉丝创作内容
- ❌ 商业游戏开发
- ❌ 素材二次销售
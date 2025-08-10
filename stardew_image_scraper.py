#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 星露谷物语Wiki图片批量下载神器

专为小红书创作者和游戏爱好者打造！
一键下载所有游戏素材，让你的创作更精彩 ✨

功能特色：
🎮 自动获取所有图片分类
📁 智能整理文件夹结构  
⚡ 多线程高速下载
🔄 断点续传不丢失
💎 高清原图质量
"""

import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StardewImageScraper:
    """🎮 星露谷物语图片下载神器
    
    专为创作者设计的智能下载工具，让素材收集变得超简单！
    """
    
    def __init__(self, base_url="https://stardewvalleywiki.com", download_dir="stardew_images", max_workers=4):
        """🚀 初始化下载器
        
        Args:
            base_url: Wiki基础地址
            download_dir: 素材保存文件夹名称
            max_workers: 下载线程数（默认2个，最大4个，避免对服务器造成过大压力）
        """
        self.base_url = base_url
        self.download_dir = Path(download_dir)
        # 限制最大线程数为4，避免对服务器造成过大压力
        self.max_workers = min(max_workers, 4)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.downloaded_images = set()  # 🎯 智能去重，避免重复下载
        self.processed_categories = set()  # 📂 分类记录，提高效率
        self.lock = Lock()  # 🔒 线程安全锁
        
        # 📁 创建素材宝库文件夹
        self.download_dir.mkdir(exist_ok=True)
    
    def get_categories_from_web(self):
        """🌐 从网络智能获取所有图片分类
        
        这是核心功能！自动发现所有素材分类，无需手动操作 ✨
        """
        images_category_url = f"{self.base_url}/Category:Images"
        logger.info(f"🔍 正在获取分类信息: {images_category_url}")
        
        content = self.get_page_content(images_category_url)
        if not content:
            logger.error("❌ 无法获取分类页面内容")
            return []
        
        return self.extract_subcategories_from_content(content)
    
    def parse_local_html(self, html_file_path):
        """解析本地HTML文件，提取所有子分类链接（保留兼容性）"""
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.extract_subcategories_from_content(content)
    
    def extract_subcategories_from_content(self, content):
        """从HTML内容中提取子分类链接"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找Subcategories部分
        subcategories_section = soup.find('div', id='mw-subcategories')
        if not subcategories_section:
            return []
        
        # 提取所有分类链接
        category_links = []
        for link in subcategories_section.find_all('a', href=True):
            href = link['href']
            if href.startswith('/Category:'):
                full_url = urljoin(self.base_url, href)
                category_name = link.get_text().strip()
                category_links.append({
                    'name': category_name,
                    'url': full_url,
                    'path': href
                })
        
        return category_links
    
    def get_page_content(self, url):
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None
    

    
    def get_original_image_url(self, thumbnail_url):
        """从缩略图URL获取原始图片URL"""
        # 移除缩略图参数，如 /120px-filename.png -> /filename.png
        if '/thumb/' in thumbnail_url:
            # 处理缩略图URL格式: /mediawiki/images/thumb/x/xx/filename.png/120px-filename.png
            parts = thumbnail_url.split('/thumb/')
            if len(parts) == 2:
                # 提取原始路径
                thumb_part = parts[1]
                # 找到最后一个/之前的部分
                last_slash = thumb_part.rfind('/')
                if last_slash != -1:
                    original_path = thumb_part[:last_slash]
                    return f"/mediawiki/images/{original_path}"
        
        return thumbnail_url
    
    def extract_filename_from_url(self, url):
        """从URL提取文件名"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        return filename
    
    def download_image(self, image_info, category_dir):
        """下载单张图片（线程安全）"""
        url = image_info['url']
        filename = image_info['filename']
        
        # 线程安全地检查是否已下载
        with self.lock:
            if url in self.downloaded_images:
                return True
        
        file_path = category_dir / filename
        
        # 如果文件已存在，跳过
        if file_path.exists():
            with self.lock:
                self.downloaded_images.add(url)
            return True
        
        try:
            # 创建新的session实例以避免线程冲突
            session = requests.Session()
            session.headers.update(self.session.headers)
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            with self.lock:
                self.downloaded_images.add(url)
            
            logger.info(f"下载成功: {filename}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"下载失败 {filename}: {e}")
            return False
    
    def process_category_recursive(self, category_info, parent_dir=None, depth=0, max_depth=10):
        """递归处理分类，包括子分类，按照树状结构组织目录"""
        category_name = category_info['name']
        category_url = category_info['url']
        
        # 避免重复处理和无限递归
        with self.lock:
            if category_url in self.processed_categories or depth > max_depth:
                return
            self.processed_categories.add(category_url)
        
        indent = "  " * depth
        logger.info(f"{indent}处理分类: {category_name} (深度: {depth})")
        
        # 获取分类页面内容
        content = self.get_page_content(category_url)
        if not content:
            return
        
        # 创建分类目录 - 按照树状结构组织
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', category_name)
        if parent_dir is None:
            # 顶级分类，直接在下载目录下创建
            category_dir = self.download_dir / safe_name
        else:
            # 子分类，在父分类目录下创建
            category_dir = parent_dir / safe_name
        
        category_dir.mkdir(exist_ok=True)
        
        # 提取并下载图片
        images = self.extract_images_from_category_content(content)
        if images:
            logger.info(f"{indent}找到 {len(images)} 张图片，开始并发下载")
            self.download_images_concurrent(images, category_dir)
        
        # 递归处理子分类，传递当前分类目录作为父目录
        subcategories = self.extract_subcategories_from_content(content)
        if subcategories:
            logger.info(f"{indent}找到 {len(subcategories)} 个子分类")
            for subcategory in subcategories:
                self.process_category_recursive(subcategory, category_dir, depth + 1, max_depth)
                time.sleep(0.2)  # 避免请求过于频繁
    
    def extract_images_from_category_content(self, content):
        """从分类页面内容中提取图片链接"""
        soup = BeautifulSoup(content, 'html.parser')
        images = []
        
        # 查找Media in category部分
        media_section = soup.find('div', id='mw-category-media')
        if media_section:
            # 提取gallery中的图片
            gallery = media_section.find('ul', class_='gallery')
            if gallery:
                for img_tag in gallery.find_all('img'):
                    src = img_tag.get('src')
                    if src:
                        # 获取原始图片URL（去掉缩略图参数）
                        original_src = self.get_original_image_url(src)
                        full_url = urljoin(self.base_url, original_src)
                        
                        # 获取图片文件名
                        filename = self.extract_filename_from_url(full_url)
                        
                        images.append({
                            'url': full_url,
                            'filename': filename,
                            'alt': img_tag.get('alt', '')
                        })
        
        return images
    
    def download_images_concurrent(self, images, category_dir):
        """并发下载图片"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交下载任务
            future_to_image = {executor.submit(self.download_image, image_info, category_dir): image_info 
                             for image_info in images}
            
            success_count = 0
            for future in as_completed(future_to_image):
                image_info = future_to_image[future]
                try:
                    if future.result():
                        success_count += 1
                except Exception as exc:
                    logger.error(f"下载图片 {image_info['filename']} 时发生异常: {exc}")
            
            logger.info(f"并发下载完成，成功下载 {success_count}/{len(images)} 张图片")
    
    def download_specific_category(self, category_url, category_name=None):
        """🎯 下载指定类别的图片
        
        Args:
            category_url: 指定的类别URL
            category_name: 类别名称（可选，如果不提供会从URL中提取）
        """
        logger.info(f"🎯 开始下载指定类别: {category_url}")
        
        # 如果没有提供类别名称，从URL中提取
        if not category_name:
            if '/Category:' in category_url:
                category_name = category_url.split('/Category:')[-1].replace('_', ' ')
            else:
                category_name = "SpecificCategory"
        
        # 构造类别信息
        category_info = {
            'name': category_name,
            'url': category_url,
            'path': category_url.replace(self.base_url, '')
        }
        
        # 处理指定类别
        self.process_category_recursive(category_info, parent_dir=None)
        
        logger.info(f"\n指定类别下载完成！")
        logger.info(f"图片下载到目录: {self.download_dir.absolute()}")
        logger.info(f"总共处理了 {len(self.processed_categories)} 个分类")
        logger.info(f"总共下载了 {len(self.downloaded_images)} 张图片")
    
    def run(self, html_file_path=None, specific_category_url=None, category_name=None):
        """主运行函数
        
        Args:
            html_file_path: 本地HTML文件路径（可选）
            specific_category_url: 指定类别URL（可选，用于按需下载）
            category_name: 指定类别名称（可选）
        """
        logger.info(f"开始解析Stardew Valley Wiki图片 (并发数: {self.max_workers})")
        
        # 如果指定了特定类别URL，只下载该类别
        if specific_category_url:
            self.download_specific_category(specific_category_url, category_name)
            return
        
        # 获取所有分类
        if html_file_path and os.path.exists(html_file_path):
            logger.info(f"使用本地HTML文件: {html_file_path}")
            categories = self.parse_local_html(html_file_path)
        else:
            logger.info("从网络获取分类信息")
            categories = self.get_categories_from_web()
        
        if not categories:
            logger.error("未找到任何分类")
            return
        
        logger.info(f"找到 {len(categories)} 个顶级分类，开始递归处理")
        
        # 递归处理每个分类
        for i, category in enumerate(categories, 1):
            logger.info(f"\n=== 进度: {i}/{len(categories)} ===")
            self.process_category_recursive(category, parent_dir=None)
            time.sleep(0.5)  # 分类之间的延迟
        
        logger.info("\n所有分类处理完成！")
        logger.info(f"图片下载到目录: {self.download_dir.absolute()}")
        logger.info(f"总共处理了 {len(self.processed_categories)} 个分类")
        logger.info(f"总共下载了 {len(self.downloaded_images)} 张图片")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🌟 星露谷物语Wiki图片批量下载神器')
    parser.add_argument('--category-url', '-u', help='指定类别URL进行按需下载')
    parser.add_argument('--category-name', '-n', help='指定类别名称（配合--category-url使用）')
    parser.add_argument('--max-workers', '-w', type=int, default=2, help='最大线程数（默认2，最大4）')
    parser.add_argument('--download-dir', '-d', default='stardew_images', help='下载目录（默认stardew_images）')
    parser.add_argument('--html-file', '-f', help='使用本地HTML文件路径')
    
    args = parser.parse_args()
    
    # 创建爬虫实例，默认并发数为4
    scraper = StardewImageScraper(
        download_dir=args.download_dir, 
        max_workers=args.max_workers
    )
    
    # 运行爬虫
    if args.category_url:
        # 按需下载指定类别
        logger.info(f"🎯 按需下载模式：{args.category_url}")
        scraper.download_specific_category(args.category_url, args.category_name)
    else:
        # 全量下载或使用本地HTML文件
        scraper.run(html_file_path=args.html_file)
    
    logger.info("\n✨ 使用示例:")
    logger.info("全量下载: python stardew_image_scraper.py")
    logger.info("按需下载: python stardew_image_scraper.py -u 'https://stardewvalleywiki.com/Category:Achievement_images' -n '成就图标'")
    logger.info("自定义线程数: python stardew_image_scraper.py -w 2")
    logger.info("💡 建议使用按需下载，避免对服务器造成过大压力！")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
像素图片无损放大程序
专门为像素艺术设计，使用最近邻插值算法保持像素的锐利边缘
"""

import os
import argparse
from PIL import Image
from pathlib import Path

class PixelUpscaler:
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
        
    def upscale_image(self, input_path, output_path, scale_factor=2):
        """
        使用最近邻插值放大像素图片
        这是最适合像素艺术的算法，能够保持像素的锐利边缘
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            scale_factor: 放大倍数
        """
        try:
            # 检查输入文件
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            # 检查文件格式
            file_ext = Path(input_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 打开图片
            with Image.open(input_path) as image:
                print(f"原始图片尺寸: {image.size}")
                
                # 计算新尺寸
                width, height = image.size
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # 使用最近邻插值放大 - 最适合像素艺术
                upscaled = image.resize((new_width, new_height), Image.NEAREST)
                
                print(f"放大后图片尺寸: {upscaled.size}")
                
                # 创建输出目录
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # 保存图片
                # 保持原始格式，如果是JPEG则使用高质量设置
                if file_ext.lower() in ['.jpg', '.jpeg']:
                    upscaled.save(output_path, quality=95, optimize=True)
                else:
                    upscaled.save(output_path, optimize=True)
                
                print(f"图片已保存到: {output_path}")
                return True
                
        except Exception as e:
            print(f"处理图片时出错: {e}")
            return False
    
    def batch_upscale(self, input_dir, output_dir, scale_factor=2):
        """
        批量放大目录中的所有图片
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"输入目录不存在: {input_dir}")
            return
        
        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"在目录 {input_dir} 中未找到支持的图片文件")
            return
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        success_count = 0
        for i, img_file in enumerate(image_files, 1):
            print(f"\n处理 {i}/{len(image_files)}: {img_file.name}")
            
            # 构造输出文件路径
            output_file = output_path / f"{img_file.stem}_x{scale_factor}{img_file.suffix}"
            
            if self.upscale_image(str(img_file), str(output_file), scale_factor):
                success_count += 1
        
        print(f"\n批量处理完成！成功处理 {success_count}/{len(image_files)} 个文件")

def main():
    parser = argparse.ArgumentParser(description='像素图片无损放大程序 - 专为像素艺术设计')
    parser.add_argument('input', help='输入图片文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件或目录路径')
    parser.add_argument('-s', '--scale', type=float, default=2.0, help='放大倍数 (默认: 2.0)')
    parser.add_argument('-b', '--batch', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    upscaler = PixelUpscaler()
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input)
        if args.batch or input_path.is_dir():
            output_path = input_path.parent / f"{input_path.name}_upscaled"
        else:
            output_path = input_path.parent / f"{input_path.stem}_x{args.scale}{input_path.suffix}"
    
    # 执行放大
    if args.batch or Path(args.input).is_dir():
        upscaler.batch_upscale(args.input, output_path, args.scale)
    else:
        upscaler.upscale_image(args.input, output_path, args.scale)

if __name__ == "__main__":
    # 如果作为脚本运行，使用命令行参数
    if len(os.sys.argv) > 1:
        main()
    else:
        # 交互式使用示例
        print("像素图片无损放大程序")
        print("专门为像素艺术设计，使用最近邻插值算法")
        print("=" * 40)
        
        upscaler = PixelUpscaler()
        
        # 示例用法
        print("\n使用示例:")
        print("1. 单个文件放大:")
        print("   upscaler.upscale_image('input.png', 'output.png', scale_factor=4)")
        print("\n2. 批量放大:")
        print("   upscaler.batch_upscale('input_dir', 'output_dir', scale_factor=2)")
        print("\n3. 命令行使用:")
        print("   python pixel_upscaler.py input.png -s 4 -o output.png")
        print("   python pixel_upscaler.py input_dir -b -s 2 -o output_dir")
        
        print("\n算法特点:")
        print("- 使用最近邻插值，专门为像素艺术优化")
        print("- 保持像素的锐利边缘，无模糊效果")
        print("- 适合8位/16位游戏图片、像素艺术作品、图标等")
        print("- 轻量级实现，只依赖Pillow库")
# 视频转WEBP工具

这是一个使用Python编写的视频转WEBP工具，它提供了一个图形用户界面（GUI），方便用户将视频文件转换为WEBP动画。

## 功能

- 支持拖放视频文件到应用程序窗口进行转换。
- 内置FFmpeg工具进行视频转码, 不需要在系统安装FFmpeg。
- 多平台, 多线程。

## 安装

### Windows

1. 下载最新的 `video2webp-windows-${version}.exe` 安装包。
2. 双击安装包，按照提示完成安装。

### macOS

1. 下载最新的 `video2webp-macos-${version}.dmg` 安装包。
2. 双击安装包，将 `Video2Webp` 应用程序拖放到 `Applications` 文件夹中。


## 使用方法

1. 启动应用程序。
2. 将视频文件拖放到应用程序窗口中。
3. 点击“转换”按钮开始转换。
4. 转换完成后，WEBP文件将保存在与视频文件相同的目录下。

## 开发

### 环境搭建

1. 安装Python 3.10及以上版本。
2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用程序：
   ```bash
   python gui.py
   ```

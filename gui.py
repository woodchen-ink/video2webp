import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import platform
import os
import webbrowser
from threading import Thread
import traceback

# 设置 FFmpeg 路径
if getattr(sys, "frozen", False):
    # 运行在 PyInstaller 打包后的环境
    ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg")
else:
    # 运行在开发环境
    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")

# 添加到系统 PATH
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]


def get_subprocess_config():
    """获取subprocess配置，用于隐藏控制台窗口"""
    if platform.system().lower() == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return {
            "startupinfo": startupinfo,
            "creationflags": subprocess.CREATE_NO_WINDOW,
        }
    return {}


class VideoToWebpConverter:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("视频或gif转WEBP工具")

        # 设置窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 设置窗口样式
        self.root.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabelframe", background="#f0f0f0")

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        # 显示支持的格式
        supported_formats_label = ttk.Label(
            self.root, text="支持的格式为\"*.mp4 *.avi *.mov *.mkv *.webm *.gif'"
        )
        supported_formats_label.pack(pady=5)
        # 文件选择框
        self.file_frame = ttk.LabelFrame(self.root, text="选择文件")
        self.file_frame.pack(padx=10, pady=5, fill="x")

        self.files_list = tk.Listbox(self.file_frame, height=5)
        self.files_list.pack(padx=5, pady=5, fill="x")

        # 为文件列表添加右键菜单
        self.files_list_menu = tk.Menu(self.root, tearoff=0)
        self.files_list_menu.add_command(label="删除选中", command=self.delete_selected)
        self.files_list_menu.add_command(
            label="清空列表", command=lambda: self.files_list.delete(0, tk.END)
        )

        self.files_list.bind("<Button-3>", self.show_context_menu)

        btn_frame = ttk.Frame(self.file_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        self.select_btn = ttk.Button(
            btn_frame, text="选择视频", command=self.select_files
        )
        self.select_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(
            btn_frame,
            text="清空列表",
            command=lambda: self.files_list.delete(0, tk.END),
        )
        self.clear_btn.pack(side="left", padx=5)

        # 转换设置框
        self.settings_frame = ttk.LabelFrame(self.root, text="转换设置")
        self.settings_frame.pack(padx=10, pady=5, fill="x")

        # 尺寸设置
        size_frame = ttk.Frame(self.settings_frame)
        size_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(size_frame, text="尺寸设置:").pack(side="left", padx=5)
        self.size_var = tk.StringVar(value="original")
        ttk.Radiobutton(
            size_frame, text="保持原始尺寸", variable=self.size_var, value="original"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            size_frame, text="自定义尺寸", variable=self.size_var, value="custom"
        ).pack(side="left", padx=5)

        # 自定义尺寸输入框
        custom_size_frame = ttk.Frame(self.settings_frame)
        custom_size_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(custom_size_frame, text="宽度:").pack(side="left", padx=5)
        self.width_var = tk.StringVar(value="480")
        self.width_entry = ttk.Entry(
            custom_size_frame, textvariable=self.width_var, width=8
        )
        self.width_entry.pack(side="left", padx=5)

        ttk.Label(custom_size_frame, text="高度:").pack(side="left", padx=5)
        self.height_var = tk.StringVar(value="auto")
        self.height_entry = ttk.Entry(
            custom_size_frame, textvariable=self.height_var, width=8
        )
        self.height_entry.pack(side="left", padx=5)

        # FPS设置
        fps_frame = ttk.Frame(self.settings_frame)
        fps_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(fps_frame, text="FPS:").pack(side="left", padx=5)
        self.fps_var = tk.StringVar(value="10")
        self.fps_entry = ttk.Entry(fps_frame, textvariable=self.fps_var, width=8)
        self.fps_entry.pack(side="left", padx=5)

        # 时长控制
        duration_frame = ttk.Frame(self.settings_frame)
        duration_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(duration_frame, text="时长控制(秒):").pack(side="left", padx=5)
        ttk.Label(duration_frame, text="开始时间:").pack(side="left", padx=5)
        self.start_time_var = tk.StringVar(value="0")
        self.start_time_entry = ttk.Entry(
            duration_frame, textvariable=self.start_time_var, width=8
        )
        self.start_time_entry.pack(side="left", padx=5)

        ttk.Label(duration_frame, text="持续时间:").pack(side="left", padx=5)
        self.duration_var = tk.StringVar(value="")
        self.duration_entry = ttk.Entry(
            duration_frame, textvariable=self.duration_var, width=8
        )
        self.duration_entry.pack(side="left", padx=5)
        ttk.Label(duration_frame, text="(留空表示全部)").pack(side="left", padx=5)

        # 质量设置
        quality_frame = ttk.Frame(self.settings_frame)
        quality_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(quality_frame, text="质量设置:").pack(side="left", padx=5)
        self.quality_var = tk.StringVar(value="medium")
        ttk.Radiobutton(
            quality_frame, text="高质量", variable=self.quality_var, value="high"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            quality_frame, text="中等", variable=self.quality_var, value="medium"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            quality_frame, text="低质量", variable=self.quality_var, value="low"
        ).pack(side="left", padx=5)

        # 输出设置
        output_frame = ttk.Frame(self.settings_frame)
        output_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(output_frame, text="输出位置:").pack(side="left", padx=5)
        self.output_var = tk.StringVar(value="same")
        ttk.Radiobutton(
            output_frame, text="与视频相同目录", variable=self.output_var, value="same"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            output_frame, text="自定义目录", variable=self.output_var, value="custom"
        ).pack(side="left", padx=5)

        self.output_path_var = tk.StringVar()
        self.output_path_entry = ttk.Entry(
            output_frame, textvariable=self.output_path_var, width=30
        )
        self.output_path_entry.pack(side="left", padx=5)

        self.browse_btn = ttk.Button(
            output_frame, text="浏览", command=self.browse_output
        )
        self.browse_btn.pack(side="left", padx=5)

        # 转换按钮
        self.convert_btn = ttk.Button(
            self.root, text="开始转换", command=self.start_conversion
        )
        self.convert_btn.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # 状态标签
        self.status_label = ttk.Label(self.root, text="就绪")
        self.status_label.pack(pady=5)

    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.files_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.files_list_menu.grab_release()

    def delete_selected(self):
        """删除选中的文件"""
        selection = self.files_list.curselection()
        for index in reversed(selection):
            self.files_list.delete(index)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path_var.set(directory)

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[
                ("All supported formats", "*.mp4 *.avi *.mov *.mkv *.webm *.gif"),
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"),
                ("GIF files", "*.gif"),
            ]
        )
        self.files_list.delete(0, tk.END)
        for file in files:
            self.files_list.insert(tk.END, file)

    def get_quality_settings(self):
        """根据质量设置返回 FFmpeg 参数"""
        quality = self.quality_var.get()
        if quality == "high":
            return ["-quality", "100"]
        elif quality == "medium":
            return ["-quality", "75"]
        else:
            return ["-quality", "50"]

    def validate_inputs(self):
        """验证输入参数"""
        try:
            # 验证FPS
            fps = int(self.fps_var.get())
            if fps <= 0:
                raise ValueError("FPS必须大于0")

            # 验证时间设置
            start_time = float(self.start_time_var.get() or 0)
            if start_time < 0:
                raise ValueError("开始时间不能为负数")

            if self.duration_var.get():
                duration = float(self.duration_var.get())
                if duration <= 0:
                    raise ValueError("持续时间必须大于0")

            # 验证自定义尺寸
            if self.size_var.get() == "custom":
                width = int(self.width_var.get())
                if width <= 0:
                    raise ValueError("宽度必须大于0")

                height = self.height_var.get()
                if height != "auto":
                    height = int(height)
                    if height <= 0:
                        raise ValueError("高度必须大于0")

            return True
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False

    def convert_to_webp(self, input_path):
        try:
            # 验证输入
            if not self.validate_inputs():
                return False

            # 确定输出路径
            if self.output_var.get() == "same":
                output_dir = os.path.dirname(input_path)
            else:
                output_dir = self.output_path_var.get()
                if not output_dir:
                    raise ValueError("请选择输出目录")

            output_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".webp"
            )

            # 获取设置值
            start_time = float(self.start_time_var.get() or 0)
            duration = self.duration_var.get()
            fps = int(self.fps_var.get())

            # 获取CPU核心数
            cpu_count = os.cpu_count() or 1
            threads = max(1, min(cpu_count - 1, 8))

            # 获取ffmpeg路径
            ffmpeg_exe = os.path.join(
                ffmpeg_path,
                "ffmpeg.exe" if platform.system().lower() == "windows" else "ffmpeg",
            )

            # 检查输入文件类型
            is_gif = input_path.lower().endswith(".gif")

            # 构建命令
            cmd = [ffmpeg_exe, "-y", "-threads", str(threads)]  # 覆盖输出文件

            # 添加输入文件
            cmd.extend(["-i", input_path])

            # 构建滤镜链
            filters = []

            # FPS控制
            if not is_gif or self.fps_var.get() != "10":
                filters.append(f"fps={fps}")

            # 尺寸控制
            if self.size_var.get() == "custom":
                width = int(self.width_var.get())
                height = self.height_var.get()
                height = -1 if height == "auto" else int(height)
                filters.append(f"scale={width}:{height}")

            # 添加滤镜
            if filters:
                cmd.extend(["-vf", ",".join(filters)])

            # 添加编码器选项
            cmd.extend(
                [
                    "-c:v",
                    "libwebp",  # 使用 WebP 编码器
                    "-lossless",
                    "0",  # 使用有损压缩
                    "-compression_level",
                    "4",  # 压缩级别
                    "-preset",
                    "default",  # 使用默认预设
                    "-loop",
                    "0",  # 无限循环
                ]
            )

            # 添加质量设置
            quality = self.quality_var.get()
            if quality == "high":
                cmd.extend(["-qscale", "90"])  # WebP质量0-100
            elif quality == "medium":
                cmd.extend(["-qscale", "75"])
            else:
                cmd.extend(["-qscale", "60"])

            # 规范化输出路径
            output_path = os.path.normpath(output_path)
            cmd.append(output_path)

            # 获取subprocess配置
            subprocess_config = get_subprocess_config()

            # 打印命令用于调试
            print("WebP转换命令:", " ".join(cmd))

            # 更新状态显示
            self.status_label.config(text=f"正在转换... {os.path.basename(input_path)}")
            self.root.update()

            # 运行转换命令
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **subprocess_config
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                error_message = stderr.decode() if stderr else "未知错误"
                raise RuntimeError(f"转换失败:\n{error_message}")

            return True

        except Exception as e:
            error_msg = str(e)
            print(f"Conversion error: {error_msg}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()
            messagebox.showerror("错误", f"转换失败:\n{error_msg}")
            return False

    def start_conversion(self):
        def convert():
            try:
                files = self.files_list.get(0, tk.END)
                if not files:
                    messagebox.showwarning("警告", "请先选择要转换的文件")
                    return

                total = len(files)
                success_count = 0

                for i, file in enumerate(files):
                    current = i + 1
                    self.status_label.config(
                        text=f"正在转换: {os.path.basename(file)} ({current}/{total})"
                    )
                    if self.convert_to_webp(file):  # 使用新的转换函数
                        success_count += 1
                    progress = current / total * 100
                    self.progress["value"] = progress

                self.status_label.config(text=f"转换完成 ({success_count}/{total})")
                self.convert_btn["state"] = "normal"

                if success_count == total:
                    messagebox.showinfo(
                        "完成", f"所有文件转换完成！\n成功转换 {total} 个文件"
                    )
                else:
                    messagebox.showwarning(
                        "完成",
                        f"转换完成，但有部分失败。\n成功：{success_count}/{total}",
                    )

            except Exception as e:
                print(f"Conversion error: {str(e)}")
                traceback.print_exc()
                messagebox.showerror("错误", f"转换过程出错：\n{str(e)}")
            finally:
                self.convert_btn["state"] = "normal"

        self.convert_btn["state"] = "disabled"
        self.progress["value"] = 0
        Thread(target=convert).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        print("程序启动...")

        app = VideoToWebpConverter()
        app.run()
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback

        traceback.print_exc()  # 打印详细错误信息
        sys.exit(1)

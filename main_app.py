import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import shutil

class DirCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("目录和文件复制及重命名工具   20250620  飞歌")
        
        # 设置窗口大小和位置
        window_width = 1056
        window_height = 650
        
        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 计算窗口位置（水平居中，垂直距离上边50像素）
        x = (screen_width - window_width) // 2
        y = 50
        
        # 确保窗口下边框不低于任务栏上边框
        taskbar_height = 40  # 估计任务栏高度
        max_y = screen_height - window_height - taskbar_height
        if y > max_y:
            y = max_y
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口最小尺寸
        self.root.minsize(800, 500)
        
        # 设置默认字体大小（缩小为原来的80%）
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=11)
        
        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(size=11)
        
        # 创建按钮专用的较大字体
        self.button_font = font.Font(family="TkDefaultFont", size=12, weight="bold")
        
        # 创建软件标题字体（二号字体约18磅）
        self.title_font = font.Font(family="华文新魏", size=20, weight="bold")
        
        # 创建加粗标签字体
        self.bold_label_font = font.Font(family="TkDefaultFont", size=11, weight="bold")
        
        # 初始化变量
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.copy_mode = tk.StringVar(value="custom")
        self.export_format = tk.StringVar(value="txt")
        
        # 存储复选框状态
        self.checked_items = set()
        
        # 创建主界面
        self.create_main_interface()
        
    def create_rename_dialog(self, title):
        """创建重命名对话框的通用方法"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        
        dialog_font = ('TkDefaultFont', 10)
        
        ttk.Label(dialog, text="要查找的字符串:", font=dialog_font).pack(pady=5)
        find_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=find_var, font=dialog_font).pack(pady=5)
        
        ttk.Label(dialog, text="替换为:", font=dialog_font).pack(pady=5)
        replace_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=replace_var, font=dialog_font).pack(pady=5)
        
        return dialog, find_var, replace_var
    
    def create_main_interface(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # 配置根窗口和主框架的网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)  # 让第1列（输入框列）可扩展
        
        # 设置样式
        style = ttk.Style()
        style.configure('Treeview', rowheight=30)  # 增加行高以容纳更大的复选框
        style.configure('Treeview.Heading', font=('TkDefaultFont', 10))
        # 配置树形视图的行样式，添加行分隔线
        style.configure('Treeview', background='white', foreground='black')
        style.map('Treeview', background=[('selected', '#E3F2FD')])
        # 设置行间分隔线
        style.configure('Treeview', relief='solid', borderwidth=1)
        style.layout('Treeview.Item', [
            ('Treeitem.padding', {'sticky': 'nswe', 'children': [
                ('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                ('Treeitem.text', {'side': 'left', 'sticky': ''})
            ]})
        ])
        
        # 软件标题
        title_label = tk.Label(main_frame, text="目录和文件复制及重命名工具", 
                              font=self.title_font, fg="#003366")
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # 源目录选择
        source_label = ttk.Label(main_frame, text="请先选择源目录:", font=self.bold_label_font)
        source_label.grid(row=1, column=0, sticky='w')
        ttk.Entry(main_frame, textvariable=self.source_dir).grid(row=1, column=1, padx=5, sticky='ew')
        ttk.Button(main_frame, text="浏览", command=self.select_source).grid(row=1, column=2, padx=5)
        
        # 目标目录选择
        dest_label = ttk.Label(main_frame, text="请选择目标目录:", font=self.bold_label_font)
        dest_label.grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_dir).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(main_frame, text="浏览", command=self.select_dest).grid(row=2, column=2, padx=5, pady=5)
        
        # 复制模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="复制目录结构和导出文件名功能：", padding="5")
        mode_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        
        # 设置LabelFrame标题颜色为蓝色，加粗
        style.configure('Blue.TLabelframe.Label', foreground='blue', font=('TkDefaultFont', 11, 'bold'))
        mode_frame.configure(style='Blue.TLabelframe')
        
        ttk.Radiobutton(mode_frame, text="仅复制一层目录", value="single_level", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(mode_frame, text="复制选定层级目录", value="selected_levels",
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(mode_frame, text="复制所有层级目录", value="all_levels", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=2, padx=10)
        ttk.Radiobutton(mode_frame, text="复制选定目录和文件", value="custom", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=3, padx=10)
        ttk.Radiobutton(mode_frame, text="导出目录和文件的名称", value="export_names", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=4, padx=10)
        files_only_radio = tk.Radiobutton(mode_frame, text="只显示文件", value="files_only", 
                       variable=self.copy_mode, command=self.on_mode_change, foreground="red")
        files_only_radio.grid(row=0, column=5, padx=10)
        
        # 导出格式选择框架
        self.export_format_frame = ttk.LabelFrame(main_frame, text="导出格式", padding="5")
        self.export_format_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Radiobutton(self.export_format_frame, text="TXT格式", value="txt", 
                       variable=self.export_format).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(self.export_format_frame, text="HTML格式", value="html", 
                       variable=self.export_format).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(self.export_format_frame, text="Markdown格式", value="md", 
                       variable=self.export_format).grid(row=0, column=2, padx=10)
        
        # 初始隐藏导出格式选择
        self.export_format_frame.grid_remove()
        
        # 重命名按钮框架
        rename_frame = ttk.Frame(main_frame)
        rename_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=5)
        
        # 添加重命名功能标签（与框架标题字体大小一致，加粗，蓝色）
        rename_label = tk.Label(rename_frame, text="重命名功能:", 
                               font=font.Font(family="TkDefaultFont", size=11, weight="bold"), 
                               fg="blue")
        rename_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(rename_frame, text="本级目录字符替换", command=self.rename_current_level).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(rename_frame, text="全部目录字符替换", command=self.rename_all_items).pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="多维重命名本级目录名", command=self.multi_rename_current_level).pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="多维重命名本级文件名", command=self.multi_rename_current_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="全部目录名修改", command=self.advanced_rename_directories).pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="全部文件名修改", command=self.advanced_rename_files).pack(side=tk.LEFT, padx=5)
        
        # 文件树视图
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=6, column=0, columnspan=4, sticky='nsew', pady=5)
        
        # 修改后的树形视图配置
        self.tree = ttk.Treeview(tree_frame, selectmode='none', height=6)
        self.tree["columns"] = ("checked", "type", "size")
        self.tree.column("#0", width=350)  # 名称列，稍微缩小为大小列腾出空间
        self.tree.column("checked", width=80, anchor='center')  # 增大复选框列宽度
        self.tree.column("type", width=100)  # 类型列
        self.tree.column("size", width=100, anchor='e')  # 大小列，右对齐
        
        # 配置树形视图的标签样式，添加行分隔效果
        self.tree.tag_configure('oddrow', background='#F5F5F5')
        self.tree.tag_configure('evenrow', background='white')
        
        self.tree.heading("#0", text="名称")
        self.tree.heading("checked", text="选择")
        self.tree.heading("type", text="类型")
        self.tree.heading("size", text="大小(K)")
        
        # 添加点击事件绑定
        self.tree.bind('<ButtonRelease-1>', self.on_tree_click)
        
        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局树视图和滚动条
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        

        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        # 创建开始复制按钮，增大字体和尺寸
        start_button = ttk.Button(button_frame, text="开始复制或导出", command=self.start_copy)
        start_button.configure(width=16)  # 增加按钮宽度
        # 为按钮设置样式以应用更大字体和蓝色
        style.configure('Large.TButton', font=self.button_font, foreground='#0066CC')
        start_button.configure(style='Large.TButton')
        start_button.pack(side=tk.LEFT, padx=5, ipady=4)  # 增加按钮高度
        ttk.Button(button_frame, text="取消", command=self.cancel_copy).pack(side=tk.LEFT, padx=5)
        
        # 添加版本信息和作者信息
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=9, column=0, columnspan=4, sticky='ew', pady=5)
        
        # 左下角版本信息
        version_label = tk.Label(info_frame, text="V1.0   2025/06/20", fg="blue", font=('TkDefaultFont', 9))
        version_label.pack(side=tk.LEFT)
        
        # 右下角作者信息
        author_label = tk.Label(info_frame, text="作者：飞歌", fg="blue", font=('TkDefaultFont', 9))
        author_label.pack(side=tk.RIGHT)
        
        # 配置grid权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(6, weight=1)  # 让文件树视图行可扩展
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)  # 让树视图可扩展

    def on_mode_change(self):
        """当复制模式改变时的处理"""
        mode = self.copy_mode.get()
        self.checked_items.clear()  # 清除之前的选择
        
        # 根据模式显示或隐藏导出格式选择
        if mode == "export_names":
            self.export_format_frame.grid()
        else:
            self.export_format_frame.grid_remove()
            
        self.refresh_tree()  # 刷新树形视图
            
    # 修改后的树形视图点击事件处理
    def on_tree_click(self, event):
        """处理树形视图的点击事件"""
        if self.copy_mode.get() not in ["custom", "selected_levels"]:
            return
            
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        column = self.tree.identify_column(event.x)
        # 添加调试日志
        print(f"点击事件 - 列: {column}, 项目: {item}")
        
        if column == "#1":  # 修正：使用 #1 代替 #2
            current_state = self.tree.set(item, "checked")
            new_state = "🔲" if current_state == "✅" else "✅"
            self.tree.set(item, "checked", new_state)
            
            if new_state == "✅":
                self.checked_items.add(item)
            else:
                self.checked_items.discard(item)
                
            # 强制更新显示
            self.tree.update()
                
    def select_all(self):
        """全选"""
        if self.copy_mode.get() in ["custom", "selected_levels"]:
            for item in self.get_all_items():
                self.tree.set(item, "checked", "✅")
                self.checked_items.add(item)
            # 强制更新显示
            self.tree.update()
                
    def deselect_all(self):
        """取消全选"""
        if self.copy_mode.get() in ["custom", "selected_levels"]:
            for item in self.get_all_items():
                self.tree.set(item, "checked", "🔲")
            self.checked_items.clear()
            # 强制更新显示
            self.tree.update()
            
    def get_all_items(self, parent=''):
        """获取所有项目"""
        items = []
        for item in self.tree.get_children(parent):
            items.append(item)
            items.extend(self.get_all_items(item))
        return items
        
    def select_source(self):
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_dir.set(directory)
            self.refresh_tree()
            
    def select_dest(self):
        directory = filedialog.askdirectory(title="选择目标目录")
        if directory:
            self.dest_dir.set(directory)
            
    def refresh_tree(self):
        # 清空树形视图
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checked_items.clear()
            
        # 添加根目录
        source_path = self.source_dir.get()
        if source_path:
            self.add_directory_to_tree('', source_path)
            
    def add_directory_to_tree(self, parent, path):
        try:
            # 检查路径是否可访问
            if not os.access(path, os.R_OK):
                # 如果无法访问，添加一个提示节点
                self.tree.insert(
                    parent, 'end', text=f"[无法访问: {os.path.basename(path)}]",
                    values=("", "受限目录", "N/A")
                )
                return
                
            items = os.listdir(path)
            for item in items:
                full_path = os.path.join(path, item)
                
                # 检查单个项目是否可访问
                try:
                    is_dir = os.path.isdir(full_path)
                    item_type = "目录" if is_dir else "文件"
                    
                    # 根据模式决定是否显示文件
                    mode = self.copy_mode.get()
                    if mode == "files_only":
                        # 只显示文件模式：跳过目录，只显示文件
                        if is_dir:
                            continue
                    elif mode not in ["custom", "export_names"] and not is_dir:
                        continue
                    
                    # 确定是否显示复选框
                    show_checkbox = mode in ["custom", "selected_levels"]
                    if mode == "selected_levels" and not is_dir:
                        show_checkbox = False
                    
                    # 计算大小
                    size_str = self.get_size_in_kb(full_path)
                    
                    # 插入节点
                    item_id = self.tree.insert(
                        parent, 'end', text=item,
                        values=("🔲" if show_checkbox else "", item_type, size_str)
                    )
                    
                    # 添加行分隔样式（奇偶行不同背景色）
                    row_count = len(self.tree.get_children(parent))
                    tag = 'oddrow' if row_count % 2 == 1 else 'evenrow'
                    self.tree.item(item_id, tags=(tag,))
                    
                    # 如果是目录，递归添加子项（files_only模式下不递归）
                    if is_dir and mode != "files_only":
                        self.add_directory_to_tree(item_id, full_path)
                        
                except (PermissionError, OSError) as e:
                    # 单个文件/目录访问失败，跳过但不中断整个过程
                    continue
                    
        except (PermissionError, OSError) as e:
            # 整个目录访问失败
            if parent == '':
                # 如果是根目录访问失败，显示错误消息
                messagebox.showerror("错误", f"无法访问选定的目录:\n{path}\n\n错误信息: {str(e)}\n\n请选择一个有访问权限的目录。")
            else:
                # 子目录访问失败，添加提示节点
                self.tree.insert(
                    parent, 'end', text=f"[无法访问: {os.path.basename(path)}]",
                    values=("", "受限目录", "N/A")
                )
        except Exception as e:
            # 其他未预期的错误
            messagebox.showerror("错误", f"访问目录时出现未知错误: {str(e)}")
            
    def start_copy(self):
        if not self.validate_inputs():
            return
            
        try:
            mode = self.copy_mode.get()
            if mode == "single_level":
                self.copy_single_level()
            elif mode == "selected_levels":
                self.copy_selected_levels()
            elif mode == "all_levels":
                self.copy_all_levels()
            elif mode == "export_names":
                self.export_names()
            else:
                self.copy_custom()
                
            if mode == "export_names":
                messagebox.showinfo("完成", "导出操作完成!")
                pass  # 状态标签已删除
            else:
                messagebox.showinfo("完成", "复制操作完成!")
                pass  # 状态标签已删除
        except Exception as e:
            if self.copy_mode.get() == "export_names":
                messagebox.showerror("错误", f"导出过程中出错:\n{str(e)}")
                pass  # 状态标签已删除
            else:
                messagebox.showerror("错误", f"复制过程中出错:\n{str(e)}")
                pass  # 状态标签已删除
        finally:
            pass
            
    def validate_inputs(self):
        if not self.source_dir.get() or not self.dest_dir.get():
            messagebox.showwarning("警告", "请选择源目录和目标目录!")
            return False
        if self.source_dir.get() == self.dest_dir.get():
            messagebox.showwarning("警告", "源目录和目标目录不能相同!")
            return False
        return True
        
    def copy_single_level(self):
        """仅复制一层目录（空目录）"""
        src = self.source_dir.get()
        dst = self.dest_dir.get()
        dirs = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
        pass
        for i, dir_name in enumerate(dirs):
            os.makedirs(os.path.join(dst, dir_name), exist_ok=True)
            pass
            pass  # 状态标签已删除
            self.root.update()
            
    def copy_selected_levels(self):
        """复制用户勾选的目录（仅结构）"""
        if not self.checked_items:
            messagebox.showwarning("警告", "请选择要复制的目录!")
            return
            
        pass
        
        for i, item_id in enumerate(self.checked_items):
            item_path = self.get_item_path(item_id)
            if not os.path.isdir(item_path):  # 跳过非目录项
                continue
                
            rel_path = os.path.relpath(item_path, self.source_dir.get())
            dst_path = os.path.join(self.dest_dir.get(), rel_path)
            
            try:
                os.makedirs(dst_path, exist_ok=True)
                pass
                pass  # 状态标签已删除
                self.root.update()
            except Exception as e:
                messagebox.showerror("错误", f"创建目录失败: {rel_path}\n{str(e)}")
                
    def copy_all_levels(self):
        """复制完整目录树（空目录）"""
        self.copy_dir_tree(self.source_dir.get(), self.dest_dir.get())
        
    def copy_dir_tree(self, src, dst):
        try:
            os.makedirs(dst, exist_ok=True)
        except (PermissionError, OSError) as e:
            print(f"警告：无法创建目录 {dst}，权限不足: {str(e)}")
            return
        
        try:
            items = os.listdir(src)
        except (PermissionError, OSError) as e:
            print(f"警告：无法访问目录 {src}，权限不足: {str(e)}")
            return
        
        for item in items:
            src_item = os.path.join(src, item)
            try:
                if os.path.isdir(src_item):
                    dst_item = os.path.join(dst, item)
                    self.copy_dir_tree(src_item, dst_item)
            except (PermissionError, OSError) as e:
                print(f"警告：跳过无法访问的目录 {src_item}: {str(e)}")
                continue
            
            pass  # 状态标签已删除
            self.root.update()
                
    def copy_custom(self):
        """自定义复制（允许选择文件和目录）"""
        if not self.checked_items:
            messagebox.showwarning("警告", "请选择要复制的项目!")
            return
            
        pass
        for i, item_id in enumerate(self.checked_items):
            item_path = self.get_item_path(item_id)
            rel_path = os.path.relpath(item_path, self.source_dir.get())
            dst_path = os.path.join(self.dest_dir.get(), rel_path)
            try:
                if os.path.isdir(item_path):
                    shutil.copytree(item_path, dst_path, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(item_path, dst_path)
                pass
                pass  # 状态标签已删除
                self.root.update()
            except Exception as e:
                messagebox.showerror("错误", f"复制失败: {rel_path}\n{str(e)}")
                
    def export_names(self):
        """导出目录和文件名称到指定格式的文档"""
        src = self.source_dir.get()
        dst = self.dest_dir.get()
        export_format = self.export_format.get()
        
        # 生成导出文件名（格式：导出时间+目录名+'目录结构'）
        from datetime import datetime
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = os.path.basename(src)
        filename = f"{current_time}_{source_name}_目录结构.{export_format}"
        output_path = os.path.join(dst, filename)
        
        # 收集目录结构信息
        structure_data = []
        self.collect_structure(src, structure_data, 0)
        
        # 根据格式生成内容
        if export_format == "txt":
            content = self.generate_txt_content(structure_data, source_name)
        elif export_format == "html":
            content = self.generate_html_content(structure_data, source_name)
        elif export_format == "md":
            content = self.generate_md_content(structure_data, source_name)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        pass  # 状态标签已删除
        
    def collect_structure(self, path, structure_data, level=0):
        """递归收集目录结构信息"""
        try:
            # 检查路径是否可访问
            if not os.access(path, os.R_OK):
                structure_data.append({
                    'name': f"[无法访问: {os.path.basename(path)}]",
                    'level': level,
                    'is_dir': False
                })
                return
                
            items = sorted(os.listdir(path))
            for item in items:
                full_path = os.path.join(path, item)
                
                try:
                    # 检查单个项目是否可访问
                    is_dir = os.path.isdir(full_path)
                    structure_data.append({
                        'name': item,
                        'level': level,
                        'is_dir': is_dir
                    })
                    
                    if is_dir:
                        self.collect_structure(full_path, structure_data, level + 1)
                        
                except (PermissionError, OSError):
                    # 单个文件/目录访问失败，添加提示信息但继续处理
                    structure_data.append({
                        'name': f"[无法访问: {item}]",
                        'level': level,
                        'is_dir': False
                    })
                    
        except (PermissionError, OSError):
            # 整个目录访问失败
            structure_data.append({
                'name': f"[无法访问: {os.path.basename(path)}]",
                'level': level,
                'is_dir': False
            })
        except Exception as e:
            # 其他未预期的错误
            structure_data.append({
                'name': f"[错误: {os.path.basename(path)} - {str(e)}]",
                'level': level,
                'is_dir': False
            })
            
    def generate_txt_content(self, structure_data, source_name):
        """生成TXT格式内容"""
        lines = []
        lines.append(f"目录结构导出 - {source_name}")
        lines.append("=" * 50)
        lines.append("")
        
        for item in structure_data:
            indent = "  " * item['level']
            prefix = "📁 " if item['is_dir'] else "📄 "
            lines.append(f"{indent}{prefix}{item['name']}")
            
        return "\n".join(lines)
        
    def generate_html_content(self, structure_data, source_name):
        """生成HTML格式内容"""
        lines = []
        lines.append("<!DOCTYPE html>")
        lines.append("<html lang='zh-CN'>")
        lines.append("<head>")
        lines.append("    <meta charset='UTF-8'>")
        lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        lines.append(f"    <title>目录结构 - {source_name}</title>")
        lines.append("    <style>")
        lines.append("        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }")
        lines.append("        h1 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }")
        lines.append("        .tree { font-family: 'Courier New', monospace; line-height: 1.6; }")
        lines.append("        .folder { color: #007acc; font-weight: bold; }")
        lines.append("        .file { color: #666; }")
        lines.append("        .indent { margin-left: 20px; }")
        lines.append("    </style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append(f"    <h1>目录结构 - {source_name}</h1>")
        lines.append("    <div class='tree'>")
        
        for item in structure_data:
            indent_class = f"indent" if item['level'] > 0 else ""
            style_class = "folder" if item['is_dir'] else "file"
            icon = "📁" if item['is_dir'] else "📄"
            
            indent_style = f"margin-left: {item['level'] * 20}px;"
            lines.append(f"        <div class='{style_class}' style='{indent_style}'>{icon} {item['name']}</div>")
            
        lines.append("    </div>")
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
        
    def generate_md_content(self, structure_data, source_name):
        """生成Markdown格式内容"""
        lines = []
        lines.append(f"# 目录结构 - {source_name}")
        lines.append("")
        lines.append("```")
        
        for item in structure_data:
            indent = "  " * item['level']
            prefix = "📁 " if item['is_dir'] else "📄 "
            lines.append(f"{indent}{prefix}{item['name']}")
            
        lines.append("```")
        lines.append("")
        lines.append(f"*导出时间: {self.get_current_time()}*")
        
        return "\n".join(lines)
        
    def get_current_time(self):
        """获取当前时间字符串"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_item_path(self, item_id):
        path_parts = []
        while item_id:
            path_parts.insert(0, self.tree.item(item_id)['text'])
            item_id = self.tree.parent(item_id)
        return os.path.join(self.source_dir.get(), *path_parts)
        
    def cancel_copy(self):
        if messagebox.askyesno("确认", "确定要取消当前操作吗?"):
            pass  # 状态标签已删除
            pass

    def rename_current_level(self):
        """重命名本级文件夹"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
            
        dialog, find_var, replace_var = self.create_rename_dialog("本级目录字符替换")
        
        def do_rename():
            find_text = find_var.get()
            replace_text = replace_var.get()
            
            if not find_text:
                messagebox.showwarning("警告", "请输入要查找的字符串!")
                return
                
            try:
                source_path = self.source_dir.get()
                renamed_count = 0
                
                for item in os.listdir(source_path):
                    full_path = os.path.join(source_path, item)
                    if os.path.isdir(full_path) and find_text in item:
                        new_name = item.replace(find_text, replace_text)
                        new_path = os.path.join(source_path, new_name)
                        os.rename(full_path, new_path)
                        renamed_count += 1
                
                messagebox.showinfo("完成", f"重命名完成！共重命名 {renamed_count} 个文件夹。")
                dialog.destroy()
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("错误", f"重命名过程中出错:\n{str(e)}")
                
        ttk.Button(dialog, text="确定", command=do_rename).pack(pady=10)

    def rename_all_items(self):
        """重命名所有项目"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
            
        dialog, find_var, replace_var = self.create_rename_dialog("全部目录字符替换")
        
        def do_rename():
            find_text = find_var.get()
            replace_text = replace_var.get()
            
            if not find_text:
                messagebox.showwarning("警告", "请输入要查找的字符串!")
                return
                
            try:
                renamed_count = [0]
                
                def rename_recursive(path):
                    items = os.listdir(path)
                    for item in items:
                        full_path = os.path.join(path, item)
                        if find_text in item:
                            new_name = item.replace(find_text, replace_text)
                            new_path = os.path.join(path, new_name)
                            os.rename(full_path, new_path)
                            renamed_count[0] += 1
                            full_path = new_path
                        
                        if os.path.isdir(full_path):
                            rename_recursive(full_path)
                
                rename_recursive(self.source_dir.get())
                messagebox.showinfo("完成", f"重命名完成！共重命名 {renamed_count[0]} 个项目。")
                dialog.destroy()
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("错误", f"重命名过程中出错:\n{str(e)}")
                
        ttk.Button(dialog, text="确定", command=do_rename).pack(pady=10)

    def multi_rename_current_level(self):
        """批量重命名本级目录"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
            
        # 获取本级目录列表
        source_path = self.source_dir.get()
        directories = []
        try:
            for item in os.listdir(source_path):
                full_path = os.path.join(source_path, item)
                if os.path.isdir(full_path):
                    directories.append(item)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取目录: {str(e)}")
            return
            
        if not directories:
            messagebox.showinfo("提示", "当前目录下没有子目录!")
            return
            
        self.create_multi_rename_dialog(directories)
        
    def multi_rename_current_files(self):
        """批量重命名本级文件"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
            
        # 获取本级文件列表
        source_path = self.source_dir.get()
        files = []
        try:
            for item in os.listdir(source_path):
                full_path = os.path.join(source_path, item)
                if os.path.isfile(full_path):
                    files.append(item)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取目录: {str(e)}")
            return
            
        if not files:
            messagebox.showinfo("提示", "当前目录下没有文件!")
            return
            
        self.create_multi_rename_file_dialog(files)
        
    def create_multi_rename_dialog(self, directories):
        """创建批量重命名对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("多维重命名本级目录名")
        dialog.geometry("1000x300")
        dialog.resizable(False, False)
        
        # 设置对话框位置：水平居中，距上边100像素
        dialog.update_idletasks()  # 确保窗口尺寸已计算
        screen_width = dialog.winfo_screenwidth()
        dialog_width = 1000
        x = (screen_width - dialog_width) // 2
        y = 100
        dialog.geometry(f"{dialog_width}x300+{x}+{y}")
        
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目名称标签
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="项目名称:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        ttk.Label(title_frame, text="前序号").grid(row=0, column=1, padx=(10,30))
        ttk.Label(title_frame, text="前连接符").grid(row=0, column=2, padx=30)
        ttk.Label(title_frame, text="前缀字符").grid(row=0, column=3, padx=30)
        ttk.Label(title_frame, text="原名称").grid(row=0, column=4, padx=(50,30))
        ttk.Label(title_frame, text="后缀字符").grid(row=0, column=6, padx=40)
        ttk.Label(title_frame, text="后连接符").grid(row=0, column=7, padx=20)
        ttk.Label(title_frame, text="后序号").grid(row=0, column=8, padx=20)
        
        # 项目选择复选框
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(select_frame, text="项目选择:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        
        # 创建复选框变量
        self.prefix_num_var = tk.BooleanVar()
        self.prefix_conn_var = tk.BooleanVar()
        self.prefix_text_var = tk.BooleanVar()
        self.suffix_text_var = tk.BooleanVar()
        self.suffix_conn_var = tk.BooleanVar()
        self.suffix_num_var = tk.BooleanVar()
        
        ttk.Checkbutton(select_frame, text="前序号", variable=self.prefix_num_var).grid(row=0, column=1, padx=(10,20))
        ttk.Checkbutton(select_frame, text="前连接符", variable=self.prefix_conn_var).grid(row=0, column=2, padx=(10,20))
        ttk.Checkbutton(select_frame, text="前缀字符", variable=self.prefix_text_var).grid(row=0, column=3, padx=10)
        ttk.Checkbutton(select_frame, text="后缀字符", variable=self.suffix_text_var).grid(row=0, column=6, padx=(180,20))
        ttk.Checkbutton(select_frame, text="后连接符", variable=self.suffix_conn_var).grid(row=0, column=7, padx=20)
        ttk.Checkbutton(select_frame, text="后序号", variable=self.suffix_num_var).grid(row=0, column=8, padx=10)
        
        # 目录新名输入框架
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="目录新名:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        
        # 序号类型选项
        num_options = ["1", "A", "a", "Ⅰ"]
        self.prefix_num_combo = ttk.Combobox(input_frame, values=num_options, width=5, state="readonly")
        self.prefix_num_combo.grid(row=0, column=1, padx=(10,20))
        self.prefix_num_combo.set("1")
        
        # 连接符选项
        conn_options = [".", "_", "-", "–", "—", "•"]
        self.prefix_conn_combo = ttk.Combobox(input_frame, values=conn_options, width=5, state="readonly")
        self.prefix_conn_combo.grid(row=0, column=2, padx=10)
        self.prefix_conn_combo.set(".")
        
        # 前缀文本输入框
        self.prefix_text_entry = ttk.Entry(input_frame, width=12)
        self.prefix_text_entry.grid(row=0, column=3, padx=(20,10))
        
        # 添加说明文字
        note_label = ttk.Label(input_frame, text="+ 目录原名称 +", font=("TkDefaultFont", 10))
        note_label.grid(row=0, column=4, padx=0)
        
        # 后缀文本输入框
        self.suffix_text_entry = ttk.Entry(input_frame, width=12)
        self.suffix_text_entry.grid(row=0, column=6, padx=10)
        
        # 后连接符选项
        self.suffix_conn_combo = ttk.Combobox(input_frame, values=conn_options, width=5, state="readonly")
        self.suffix_conn_combo.grid(row=0, column=7, padx=20)
        self.suffix_conn_combo.set(".")
        
        # 后序号类型选项
        self.suffix_num_combo = ttk.Combobox(input_frame, values=num_options, width=5, state="readonly")
        self.suffix_num_combo.grid(row=0, column=8, padx=10)
        self.suffix_num_combo.set("1")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def do_multi_rename():
            try:
                self.execute_multi_rename(directories)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"重命名过程中出错: {str(e)}")
        
        ttk.Button(button_frame, text="确定", command=do_multi_rename).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
    def execute_multi_rename(self, directories):
        """执行批量重命名"""
        source_path = self.source_dir.get()
        renamed_count = 0
        
        for i, dir_name in enumerate(directories):
            new_name = dir_name
            
            # 构建新名称
            prefix_parts = []
            suffix_parts = []
            
            # 前序号
            if self.prefix_num_var.get():
                num_type = self.prefix_num_combo.get()
                prefix_parts.append(self.generate_sequence_number(i + 1, num_type))
            
            # 前连接符
            if self.prefix_conn_var.get():
                prefix_parts.append(self.prefix_conn_combo.get())
            
            # 前缀字符
            if self.prefix_text_var.get():
                prefix_text = self.prefix_text_entry.get().strip()
                if prefix_text:
                    prefix_parts.append(prefix_text)
            
            # 后缀字符
            if self.suffix_text_var.get():
                suffix_text = self.suffix_text_entry.get().strip()
                if suffix_text:
                    suffix_parts.append(suffix_text)
            
            # 后连接符
            if self.suffix_conn_var.get():
                suffix_parts.append(self.suffix_conn_combo.get())
            
            # 后序号
            if self.suffix_num_var.get():
                num_type = self.suffix_num_combo.get()
                suffix_parts.append(self.generate_sequence_number(i + 1, num_type))
            
            # 组合新名称
            new_name = "".join(prefix_parts) + dir_name + "".join(suffix_parts)
            
            # 执行重命名
            if new_name != dir_name:
                old_path = os.path.join(source_path, dir_name)
                new_path = os.path.join(source_path, new_name)
                
                # 检查新名称是否已存在
                if os.path.exists(new_path):
                    messagebox.showwarning("警告", f"目录 '{new_name}' 已存在，跳过重命名 '{dir_name}'")
                    continue
                
                os.rename(old_path, new_path)
                renamed_count += 1
        
        messagebox.showinfo("完成", f"批量重命名完成！共重命名 {renamed_count} 个目录。")
        self.refresh_tree()
        
    def create_multi_rename_file_dialog(self, files):
        """创建批量文件重命名对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("多维重命名本级文件名")
        dialog.geometry("1000x300")
        dialog.resizable(False, False)
        
        # 设置对话框位置：水平居中，距上边100像素
        dialog.update_idletasks()  # 确保窗口尺寸已计算
        screen_width = dialog.winfo_screenwidth()
        dialog_width = 1000
        x = (screen_width - dialog_width) // 2
        y = 100
        dialog.geometry(f"{dialog_width}x300+{x}+{y}")
        
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目名称标签
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="项目名称:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        ttk.Label(title_frame, text="前序号").grid(row=0, column=1, padx=(10,30))
        ttk.Label(title_frame, text="前连接符").grid(row=0, column=2, padx=30)
        ttk.Label(title_frame, text="前缀字符").grid(row=0, column=3, padx=30)
        ttk.Label(title_frame, text="原名称").grid(row=0, column=4, padx=(50,30))
        ttk.Label(title_frame, text="后缀字符").grid(row=0, column=6, padx=40)
        ttk.Label(title_frame, text="后连接符").grid(row=0, column=7, padx=20)
        ttk.Label(title_frame, text="后序号").grid(row=0, column=8, padx=20)
        
        # 项目选择复选框
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(select_frame, text="项目选择:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        
        # 创建复选框变量（文件重命名用）
        self.file_prefix_num_var = tk.BooleanVar()
        self.file_prefix_conn_var = tk.BooleanVar()
        self.file_prefix_text_var = tk.BooleanVar()
        self.file_suffix_text_var = tk.BooleanVar()
        self.file_suffix_conn_var = tk.BooleanVar()
        self.file_suffix_num_var = tk.BooleanVar()
        
        ttk.Checkbutton(select_frame, text="前序号", variable=self.file_prefix_num_var).grid(row=0, column=1, padx=(10,20))
        ttk.Checkbutton(select_frame, text="前连接符", variable=self.file_prefix_conn_var).grid(row=0, column=2, padx=(10,20))
        ttk.Checkbutton(select_frame, text="前缀字符", variable=self.file_prefix_text_var).grid(row=0, column=3, padx=10)
        ttk.Checkbutton(select_frame, text="后缀字符", variable=self.file_suffix_text_var).grid(row=0, column=6, padx=(180,20))
        ttk.Checkbutton(select_frame, text="后连接符", variable=self.file_suffix_conn_var).grid(row=0, column=7, padx=20)
        ttk.Checkbutton(select_frame, text="后序号", variable=self.file_suffix_num_var).grid(row=0, column=8, padx=10)
        
        # 文件新名输入框架
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="文件新名:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky='w')
        
        # 序号类型选项
        num_options = ["1", "A", "a", "Ⅰ"]
        self.file_prefix_num_combo = ttk.Combobox(input_frame, values=num_options, width=5, state="readonly")
        self.file_prefix_num_combo.grid(row=0, column=1, padx=(10,20))
        self.file_prefix_num_combo.set("1")
        
        # 连接符选项
        conn_options = [".", "_", "-", "–", "—", "•"]
        self.file_prefix_conn_combo = ttk.Combobox(input_frame, values=conn_options, width=5, state="readonly")
        self.file_prefix_conn_combo.grid(row=0, column=2, padx=10)
        self.file_prefix_conn_combo.set(".")
        
        # 前缀文本输入框
        self.file_prefix_text_entry = ttk.Entry(input_frame, width=12)
        self.file_prefix_text_entry.grid(row=0, column=3, padx=(20,10))
        
        # 添加说明文字
        note_label = ttk.Label(input_frame, text="+ 文件原名称 +", font=("TkDefaultFont", 10))
        note_label.grid(row=0, column=4, padx=0)
        
        # 后缀文本输入框
        self.file_suffix_text_entry = ttk.Entry(input_frame, width=12)
        self.file_suffix_text_entry.grid(row=0, column=6, padx=10)
        
        # 后连接符选项
        self.file_suffix_conn_combo = ttk.Combobox(input_frame, values=conn_options, width=5, state="readonly")
        self.file_suffix_conn_combo.grid(row=0, column=7, padx=20)
        self.file_suffix_conn_combo.set(".")
        
        # 后序号类型选项
        self.file_suffix_num_combo = ttk.Combobox(input_frame, values=num_options, width=5, state="readonly")
        self.file_suffix_num_combo.grid(row=0, column=8, padx=10)
        self.file_suffix_num_combo.set("1")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def do_multi_file_rename():
            try:
                self.execute_multi_file_rename(files)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"重命名过程中出错: {str(e)}")
        
        ttk.Button(button_frame, text="确定", command=do_multi_file_rename).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
    def execute_multi_file_rename(self, files):
        """执行批量文件重命名"""
        source_path = self.source_dir.get()
        renamed_count = 0
        
        for i, file_name in enumerate(files):
            # 分离文件名和扩展名
            name_part, ext_part = os.path.splitext(file_name)
            
            # 构建新名称
            prefix_parts = []
            suffix_parts = []
            
            # 前序号
            if self.file_prefix_num_var.get():
                num_type = self.file_prefix_num_combo.get()
                prefix_parts.append(self.generate_sequence_number(i + 1, num_type))
            
            # 前连接符
            if self.file_prefix_conn_var.get():
                prefix_parts.append(self.file_prefix_conn_combo.get())
            
            # 前缀字符
            if self.file_prefix_text_var.get():
                prefix_text = self.file_prefix_text_entry.get().strip()
                if prefix_text:
                    prefix_parts.append(prefix_text)
            
            # 后缀字符
            if self.file_suffix_text_var.get():
                suffix_text = self.file_suffix_text_entry.get().strip()
                if suffix_text:
                    suffix_parts.append(suffix_text)
            
            # 后连接符
            if self.file_suffix_conn_var.get():
                suffix_parts.append(self.file_suffix_conn_combo.get())
            
            # 后序号
            if self.file_suffix_num_var.get():
                num_type = self.file_suffix_num_combo.get()
                suffix_parts.append(self.generate_sequence_number(i + 1, num_type))
            
            # 组合新名称（保留原扩展名）
            new_name = "".join(prefix_parts) + name_part + "".join(suffix_parts) + ext_part
            
            # 执行重命名
            if new_name != file_name:
                old_path = os.path.join(source_path, file_name)
                new_path = os.path.join(source_path, new_name)
                
                # 检查新名称是否已存在
                if os.path.exists(new_path):
                    messagebox.showwarning("警告", f"文件 '{new_name}' 已存在，跳过重命名 '{file_name}'")
                    continue
                
                os.rename(old_path, new_path)
                renamed_count += 1
        
        messagebox.showinfo("完成", f"批量重命名完成！共重命名 {renamed_count} 个文件。")
        self.refresh_tree()
        
    def generate_sequence_number(self, index, num_type):
        """生成序列号"""
        if num_type == "1":
            return str(index)
        elif num_type == "A":
            # 大写字母序列 A, B, C, ..., Z, AA, AB, ...
            result = ""
            while index > 0:
                index -= 1
                result = chr(65 + index % 26) + result
                index //= 26
            return result
        elif num_type == "a":
            # 小写字母序列 a, b, c, ..., z, aa, ab, ...
            result = ""
            while index > 0:
                index -= 1
                result = chr(97 + index % 26) + result
                index //= 26
            return result
        elif num_type == "Ⅰ":
            # 罗马数字
            roman_numerals = [
                (1000, 'Ⅿ'), (900, 'ⅭⅯ'), (500, 'Ⅾ'), (400, 'ⅭⅮ'),
                (100, 'Ⅽ'), (90, 'ⅩⅭ'), (50, 'Ⅼ'), (40, 'ⅩⅬ'),
                (10, 'Ⅹ'), (9, 'Ⅸ'), (5, 'Ⅴ'), (4, 'Ⅳ'), (1, 'Ⅰ')
            ]
            result = ""
            for value, numeral in roman_numerals:
                count = index // value
                result += numeral * count
                index -= value * count
            return result
        else:
            return str(index)
    
    def get_size_in_kb(self, path):
        """获取文件或目录的大小，单位为KB"""
        try:
            if os.path.isfile(path):
                # 文件大小
                size_bytes = os.path.getsize(path)
                size_kb = size_bytes / 1024
                return f"{size_kb:.1f}" if size_kb >= 0.1 else "0.1"
            elif os.path.isdir(path):
                # 目录大小（递归计算所有文件）
                total_size = 0
                try:
                    for dirpath, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except (OSError, IOError):
                                # 跳过无法访问的文件
                                continue
                    size_kb = total_size / 1024
                    return f"{size_kb:.1f}" if size_kb >= 0.1 else "0.1"
                except (OSError, IOError):
                    return "N/A"
            else:
                return "N/A"
        except (OSError, IOError):
            return "N/A"
    
    def advanced_rename_directories(self):
        """全部目录名修改 - 支持通配符和正则表达式"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
        
        # 保存当前模式
        original_mode = self.copy_mode.get()
        # 临时切换到只显示目录的模式
        self.copy_mode.set("single_level")
        # 刷新树形视图以只显示目录
        self.refresh_tree()
        
        # 创建对话框
        self.create_advanced_rename_dialog("全部目录名修改", "directory")
        
        # 恢复原始模式
        self.copy_mode.set(original_mode)
        # 刷新树形视图恢复原始显示
        self.refresh_tree()
    
    def advanced_rename_files(self):
        """全部文件名修改 - 支持通配符和正则表达式"""
        if not self.source_dir.get():
            messagebox.showwarning("警告", "请先选择源目录!")
            return
        
        # 保存当前模式
        original_mode = self.copy_mode.get()
        # 临时切换到显示文件的模式
        self.copy_mode.set("export_names")
        # 刷新树形视图以显示文件
        self.refresh_tree()
        
        # 创建对话框
        self.create_advanced_rename_dialog("全部文件名修改", "file")
        
        # 恢复原始模式
        self.copy_mode.set(original_mode)
        # 刷新树形视图恢复原始显示
        self.refresh_tree()
    
    def create_advanced_rename_dialog(self, title, target_type):
        """创建高级重命名对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("560x600")
        dialog.resizable(False, False)
        
        # 设置对话框位置：水平居中，距上边100像素
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        dialog_width = 560
        x = (screen_width - dialog_width) // 2
        y = 100
        dialog.geometry(f"{dialog_width}x600+{x}+{y}")
        
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text=title, font=("TkDefaultFont", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # 匹配模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="匹配模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        match_mode = tk.StringVar(value="exact")
        ttk.Radiobutton(mode_frame, text="精确匹配", value="exact", variable=match_mode).grid(row=0, column=0, sticky='w', padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="通配符匹配", value="wildcard", variable=match_mode).grid(row=0, column=1, sticky='w', padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="正则表达式", value="regex", variable=match_mode).grid(row=0, column=2, sticky='w')
        
        # 说明文字
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(0, 10))
        
        help_text = (
            "匹配模式说明:\n"
            "• 精确匹配：完全匹配指定字符串\n"
            "• 通配符匹配：支持 * (任意字符) 和 ? (单个字符)\n"
            "• 正则表达式：支持完整的正则表达式语法"
        )
        help_label = ttk.Label(help_frame, text=help_text, font=("TkDefaultFont", 9), foreground="#666666")
        help_label.pack(anchor='w')
        
        # 查找和替换输入
        input_frame = ttk.LabelFrame(main_frame, text="查找和替换", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="查找模式:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        find_var = tk.StringVar()
        find_entry = ttk.Entry(input_frame, textvariable=find_var, width=50)
        find_entry.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(input_frame, text="替换为:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        replace_var = tk.StringVar()
        replace_entry = ttk.Entry(input_frame, textvariable=replace_var, width=50)
        replace_entry.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        
        input_frame.grid_columnconfigure(0, weight=1)
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        case_sensitive = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="区分大小写", variable=case_sensitive).pack(anchor='w')
        
        preview_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="预览模式（仅显示将要修改的项目）", variable=preview_mode).pack(anchor='w')
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 15))
        
        def do_advanced_rename():
            find_pattern = find_var.get()
            replace_text = replace_var.get()
            mode = match_mode.get()
            case_sens = case_sensitive.get()
            preview = preview_mode.get()
            
            if not find_pattern:
                messagebox.showwarning("警告", "请输入查找模式!")
                return
            
            try:
                self.execute_advanced_rename(find_pattern, replace_text, mode, case_sens, preview, target_type)
                if not preview:
                    dialog.destroy()
                    self.refresh_tree()
            except Exception as e:
                messagebox.showerror("错误", f"操作过程中出错:\n{str(e)}")
        
        # 创建按钮并居中显示
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor='center')
        
        ttk.Button(button_container, text="执行", command=do_advanced_rename).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_container, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
    
    def execute_advanced_rename(self, find_pattern, replace_text, mode, case_sensitive, preview_mode, target_type):
        """执行高级重命名操作"""
        import re
        import fnmatch
        
        renamed_items = []
        preview_items = []
        
        def process_directory(path):
            try:
                items = os.listdir(path)
                for item in items:
                    full_path = os.path.join(path, item)
                    is_dir = os.path.isdir(full_path)
                    
                    # 根据目标类型过滤
                    if target_type == "directory" and not is_dir:
                        continue
                    elif target_type == "file" and is_dir:
                        # 对于文件模式，仍需要递归处理目录
                        if is_dir:
                            process_directory(full_path)
                        continue
                    
                    # 匹配检查
                    match_found = False
                    new_name = item
                    
                    if mode == "exact":
                        if case_sensitive:
                            match_found = find_pattern in item
                            new_name = item.replace(find_pattern, replace_text)
                        else:
                            match_found = find_pattern.lower() in item.lower()
                            # 大小写不敏感的替换
                            import re
                            new_name = re.sub(re.escape(find_pattern), replace_text, item, flags=re.IGNORECASE)
                    
                    elif mode == "wildcard":
                        # 将通配符模式转换为正则表达式进行匹配和替换
                        import re
                        
                        # 转换通配符为正则表达式
                        regex_pattern = find_pattern.replace('*', '.*').replace('?', '.')
                        
                        try:
                            flags = 0 if case_sensitive else re.IGNORECASE
                            if re.search(regex_pattern, item, flags):
                                match_found = True
                                # 使用正则表达式进行替换
                                new_name = re.sub(regex_pattern, replace_text, item, flags=flags)
                        except re.error:
                            # 如果正则表达式转换失败，回退到简单匹配
                            if case_sensitive:
                                match_found = fnmatch.fnmatch(item, find_pattern)
                            else:
                                match_found = fnmatch.fnmatch(item.lower(), find_pattern.lower())
                            
                            if match_found:
                                new_name = item.replace(find_pattern, replace_text)
                    
                    elif mode == "regex":
                        try:
                            flags = 0 if case_sensitive else re.IGNORECASE
                            if re.search(find_pattern, item, flags):
                                match_found = True
                                new_name = re.sub(find_pattern, replace_text, item, flags=flags)
                        except re.error as e:
                            raise Exception(f"正则表达式错误: {str(e)}")
                    
                    if match_found and new_name != item:
                        if preview_mode:
                            preview_items.append({
                                'path': full_path,
                                'old_name': item,
                                'new_name': new_name,
                                'type': '目录' if is_dir else '文件'
                            })
                        else:
                            # 检查新名称是否已存在
                            new_path = os.path.join(path, new_name)
                            if not os.path.exists(new_path):
                                os.rename(full_path, new_path)
                                renamed_items.append(item)
                                full_path = new_path  # 更新路径用于递归
                            else:
                                print(f"跳过 {item}：目标名称 {new_name} 已存在")
                    
                    # 递归处理子目录
                    if is_dir:
                        process_directory(full_path)
                        
            except (PermissionError, OSError) as e:
                print(f"无法访问目录 {path}: {str(e)}")
        
        # 开始处理
        process_directory(self.source_dir.get())
        
        if preview_mode:
            if preview_items:
                self.show_preview_dialog(preview_items)
            else:
                messagebox.showinfo("预览结果", "没有找到匹配的项目。")
        else:
            count = len(renamed_items)
            type_name = "目录" if target_type == "directory" else "文件"
            messagebox.showinfo("完成", f"重命名完成！共重命名 {count} 个{type_name}。")
    
    def show_preview_dialog(self, preview_items):
        """显示预览对话框"""
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title("预览重命名结果")
        preview_dialog.geometry("700x400")
        
        # 设置对话框位置
        preview_dialog.update_idletasks()
        screen_width = preview_dialog.winfo_screenwidth()
        dialog_width = 700
        x = (screen_width - dialog_width) // 2
        y = 80
        preview_dialog.geometry(f"{dialog_width}x400+{x}+{y}")
        
        preview_dialog.transient(self.root)
        preview_dialog.grab_set()
        
        main_frame = ttk.Frame(preview_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text=f"将要重命名的项目 (共 {len(preview_items)} 个)", 
                               font=("TkDefaultFont", 11, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 创建树形视图显示预览结果
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_tree = ttk.Treeview(tree_frame, columns=("type", "old_name", "new_name"), show="headings")
        preview_tree.heading("type", text="类型")
        preview_tree.heading("old_name", text="原名称")
        preview_tree.heading("new_name", text="新名称")
        
        preview_tree.column("type", width=80)
        preview_tree.column("old_name", width=250)
        preview_tree.column("new_name", width=250)
        
        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=preview_tree.yview)
        preview_tree.configure(yscrollcommand=v_scrollbar.set)
        
        preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充数据
        for item in preview_items:
            preview_tree.insert("", "end", values=(item['type'], item['old_name'], item['new_name']))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="关闭", command=preview_dialog.destroy).pack(side=tk.RIGHT)

def main():
    root = tk.Tk()
    app = DirCopyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
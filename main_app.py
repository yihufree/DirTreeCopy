import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import shutil

class DirCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("目录和文件及文件名复制工具   20250618  飞歌")
        
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
        self.title_font = font.Font(family="华文新魏", size=18, weight="bold")
        
        # 创建加粗标签字体
        self.bold_label_font = font.Font(family="TkDefaultFont", size=11, weight="bold")
        
        # 初始化变量
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.copy_mode = tk.StringVar(value="single_level")
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
        title_label = tk.Label(main_frame, text="目录和文件及文件名复制工具", 
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
        mode_frame = ttk.LabelFrame(main_frame, text="复制模式", padding="5")
        mode_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Radiobutton(mode_frame, text="仅复制一层目录", value="single_level", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(mode_frame, text="复制选定层级的目录", value="selected_levels",
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(mode_frame, text="复制所有层级目录", value="all_levels", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=2, padx=10)
        ttk.Radiobutton(mode_frame, text="复制选定目录和文件", value="custom", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=3, padx=10)
        ttk.Radiobutton(mode_frame, text="导出目录和文件的名称", value="export_names", 
                       variable=self.copy_mode, command=self.on_mode_change).grid(row=0, column=4, padx=10)
        
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
        
        ttk.Button(rename_frame, text="重命名本级目录", command=self.rename_current_level).pack(side=tk.LEFT, padx=5)
        ttk.Button(rename_frame, text="重命名所有目录", command=self.rename_all_items).pack(side=tk.LEFT, padx=5)
        
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
        version_label = tk.Label(info_frame, text="V1.0   2025/06/18", fg="blue", font=('TkDefaultFont', 9))
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
                    if mode not in ["custom", "export_names"] and not is_dir:
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
                    
                    # 如果是目录，递归添加子项
                    if is_dir:
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
            
        dialog, find_var, replace_var = self.create_rename_dialog("重命名本级文件夹")
        
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
            
        dialog, find_var, replace_var = self.create_rename_dialog("重命名所有项目")
        
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

def main():
    root = tk.Tk()
    app = DirCopyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
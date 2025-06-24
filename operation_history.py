# -*- coding: utf-8 -*-
"""
操作历史管理模块
实现文件和目录操作的历史记录、回退和重做功能
作者：飞歌
日期：20250624
"""

import os
import json
import shutil
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
try:
    from tkinter import messagebox
except ImportError:
    messagebox = None

class OperationHistory:
    """操作历史管理类"""
    
    def __init__(self, max_history_size: int = 50, enable_confirmation: bool = True):
        """初始化操作历史管理器
        
        Args:
            max_history_size: 最大历史记录数量
            enable_confirmation: 是否启用删除确认对话框
        """
        self.max_history_size = max_history_size
        self.history: List[Dict[str, Any]] = []
        self.current_index = -1  # 当前操作位置索引
        self.backup_base_dir = None
        self.enable_confirmation = enable_confirmation
        
    def set_backup_directory(self, backup_dir: str):
        """设置备份目录
        
        Args:
            backup_dir: 备份文件存储目录
        """
        self.backup_base_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """创建文件或目录的备份
        
        Args:
            file_path: 要备份的文件或目录路径
            
        Returns:
            备份文件路径，失败返回None
        """
        if not self.backup_base_dir or not os.path.exists(file_path):
            return None
            
        try:
            # 生成唯一的备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup_name = f"backup_{timestamp}_{os.path.basename(file_path)}"
            backup_path = os.path.join(self.backup_base_dir, backup_name)
            
            if os.path.isfile(file_path):
                shutil.copy2(file_path, backup_path)
            elif os.path.isdir(file_path):
                shutil.copytree(file_path, backup_path)
            
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {str(e)}")
            return None
    
    def add_operation(self, operation_type: str, details: Dict[str, Any]):
        """添加操作记录
        
        Args:
            operation_type: 操作类型 ('rename', 'copy', 'delete', 'move')
            details: 操作详细信息
        """
        # 如果当前不在历史记录末尾，删除后续记录
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # 添加新操作记录
        operation = {
            'id': len(self.history),
            'type': operation_type,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'can_undo': self._can_operation_undo(operation_type, details)
        }
        
        self.history.append(operation)
        self.current_index = len(self.history) - 1
        
        # 限制历史记录数量
        if len(self.history) > self.max_history_size:
            # 删除最旧的记录和对应的备份文件
            old_operation = self.history.pop(0)
            self._cleanup_backup(old_operation)
            self.current_index -= 1
    
    def _can_operation_undo(self, operation_type: str, details: Dict[str, Any]) -> bool:
        """判断操作是否可以撤销
        
        Args:
            operation_type: 操作类型
            details: 操作详细信息
            
        Returns:
            是否可以撤销
        """
        # 重命名操作：检查原文件是否仍存在且新文件存在
        if operation_type == 'rename':
            old_path = details.get('old_path')
            new_path = details.get('new_path')
            return (old_path and new_path and 
                   not os.path.exists(old_path) and 
                   os.path.exists(new_path))
        
        # 复制操作：检查目标文件是否存在
        elif operation_type == 'copy':
            target_path = details.get('target_path')
            return target_path and os.path.exists(target_path)
        
        # 删除操作：检查备份是否存在
        elif operation_type == 'delete':
            backup_path = details.get('backup_path')
            return backup_path and os.path.exists(backup_path)
        
        return False
    
    def can_undo(self) -> bool:
        """检查是否可以撤销
        
        Returns:
            是否可以撤销当前操作
        """
        if self.current_index < 0 or self.current_index >= len(self.history):
            return False
        
        current_operation = self.history[self.current_index]
        return current_operation.get('can_undo', False)
    
    def can_redo(self) -> bool:
        """检查是否可以重做
        
        Returns:
            是否可以重做下一个操作
        """
        return self.current_index < len(self.history) - 1
    
    def undo(self) -> bool:
        """撤销当前操作
        
        Returns:
            撤销是否成功
        """
        if not self.can_undo():
            return False
        
        try:
            operation = self.history[self.current_index]
            success = self._execute_undo(operation)
            
            if success:
                self.current_index -= 1
                return True
        except Exception as e:
            print(f"撤销操作失败: {str(e)}")
        
        return False
    
    def redo(self) -> bool:
        """重做下一个操作
        
        Returns:
            重做是否成功
        """
        if not self.can_redo():
            return False
        
        try:
            next_index = self.current_index + 1
            operation = self.history[next_index]
            success = self._execute_redo(operation)
            
            if success:
                self.current_index = next_index
                return True
        except Exception as e:
            print(f"重做操作失败: {str(e)}")
        
        return False
    
    def _execute_undo(self, operation: Dict[str, Any]) -> bool:
        """执行撤销操作
        
        Args:
            operation: 要撤销的操作记录
            
        Returns:
            撤销是否成功
        """
        op_type = operation['type']
        details = operation['details']
        
        if op_type == 'rename':
            # 重命名撤销：将新名称改回原名称
            old_path = details['old_path']
            new_path = details['new_path']
            
            if os.path.exists(new_path) and not os.path.exists(old_path):
                os.rename(new_path, old_path)
                return True
        
        elif op_type == 'copy':
            # 复制撤销：删除复制的文件
            target_path = details['target_path']
            
            if os.path.exists(target_path):
                # 添加删除确认对话框
                if self.enable_confirmation and messagebox:
                    item_name = os.path.basename(target_path)
                    item_type = "目录" if os.path.isdir(target_path) else "文件"
                    result = messagebox.askyesno(
                        "确认删除", 
                        f"撤销复制操作将删除{item_type}：\n{item_name}\n\n确定要删除吗？",
                        icon='warning'
                    )
                    if not result:
                        return False
                
                if os.path.isfile(target_path):
                    os.remove(target_path)
                elif os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                return True
        
        elif op_type == 'delete':
            # 删除撤销：从备份恢复文件
            original_path = details['original_path']
            backup_path = details['backup_path']
            
            if os.path.exists(backup_path) and not os.path.exists(original_path):
                if os.path.isfile(backup_path):
                    shutil.copy2(backup_path, original_path)
                elif os.path.isdir(backup_path):
                    shutil.copytree(backup_path, original_path)
                return True
        
        return False
    
    def _execute_redo(self, operation: Dict[str, Any]) -> bool:
        """执行重做操作
        
        Args:
            operation: 要重做的操作记录
            
        Returns:
            重做是否成功
        """
        op_type = operation['type']
        details = operation['details']
        
        if op_type == 'rename':
            # 重命名重做：将原名称改为新名称
            old_path = details['old_path']
            new_path = details['new_path']
            
            if os.path.exists(old_path) and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                return True
        
        elif op_type == 'copy':
            # 复制重做：重新执行复制操作
            source_path = details['source_path']
            target_path = details['target_path']
            
            if os.path.exists(source_path) and not os.path.exists(target_path):
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, target_path)
                elif os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path)
                return True
        
        elif op_type == 'delete':
            # 删除重做：重新删除文件
            original_path = details['original_path']
            
            if os.path.exists(original_path):
                # 添加删除确认对话框
                if self.enable_confirmation and messagebox:
                    item_name = os.path.basename(original_path)
                    item_type = "目录" if os.path.isdir(original_path) else "文件"
                    result = messagebox.askyesno(
                        "确认删除", 
                        f"重做删除操作将删除{item_type}：\n{item_name}\n\n确定要删除吗？",
                        icon='warning'
                    )
                    if not result:
                        return False
                
                if os.path.isfile(original_path):
                    os.remove(original_path)
                elif os.path.isdir(original_path):
                    shutil.rmtree(original_path)
                return True
        
        return False
    
    def _cleanup_backup(self, operation: Dict[str, Any]):
        """清理操作对应的备份文件
        
        Args:
            operation: 操作记录
        """
        details = operation.get('details', {})
        backup_path = details.get('backup_path')
        
        if backup_path and os.path.exists(backup_path):
            try:
                if os.path.isfile(backup_path):
                    os.remove(backup_path)
                elif os.path.isdir(backup_path):
                    shutil.rmtree(backup_path)
            except Exception as e:
                print(f"清理备份文件失败: {str(e)}")
    
    def get_history_summary(self) -> List[Dict[str, Any]]:
        """获取历史记录摘要
        
        Returns:
            历史记录摘要列表
        """
        summary = []
        for i, operation in enumerate(self.history):
            summary.append({
                'index': i,
                'type': operation['type'],
                'timestamp': operation['timestamp'],
                'description': self._get_operation_description(operation),
                'can_undo': operation.get('can_undo', False),
                'is_current': i == self.current_index
            })
        return summary
    
    def _get_operation_description(self, operation: Dict[str, Any]) -> str:
        """获取操作描述
        
        Args:
            operation: 操作记录
            
        Returns:
            操作描述字符串
        """
        op_type = operation['type']
        details = operation['details']
        
        if op_type == 'rename':
            old_name = os.path.basename(details.get('old_path', ''))
            new_name = os.path.basename(details.get('new_path', ''))
            return f"重命名: {old_name} → {new_name}"
        
        elif op_type == 'copy':
            source_name = os.path.basename(details.get('source_path', ''))
            target_name = os.path.basename(details.get('target_path', ''))
            return f"复制: {source_name} → {target_name}"
        
        elif op_type == 'delete':
            original_name = os.path.basename(details.get('original_path', ''))
            return f"删除: {original_name}"
        
        return f"未知操作: {op_type}"
    
    def clear_history(self):
        """清空历史记录"""
        # 清理所有备份文件
        for operation in self.history:
            self._cleanup_backup(operation)
        
        self.history.clear()
        self.current_index = -1
    
    def save_to_file(self, file_path: str) -> bool:
        """保存历史记录到文件
        
        Args:
            file_path: 保存文件路径
            
        Returns:
            保存是否成功
        """
        try:
            data = {
                'history': self.history,
                'current_index': self.current_index,
                'backup_base_dir': self.backup_base_dir
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """从文件加载历史记录
        
        Args:
            file_path: 历史记录文件路径
            
        Returns:
            加载是否成功
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.history = data.get('history', [])
            self.current_index = data.get('current_index', -1)
            self.backup_base_dir = data.get('backup_base_dir')
            
            return True
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            return False
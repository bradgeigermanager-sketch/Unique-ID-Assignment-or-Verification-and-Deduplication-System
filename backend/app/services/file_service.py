python
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import UploadFile

class FileService:
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def compute_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """计算文件哈希"""
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def compare_files(self, file1: str, file2: str) -> Dict:
        """比较两个文件"""
        info1 = self._get_file_info(file1)
        info2 = self._get_file_info(file2)
        
        if info1['size'] != info2['size']:
            return {
                "is_same": False,
                "difference_type": "size_mismatch",
                "details": {
                    "file1_size": info1['size'],
                    "file2_size": info2['size']
                }
            }
        
        hash1 = self.compute_hash(file1)
        hash2 = self.compute_hash(file2)
        
        if hash1 == hash2:
            return {
                "is_same": True,
                "difference_type": "identical",
                "hash": hash1
            }
        
        return {
            "is_same": False,
            "difference_type": "content_mismatch",
            "hash1": hash1,
            "hash2": hash2
        }
    
    def _get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        path = Path(file_path)
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "owner": str(stat.st_uid)
        }
    
    def find_duplicates(self, entity_id: str, directory: str) -> List[Dict]:
        """查找重复文件"""
        dir_path = Path(directory) / entity_id
        if not dir_path.exists():
            return []
        
        files = list(dir_path.glob("*"))
        hash_groups = {}
        
        for file in files:
            if file.is_file():
                file_hash = self.compute_hash(str(file))
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append({
                    "path": str(file),
                    "name": file.name,
                    "size": file.stat().st_size
                })
        
        duplicates = []
        for file_hash, file_list in hash_groups.items():
            if len(file_list) > 1:
                duplicates.append({
                    "hash": file_hash,
                    "files": file_list,
                    "count": len(file_list)
                })
        
        return duplicates
    
    def upload_file(self, entity_id: str, file: UploadFile) -> Dict:
        """上传文件"""
        entity_dir = self.upload_dir / entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = entity_dir / file.filename
        with open(file_path, 'wb') as f:
            content = file.file.read()
            f.write(content)
        
        return {
            "status": "success",
            "file_path": str(file_path),
            "hash": self.compute_hash(str(file_path)),
            "size": len(content)
        }

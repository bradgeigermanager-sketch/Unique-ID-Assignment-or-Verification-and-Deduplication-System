#!/usr/bin/env python3
"""Neo4j 数据初始化脚本"""

import os
from neo4j import GraphDatabase
from app.config import get_settings

def run_cypher_script(driver, script_path: str):
    """运行 Cypher 脚本"""
    with open(script_path, 'r', encoding='utf-8') as f:
        script = f.read()
    
    with driver.session() as session:
        result = session.run(script)
        records = list(result)
        return records

def main():
    settings = get_settings()
    
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    
    try:
        print("Starting Neo4j initialization...")
        
        # 运行初始化脚本
        records = run_cypher_script(driver, 'scripts/init_neo4j.cypher')
        
        print(f"Initialization complete. Records: {len(records)}")
        for record in records:
            print(f"  - {record}")
        
    finally:
        driver.close()

if __name__ == "__main__":
    main()

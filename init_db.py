#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建空的数据库和所有必要的表
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base
from app.models import Card, ActivationLog


def init_database():
    """初始化数据库，创建所有表"""
    print("正在初始化数据库...")
    print(f"数据库引擎: {engine.url}")

    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库初始化成功！")
        print(f"✅ 已创建表: {', '.join(Base.metadata.tables.keys())}")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


def check_database():
    """检查数据库和表是否存在"""
    print("\n检查数据库状态...")
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"✅ 数据库已存在，包含以下表: {', '.join(tables)}")

            # 显示每个表的列信息
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                print(f"\n表 '{table_name}' 的列:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
        else:
            print("⚠️  数据库为空，没有表")

        return True
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False


def drop_all_tables():
    """删除所有表（谨慎使用！）"""
    print("\n⚠️  警告：即将删除所有表！")
    confirm = input("确定要继续吗？(yes/no): ")

    if confirm.lower() == 'yes':
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ 已删除所有表")
            return True
        except Exception as e:
            print(f"❌ 删除表失败: {e}")
            return False
    else:
        print("操作已取消")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='MisaCard 数据库管理工具')
    parser.add_argument('action',
                       choices=['init', 'check', 'reset'],
                       help='操作: init(初始化), check(检查), reset(重置)')

    args = parser.parse_args()

    if args.action == 'init':
        init_database()
        check_database()
    elif args.action == 'check':
        check_database()
    elif args.action == 'reset':
        if drop_all_tables():
            init_database()
            check_database()

    print("\n完成！")

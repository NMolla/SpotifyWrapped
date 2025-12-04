#!/usr/bin/env python3
"""Cleanup script for JSON storage."""

import os
import shutil
import json
from datetime import datetime

def cleanup_storage():
    """Clean up the JSON storage directory."""
    
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    print("JSON Storage Cleanup Utility")
    print("=" * 60)
    
    if not os.path.exists(storage_dir):
        print(f"❌ Storage directory not found: {storage_dir}")
        print("   Nothing to clean up!")
        return
    
    print(f"📁 Storage directory: {storage_dir}")
    
    # Analyze storage
    user_count = 0
    file_count = 0
    total_size = 0
    users = []
    
    for user_dir in os.listdir(storage_dir):
        user_path = os.path.join(storage_dir, user_dir)
        if os.path.isdir(user_path):
            user_count += 1
            user_size = 0
            user_files = 0
            
            for file in os.listdir(user_path):
                if file.endswith('.json'):
                    file_count += 1
                    user_files += 1
                    file_path = os.path.join(user_path, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    user_size += file_size
            
            users.append({
                'id': user_dir,
                'files': user_files,
                'size_kb': user_size / 1024
            })
    
    print(f"\n📊 Current Storage Status:")
    print(f"   - Users: {user_count}")
    print(f"   - Total files: {file_count}")
    print(f"   - Total size: {total_size / 1024:.2f} KB")
    
    if users:
        print(f"\n👤 Users:")
        for user in users:
            print(f"   - {user['id']}: {user['files']} files, {user['size_kb']:.2f} KB")
    
    print("\n🔧 Cleanup Options:")
    print("1. Clear all storage (delete everything)")
    print("2. Clear specific user data")
    print("3. Clear old data (>30 days)")
    print("4. View storage details")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        confirm = input("⚠️  This will delete ALL stored data! Are you sure? (yes/no): ").strip().lower()
        if confirm == 'yes':
            shutil.rmtree(storage_dir)
            os.makedirs(storage_dir)
            print("✅ All storage cleared!")
        else:
            print("❌ Cancelled")
    
    elif choice == '2':
        user_id = input("Enter user ID to clear: ").strip()
        user_path = os.path.join(storage_dir, user_id)
        if os.path.exists(user_path):
            confirm = input(f"⚠️  Delete all data for user {user_id}? (yes/no): ").strip().lower()
            if confirm == 'yes':
                shutil.rmtree(user_path)
                print(f"✅ Cleared data for user {user_id}")
            else:
                print("❌ Cancelled")
        else:
            print(f"❌ User {user_id} not found")
    
    elif choice == '3':
        old_count = 0
        old_size = 0
        
        for user_dir in os.listdir(storage_dir):
            user_path = os.path.join(storage_dir, user_dir)
            if os.path.isdir(user_path):
                for file in os.listdir(user_path):
                    if file.endswith('.json'):
                        file_path = os.path.join(user_path, file)
                        
                        # Check file age
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                timestamp = datetime.fromisoformat(data.get('timestamp', ''))
                                age = datetime.now() - timestamp
                                
                                if age.days > 30:
                                    old_count += 1
                                    old_size += os.path.getsize(file_path)
                        except:
                            pass
        
        if old_count > 0:
            print(f"\n📊 Found {old_count} old files ({old_size / 1024:.2f} KB)")
            confirm = input("Delete these old files? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                deleted = 0
                for user_dir in os.listdir(storage_dir):
                    user_path = os.path.join(storage_dir, user_dir)
                    if os.path.isdir(user_path):
                        for file in os.listdir(user_path):
                            if file.endswith('.json'):
                                file_path = os.path.join(user_path, file)
                                
                                try:
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                        timestamp = datetime.fromisoformat(data.get('timestamp', ''))
                                        age = datetime.now() - timestamp
                                        
                                        if age.days > 30:
                                            os.remove(file_path)
                                            deleted += 1
                                            print(f"   Deleted: {file}")
                                except:
                                    pass
                
                print(f"✅ Deleted {deleted} old files")
            else:
                print("❌ Cancelled")
        else:
            print("✅ No old files found (all data is fresh)")
    
    elif choice == '4':
        print("\n📊 Detailed Storage Information:")
        for user_dir in os.listdir(storage_dir):
            user_path = os.path.join(storage_dir, user_dir)
            if os.path.isdir(user_path):
                print(f"\n👤 User: {user_dir}")
                for file in sorted(os.listdir(user_path)):
                    if file.endswith('.json'):
                        file_path = os.path.join(user_path, file)
                        size_kb = os.path.getsize(file_path) / 1024
                        
                        # Get timestamp
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                timestamp = data.get('timestamp', 'unknown')
                                if timestamp != 'unknown':
                                    dt = datetime.fromisoformat(timestamp)
                                    age_days = (datetime.now() - dt).days
                                    print(f"   - {file}: {size_kb:.2f} KB, {age_days} days old")
                                else:
                                    print(f"   - {file}: {size_kb:.2f} KB")
                        except:
                            print(f"   - {file}: {size_kb:.2f} KB")
    
    elif choice == '5':
        print("👋 Exiting...")
    
    else:
        print("❌ Invalid choice")
    
    print("\n" + "=" * 60)
    print("Done!")

if __name__ == "__main__":
    cleanup_storage()

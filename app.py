from flask import Flask, request, jsonify
from flask_cors import CORS
from git import Repo
import os
from dotenv import load_dotenv
import schedule
import time
import threading
import json
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cấu hình
GIT_REPO_PATH = os.getenv('GIT_REPO_PATH')
CONFIG_FILE = 'merge_configs.json'
repo = Repo(GIT_REPO_PATH)

# Lưu trữ cấu hình merge
merge_configs = []

# Hàm đọc cấu hình từ file JSON
def load_configs():
    global merge_configs
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                merge_configs = json.load(f)
            # Lên lại lịch cho các cấu hình
            for config in merge_configs:
                schedule.every().day.at(config['time']).do(
                    perform_merge,
                    config['source_branch'],
                    config['target_branch']
                )
    except Exception as e:
        print(f"Error loading configs: {e}")
        merge_configs = []

# Hàm lưu cấu hình vào file JSON
def save_configs():
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(merge_configs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving configs: {e}")

def perform_merge(source_branch, target_branch):
    try:
        # Checkout target branch
        repo.git.checkout(target_branch)
        repo.git.pull('origin', target_branch)
        
        # Merge source branch
        merge_result = repo.git.merge(source_branch)
        
        if 'CONFLICT' in merge_result:
            # Nếu có conflict, abort merge và trả về lỗi
            repo.git.merge('--abort')
            return {
                'success': False,
                'message': 'Merge conflict detected',
                'details': merge_result
            }
        
        # Push changes
        repo.git.push('origin', target_branch)
        
        return {
            'success': True,
            'message': 'Merge completed successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def run_scheduled_merges():
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/api/configs', methods=['GET'])
def get_configs():
    return jsonify(merge_configs)

@app.route('/api/configs', methods=['POST'])
def add_config():
    config = request.json
    config['id'] = str(uuid.uuid4())
    
    # Đảm bảo định dạng thời gian đúng (HH:MM)
    try:
        time_obj = datetime.strptime(config['time'], '%H:%M')
        config['time'] = time_obj.strftime('%H:%M')
    except ValueError:
        return jsonify({'message': 'Invalid time format. Please use HH:MM format'}), 400
    
    merge_configs.append(config)
    
    # Lên lịch merge
    schedule.every().day.at(config['time']).do(
        perform_merge,
        config['source_branch'],
        config['target_branch']
    )
    
    # Lưu cấu hình vào file
    save_configs()
    
    return jsonify({'message': 'Configuration added successfully'})

@app.route('/api/configs/<config_id>', methods=['DELETE'])
def delete_config(config_id):
    global merge_configs
    config_to_delete = next((config for config in merge_configs if config['id'] == config_id), None)
    
    if config_to_delete:
        # Hủy lịch merge
        schedule.clear()
        
        # Xóa cấu hình
        merge_configs = [config for config in merge_configs if config['id'] != config_id]
        
        # Lên lại lịch cho các cấu hình còn lại
        for config in merge_configs:
            schedule.every().day.at(config['time']).do(
                perform_merge,
                config['source_branch'],
                config['target_branch']
            )
        
        # Lưu cấu hình vào file
        save_configs()
        
        return jsonify({'message': 'Configuration deleted successfully'})
    
    return jsonify({'message': 'Configuration not found'}), 404

@app.route('/api/branches', methods=['GET'])
def get_branches():
    branches = [branch.name for branch in repo.heads]
    return jsonify(branches)

@app.route('/api/merge', methods=['POST'])
def merge_branches():
    data = request.json
    result = perform_merge(data['source_branch'], data['target_branch'])
    return jsonify(result)

if __name__ == '__main__':
    # Đọc cấu hình từ file
    load_configs()
    
    # Khởi động thread chạy lịch merge
    scheduler_thread = threading.Thread(target=run_scheduled_merges)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    app.run(debug=True) 
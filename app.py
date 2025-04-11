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
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cấu hình
GIT_REPO_PATH = os.getenv('GIT_REPO_PATH')
CONFIG_FILE = 'merge_configs.json'
JENKINS_CONFIG_FILE = 'jenkins_config.json'
JENKINS_URL = os.getenv('JENKINS_URL', 'https://jenkins-dev.f88.co')
JENKINS_USERNAME = os.getenv('JENKINS_USERNAME')
JENKINS_TOKEN = os.getenv('JENKINS_TOKEN')
repo = Repo(GIT_REPO_PATH)

# Lưu trữ cấu hình merge
merge_configs = []
jenkins_config = {
    'jenkinsUrl': JENKINS_URL,
    'jenkinsUsername': JENKINS_USERNAME,
    'jenkinsToken': JENKINS_TOKEN
}

# Thêm biến toàn cục để lưu trạng thái tự động merge
auto_merge_enabled = False
auto_merge_interval = 20  # phút
last_merge_time = None

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

# Hàm đọc cấu hình Jenkins từ file JSON
def load_jenkins_config():
    global jenkins_config
    try:
        if os.path.exists(JENKINS_CONFIG_FILE):
            with open(JENKINS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                jenkins_config = json.load(f)
    except Exception as e:
        print(f"Error loading Jenkins config: {e}")
        jenkins_config = {
            'jenkinsUrl': JENKINS_URL,
            'jenkinsUsername': JENKINS_USERNAME,
            'jenkinsToken': JENKINS_TOKEN
        }

# Hàm lưu cấu hình Jenkins vào file JSON
def save_jenkins_config():
    try:
        with open(JENKINS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(jenkins_config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving Jenkins config: {e}")

def perform_merge(source_branch, target_branch):
    try:
        # Pull source branch
        repo.git.checkout(source_branch)
        repo.git.pull('origin', source_branch)
        
        # Checkout và pull target branch
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
        
        # Trigger Jenkins sau khi merge thành công
        try:
            response = requests.post(
                f"{JENKINS_URL}/job/SIT-LOS-UI-V2/build?delay=0sec",
                auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_TOKEN)
            )
            if response.status_code != 201:
                print(f"Failed to trigger Jenkins job. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error triggering Jenkins job: {str(e)}")
        
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

@app.route('/api/branches/local', methods=['GET'])
def get_local_branches():
    try:
        local_branches = [branch.name for branch in repo.branches]
        return jsonify(local_branches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/branches/remote', methods=['GET'])
def get_remote_branches():
    try:
        remote_branches = []
        for remote in repo.remotes:
            remote.fetch()
            for ref in remote.refs:
                if ref.name.startswith('refs/heads/'):
                    branch_name = ref.name.replace('refs/heads/', '')
                    if remote.name != 'origin':
                        branch_name = f"{remote.name}/{branch_name}"
                    remote_branches.append(branch_name)
        return jsonify(remote_branches)
    except Exception as e:
        print(f"Error fetching remote branches: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auto-merge', methods=['POST'])
def toggle_auto_merge():
    global auto_merge_enabled
    data = request.json
    auto_merge_enabled = data.get('enabled', False)
    
    if auto_merge_enabled:
        # Lên lịch merge mỗi 20 phút
        schedule.every(20).minutes.do(run_all_merges)
        return jsonify({'message': 'Auto merge enabled'})
    else:
        # Hủy lịch merge
        schedule.clear()
        # Lên lại lịch cho các cấu hình còn lại
        for config in merge_configs:
            schedule.every().day.at(config['time']).do(
                perform_merge,
                config['source_branch'],
                config['target_branch']
            )
        return jsonify({'message': 'Auto merge disabled'})

@app.route('/api/auto-merge/status', methods=['GET'])
def get_auto_merge_status():
    global auto_merge_enabled, auto_merge_interval, last_merge_time
    return jsonify({
        'enabled': auto_merge_enabled,
        'interval': auto_merge_interval,
        'last_merge_time': last_merge_time.isoformat() if last_merge_time else None
    })

@app.route('/api/auto-merge/interval', methods=['POST'])
def set_auto_merge_interval():
    global auto_merge_enabled, auto_merge_interval
    data = request.json
    new_interval = data.get('interval', 20)
    
    if new_interval < 1:
        return jsonify({'error': 'Interval must be at least 1 minute'}), 400
        
    auto_merge_interval = new_interval
    
    if auto_merge_enabled:
        # Hủy lịch cũ
        schedule.clear()
        # Lên lịch mới
        schedule.every(auto_merge_interval).minutes.do(run_all_merges)
        # Chạy ngay lập tức
        run_all_merges()
    
    return jsonify({'message': f'Auto merge interval set to {auto_merge_interval} minutes'})

def run_all_merges():
    global last_merge_time
    if not auto_merge_enabled:
        return
        
    last_merge_time = datetime.now()
    for config in merge_configs:
        try:
            perform_merge(config['source_branch'], config['target_branch'])
        except Exception as e:
            print(f"Error performing merge for config {config['id']}: {str(e)}")

@app.route('/api/trigger-jenkins', methods=['POST'])
def trigger_jenkins():
    try:
        # Gọi API Jenkins
        response = requests.post(
            f"{JENKINS_URL}/job/SIT-LOS-UI-V2/build?delay=0sec",
            auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_TOKEN)
        )
        
        if response.status_code == 201:
            return jsonify({
                'success': True,
                'message': 'Jenkins job triggered successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to trigger Jenkins job. Status code: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(jenkins_config)

@app.route('/api/settings', methods=['POST'])
def save_settings():
    global jenkins_config
    data = request.json
    jenkins_config = {
        'jenkinsUrl': data.get('jenkinsUrl', JENKINS_URL),
        'jenkinsUsername': data.get('jenkinsUsername', JENKINS_USERNAME),
        'jenkinsToken': data.get('jenkinsToken', JENKINS_TOKEN)
    }
    save_jenkins_config()
    return jsonify({'message': 'Settings saved successfully'})

@app.route('/api/commits', methods=['GET'])
def get_commits():
    try:
        # Lấy danh sách commit gần đây
        commits = []
        for commit in repo.iter_commits('HEAD', max_count=50):
            commits.append({
                'hash': commit.hexsha,
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.isoformat()
            })
        return jsonify(commits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        data = request.json
        branch = data.get('branch')
        if not branch:
            return jsonify({'error': 'Branch name is required'}), 400
            
        repo.git.checkout(branch)
        return jsonify({'message': f'Switched to branch {branch}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/branches/create', methods=['POST'])
def create_branch():
    try:
        data = request.json
        name = data.get('name')
        from_branch = data.get('from')
        
        if not name:
            return jsonify({'error': 'Branch name is required'}), 400
            
        if from_branch:
            repo.git.checkout(from_branch)
            
        repo.git.checkout('-b', name)
        return jsonify({'message': f'Created branch {name}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/branches/delete', methods=['POST'])
def delete_branch():
    try:
        data = request.json
        branch = data.get('branch')
        if not branch:
            return jsonify({'error': 'Branch name is required'}), 400
            
        repo.git.branch('-d', branch)
        return jsonify({'message': f'Deleted branch {branch}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stashes', methods=['GET'])
def get_stashes():
    try:
        stashes = []
        for stash in repo.git.stash('list').split('\n'):
            if stash:
                parts = stash.split(':')
                stashes.append({
                    'id': parts[0],
                    'message': parts[2].strip()
                })
        return jsonify(stashes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stashes/create', methods=['POST'])
def create_stash():
    try:
        data = request.json
        message = data.get('message', '')
        
        if message:
            repo.git.stash('save', message)
        else:
            repo.git.stash('save')
            
        return jsonify({'message': 'Changes stashed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stashes/apply', methods=['POST'])
def apply_stash():
    try:
        data = request.json
        stash_id = data.get('stashId', '0')
        
        repo.git.stash('apply', f'stash@{{{stash_id}}}')
        return jsonify({'message': 'Stash applied successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stashes/drop', methods=['POST'])
def drop_stash():
    try:
        data = request.json
        stash_id = data.get('stashId', '0')
        
        repo.git.stash('drop', f'stash@{{{stash_id}}}')
        return jsonify({'message': 'Stash dropped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pull', methods=['POST'])
def pull():
    try:
        repo.git.pull()
        return jsonify({'message': 'Pulled changes successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/push', methods=['POST'])
def push():
    try:
        repo.git.push()
        return jsonify({'message': 'Pushed changes successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Đọc cấu hình từ file
    load_configs()
    
    # Đọc cấu hình Jenkins từ file
    load_jenkins_config()
    
    # Khởi động thread chạy lịch merge
    scheduler_thread = threading.Thread(target=run_scheduled_merges)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    app.run(debug=True) 
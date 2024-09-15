import os
import subprocess

def create_supervisor_conf(program_name, script_path, log_path):
    conf_content = f"""[program:{program_name}]
command=/home/vectra_telegram_bot/venv/bin/python {script_path}
autostart=true
autorestart=true
directory=/home/vectra_telegram_bot/project_root
environment=PYTHONPATH="/home/vectra_telegram_bot/project_root"
stderr_logfile={log_path}/{program_name}.err.log
stdout_logfile={log_path}/{program_name}.out.log
user={os.getenv('USER')}
"""
    conf_path = f'/etc/supervisor/conf.d/{program_name}.conf'
    with open(conf_path, 'w') as conf_file:
        conf_file.write(conf_content)
    print(f"Конфигурационный файл создан: {conf_path}")

def setup_supervisor_for_bots():
    bot_scripts_dir = "/home/vectra_telegram_bot/project_root/src/bot_scripts"
    log_dir = "/var/log"
    bots = [
        ("first_bot", f"{bot_scripts_dir}/first_bot.py"),
        ("second_bot", f"{bot_scripts_dir}/second_bot.py"),
        ("third_bot", f"{bot_scripts_dir}/third_bot.py"),
        ("designer_bot", f"{bot_scripts_dir}/designer_bot.py"),
    ]
    for bot_name, script_path in bots:
        create_supervisor_conf(bot_name, script_path, log_dir)
    try:
        subprocess.run(["sudo", "supervisorctl", "reread"], check=True)
        subprocess.run(["sudo", "supervisorctl", "update"], check=True)
        print("Supervisor успешно перезапущен и все боты запущены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при перезагрузке Supervisor: {e}")

if __name__ == "__main__":
    os.chdir('/home/vectra_telegram_bot/project_root')
    setup_supervisor_for_bots()

#!/usr/bin/env python3
"""
🤖 AI自动定时推送系统
支持多种AI模型，通过环境变量配置，无需修改代码
"""
import os
import sys
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# ==================== 从环境变量读取配置 ====================

# Push Plus配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

# AI模型配置
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "claude").lower()

# 推送时间配置（可选，默认值已设置）
MORNING_HOUR = int(os.environ.get("MORNING_HOUR", "9"))
NOON_HOUR = int(os.environ.get("NOON_HOUR", "11"))
NOON_MINUTE = int(os.environ.get("NOON_MINUTE", "30"))
EVENING_HOUR = int(os.environ.get("EVENING_HOUR", "18"))
NIGHT_HOUR = int(os.environ.get("NIGHT_HOUR", "2"))

# 各模型的API配置（从环境变量读取API Key）
API_CONFIGS = {
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "api_key": os.environ.get("CLAUDE_API_KEY", ""),
        "model": os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
        "headers": {
            "anthropic-version": "2023-06-01",
            "x-api-key": "",  # 会自动填充
        }
    },
    "openai": {
        "url": os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions"),
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
        "headers": {
            "Authorization": "",  # 会自动填充
        }
    },
    "qwen": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key": os.environ.get("QWEN_API_KEY", ""),
        "model": os.environ.get("QWEN_MODEL", "qwen-plus"),
        "headers": {
            "Authorization": "",  # 会自动填充
        }
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        "headers": {
            "Authorization": "",  # 会自动填充
        }
    },
    "glm": {
        "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key": os.environ.get("GLM_API_KEY", ""),
        "model": os.environ.get("GLM_MODEL", "glm-4-plus"),
        "headers": {
            "Authorization": "",  # 会自动填充
        }
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
        "model": os.environ.get("GEMINI_MODEL", "gemini-pro"),
        "headers": {}
    }
}

# ==================== 启动检查 ====================

def check_config():
    """检查必需的配置是否存在"""
    errors = []
    
    if not PUSHPLUS_TOKEN:
        errors.append("❌ 缺少 PUSHPLUS_TOKEN")
    
    if MODEL_PROVIDER not in API_CONFIGS:
        errors.append(f"❌ 不支持的模型: {MODEL_PROVIDER}")
    elif not API_CONFIGS[MODEL_PROVIDER]["api_key"]:
        errors.append(f"❌ 缺少 {MODEL_PROVIDER.upper()}_API_KEY")
    
    if errors:
        print("=" * 50)
        print("⚠️  配置错误，请在Railway环境变量中设置:")
        for error in errors:
            print(error)
        print("=" * 50)
        sys.exit(1)
    
    return True

# ==================== 核心功能 ====================

def call_ai_model(prompt):
    """
    调用AI模型生成内容
    支持多种模型API，自动适配不同格式
    """
    config = API_CONFIGS[MODEL_PROVIDER]
    
    try:
        if MODEL_PROVIDER == "claude":
            # Claude API格式
            headers = config["headers"].copy()
            headers["x-api-key"] = config["api_key"]
            headers["content-type"] = "application/json"
            
            data = {
                "model": config["model"],
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(config["url"], headers=headers, json=data, timeout=30)
            result = response.json()
            return result["content"][0]["text"]
            
        elif MODEL_PROVIDER == "gemini":
            # Gemini API格式（特殊）
            url = f"{config['url']}?key={config['api_key']}"
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            response = requests.post(url, json=data, timeout=30)
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
            
        else:
            # OpenAI兼容格式 (openai, qwen, deepseek, glm)
            headers = config["headers"].copy()
            headers["Authorization"] = f"Bearer {config['api_key']}"
            headers["Content-Type"] = "application/json"
            
            data = {
                "model": config["model"],
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(config["url"], headers=headers, json=data, timeout=30)
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
    except Exception as e:
        return f"AI调用失败: {str(e)}"


def send_wechat(title, content):
    """通过Push Plus发送微信消息"""
    try:
        r = requests.get(
            "http://www.pushplus.plus/send",
            params={
                "token": PUSHPLUS_TOKEN,
                "title": title,
                "content": content,
                "template": "html"
            },
            timeout=10
        )
        result = r.json()
        if result.get("code") == 200:
            print(f"[{datetime.now()}] ✅ 发送成功: {title}")
            return True
        else:
            print(f"[{datetime.now()}] ❌ 发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 发送出错: {str(e)}")
        return False


# ==================== 定时任务 ====================

def morning_push():
    """早上9点 - 早安问候"""
    prompt = """现在是早上9点，请生成一条温暖的早安问候消息给猫猫。

要求：
- 简短亲切，2-3句话
- 包含对新一天的美好祝愿
- 可以提醒吃早餐、保持好心情
- 语气要温柔可爱

直接输出消息内容即可，不要有多余的解释。"""

    content = call_ai_model(prompt)
    send_wechat("早安，猫猫！☀️", content)


def noon_push():
    """中午11:30 - 午餐提醒"""
    prompt = """现在是中午11:30，请生成一条午餐提醒消息给猫猫。

要求：
- 简短温馨，2-3句话
- 提醒该吃午饭了
- 可以建议饮食健康、劳逸结合
- 语气要关心体贴

直接输出消息内容即可，不要有多余的解释。"""

    content = call_ai_model(prompt)
    send_wechat("该吃午饭啦！🍱", content)


def evening_push():
    """晚上6点 - 晚餐提醒"""
    prompt = """现在是晚上6点，请生成一条晚餐提醒消息给猫猫。

要求：
- 简短温暖，2-3句话
- 提醒该吃晚饭了
- 可以建议放松休息、准备晚上的活动
- 语气要轻松愉快

直接输出消息内容即可，不要有多余的解释。"""

    content = call_ai_model(prompt)
    send_wechat("晚餐时间到！🍜", content)


def night_push():
    """凌晨2点 - 睡觉提醒"""
    prompt = """现在是凌晨2点，猫猫可能还在熬夜。请生成一条温柔的催眠提醒消息。

要求：
- 简短关心，2-3句话
- 提醒该睡觉了，熬夜伤身体
- 语气要温柔但坚定
- 可以营造安心入睡的氛围

直接输出消息内容即可，不要有多余的解释。"""

    content = call_ai_model(prompt)
    send_wechat("该睡觉啦！🌙", content)


# ==================== 主程序 ====================

def main():
    """启动定时任务"""
    # 检查配置
    check_config()
    
    print("=" * 50)
    print("🤖 自动推送服务已启动")
    print(f"📱 使用模型: {MODEL_PROVIDER.upper()}")
    print(f"⏰ 推送时间:")
    print(f"   早安: {MORNING_HOUR:02d}:00")
    print(f"   午餐: {NOON_HOUR:02d}:{NOON_MINUTE:02d}")
    print(f"   晚餐: {EVENING_HOUR:02d}:00")
    print(f"   睡觉: {NIGHT_HOUR:02d}:00")
    print("=" * 50)
    
    # 创建调度器
    scheduler = BlockingScheduler()
    
    # 添加定时任务（使用环境变量配置的时间）
    scheduler.add_job(morning_push, CronTrigger(hour=MORNING_HOUR, minute=0))
    scheduler.add_job(noon_push, CronTrigger(hour=NOON_HOUR, minute=NOON_MINUTE))
    scheduler.add_job(evening_push, CronTrigger(hour=EVENING_HOUR, minute=0))
    scheduler.add_job(night_push, CronTrigger(hour=NIGHT_HOUR, minute=0))
    
    print(f"✅ 定时任务已设置完成")
    print(f"💤 等待推送时间到来...")
    print()
    
    # 启动调度器
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 服务已停止")


if __name__ == "__main__":
    main()

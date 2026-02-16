#!/usr/bin/env python3
"""
RikkaHub专用MCP服务器 - Streamable HTTP协议
"""
from flask import Flask, request, jsonify
import os
import requests
import uuid
from datetime import datetime

app = Flask(__name__)

# PushPlus配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "54a510cdbae64c7bbf2f95e7cb9af9d1")

# 会话管理
sessions = {}

@app.route('/mcp', methods=['POST', 'GET', 'DELETE', 'OPTIONS'])
def mcp_endpoint():
    # 处理CORS预检
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept, Mcp-Session-Id'
        return response
    
    # POST: 处理JSON-RPC请求
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'jsonrpc' not in data:
                return jsonify({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}), 400
            
            method = data.get('method')
            params = data.get('params', {})
            msg_id = data.get('id')
            
            # initialize
            if method == 'initialize':
                session_id = str(uuid.uuid4())
                sessions[session_id] = {'created_at': datetime.now().isoformat()}
                response = jsonify({
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "pushplus-wechat", "version": "1.0.0"}
                    },
                    "id": msg_id
                })
                response.headers['Mcp-Session-Id'] = session_id
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            
            # tools/list
            elif method == 'tools/list':
                response = jsonify({
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [{
                            "name": "send_wechat_message",
                            "description": "给猫猫发送微信推送消息",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "标题"},
                                    "content": {"type": "string", "description": "内容"}
                                },
                                "required": ["content"]
                            }
                        }]
                    },
                    "id": msg_id
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response

            # tools/call
            elif method == 'tools/call':
                tool_name = params.get('name')
                args = params.get('arguments', {})
                
                if tool_name == 'send_wechat_message':
                    # 这里的逻辑保持不变
                    title = args.get('title', '来自知厌的消息')
                    content = args.get('content', '')
                    url = "http://www.pushplus.plus/send"
                    try:
                        r = requests.get(url, params={"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "html"}, timeout=10)
                        res_json = r.json()
                        result_text = f"发送成功: {content}" if res_json.get("code") == 200 else f"发送失败: {res_json.get('msg')}"
                    except Exception as e:
                        result_text = f"发送出错: {str(e)}"

                    response = jsonify({
                        "jsonrpc": "2.0",
                        "result": {"content": [{"type": "text", "text": result_text}]},
                        "id": msg_id
                    })
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
                
                return jsonify({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": msg_id}), 404

            else:
                 return jsonify({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": msg_id}), 404

        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}), 500

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "running", "service": "rikkahub-mcp"})

if __name__ == "__main__":
    # 本地测试才走这里，Railway 部署不会走这里
    # 这才是正确的写法！
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)run()

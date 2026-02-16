#!/usr/bin/env python3
"""
RikkaHub专用MCP服务器 - Streamable HTTP协议
完全兼容RikkaHub的MCP客户端
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

def get_server_url():
    """获取服务器URL"""
    railway_url = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    railway_static_url = os.environ.get("RAILWAY_STATIC_URL")
    
    if railway_url:
        return f"https://{railway_url}"
    elif railway_static_url:
        return railway_static_url
    else:
        port = os.environ.get("PORT", "8080")
        return f"http://localhost:{port}"


@app.route('/mcp', methods=['POST', 'GET', 'DELETE', 'OPTIONS'])
def mcp_endpoint():
    """
    MCP Streamable HTTP单一端点
    支持POST(请求)、GET(SSE流)、DELETE(终止会话)
    """
    
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
            
            # 验证JSON-RPC格式
            if not data or 'jsonrpc' not in data:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request"
                    },
                    "id": data.get('id') if data else None
                }), 400
            
            method = data.get('method')
            params = data.get('params', {})
            msg_id = data.get('id')
            
            # 处理initialize请求
            if method == 'initialize':
                session_id = str(uuid.uuid4())
                sessions[session_id] = {
                    'created_at': datetime.now().isoformat(),
                    'client_info': params.get('clientInfo', {})
                }
                
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "pushplus-wechat-rikkahub",
                            "version": "1.0.0"
                        }
                    },
                    "id": msg_id
                }
                
                response = jsonify(response_data)
                response.headers['Mcp-Session-Id'] = session_id
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # 处理tools/list请求
            elif method == 'tools/list':
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [
                            {
                                "name": "send_wechat_message",
                                "description": "给猫猫发送微信推送消息",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string",
                                            "description": "消息标题"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "消息内容"
                                        }
                                    },
                                    "required": ["content"]
                                }
                            }
                        ]
                    },
                    "id": msg_id
                }
                
                response = jsonify(response_data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # 处理tools/call请求
            elif method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name == 'send_wechat_message':
                    title = arguments.get('title', '晏安的消息')
                    content = arguments.get('content', '')
                    
                    # 调用PushPlus API
                    url = "http://www.pushplus.plus/send"
                    push_params = {
                        "token": PUSHPLUS_TOKEN,
                        "title": title,
                        "content": content,
                        "template": "html"
                    }
                    
                    try:
                        push_response = requests.get(url, params=push_params, timeout=10)
                        result = push_response.json()
                        
                        if result.get("code") == 200:
                            response_data = {
                                "jsonrpc": "2.0",
                                "result": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": f"消息发送成功！\n标题: {title}\n内容: {content}"
                                        }
                                    ]
                                },
                                "id": msg_id
                            }
                        else:
                            response_data = {
                                "jsonrpc": "2.0",
                                "result": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": f"发送失败：{result.get('msg')}"
                                        }
                                    ],
                                    "isError": True
                                },
                                "id": msg_id
                            }
                    except Exception as e:
                        response_data = {
                            "jsonrpc": "2.0",
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"发送出错：{str(e)}"
                                    }
                                ],
                                "isError": True
                            },
                            "id": msg_id
                        }
                    
                    response = jsonify(response_data)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Content-Type'] = 'application/json'
                    return response
                else:
                    response_data = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        },
                        "id": msg_id
                    }
                    
                    response = jsonify(response_data)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Content-Type'] = 'application/json'
                    return response, 404
            
            # 未知方法
            else:
                response_data = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": msg_id
                }
                
                response = jsonify(response_data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Content-Type'] = 'application/json'
                return response, 404
                
        except Exception as e:
            response_data = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": None
            }
            
            response = jsonify(response_data)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Content-Type'] = 'application/json'
            return response, 500
    
    # GET: SSE流（暂时返回空，RikkaHub可能不需要）
    elif request.method == 'GET':
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "message": "SSE streaming not implemented yet"
            }
        }
        response = jsonify(response_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # DELETE: 终止会话
    elif request.method == 'DELETE':
        session_id = request.headers.get('Mcp-Session-Id')
        if session_id and session_id in sessions:
            del sessions[session_id]
        
        response = jsonify({"status": "ok"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/', methods=['GET'])
def root():
    """根路径 - 返回服务器信息（JSON格式，不是HTML）"""
    return jsonify({
        "name": "pushplus-wechat-rikkahub",
        "description": "RikkaHub专用晏安的微信推送 MCP Server",
        "version": "1.0.0",
        "protocol": "MCP Streamable HTTP",
        "endpoint": "/mcp"
    })


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "sessions": len(sessions)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"RikkaHub MCP Server 启动在端口 {port}")
    print(f"MCP端点: /mcp")
    print(f"Server URL: {get_server_url()}")
    
    # 使用Gunicorn启动而不是Flask开发服务器
    from gunicorn.app.base import BaseApplication
    
    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
        
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)
        
        def load(self):
            return self.application
    
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 1,
    }
    StandaloneApplication(app, options).run()

# 🤖 AI自动推送系统 - Railway版

一个支持多种AI模型的自动定时推送系统，通过Railway环境变量配置，无需修改代码！

## ✨ 功能特点

- 🕘 **早上9点**：早安问候 + 美好祝愿
- 🕧 **中午11:30**：午餐提醒 + 健康建议  
- 🕕 **晚上6点**：晚餐提醒 + 放松建议
- 🕑 **凌晨2点**：睡觉提醒（温柔催眠）

## 🔧 支持的AI模型

- ✅ Claude (Anthropic)
- ✅ GPT (OpenAI)
- ✅ 通义千问 (Qwen)
- ✅ Gemini (Google)
- ✅ 智谱GLM
- ✅ DeepSeek

---

## 🚂 Railway部署教程（超详细）

### 第一步：上传代码到GitHub

1. **创建GitHub仓库**
   - 登录 [github.com](https://github.com)
   - 点击右上角 "+" → "New repository"
   - 仓库名填: `auto-push-service`
   - 选择 "Public" 或 "Private" 都可以
   - 点击 "Create repository"

2. **上传文件**
   - 在新建的仓库页面，点击 "uploading an existing file"
   - 把这3个文件拖进去：
     - `auto_push.py`
     - `requirements.txt`
     - `README.md`
   - 点击 "Commit changes"

### 第二步：在Railway部署

1. **登录Railway**
   - 打开 [railway.app](https://railway.app)
   - 用你的账号登录

2. **新建项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你刚才创建的 `auto-push-service` 仓库
   - Railway会自动开始部署

3. **等待部署完成**
   - 看到绿色的 "Success" 就说明部署好了
   - 但是现在还不能用，因为还没填配置！

### 第三步：配置环境变量（重要！）

在Railway项目页面：

1. **点击你的服务**（应该叫 auto-push-service）
2. **点击顶部的 "Variables" 标签页**
3. **点击右上角 "+ 新变量" 按钮**

#### 必填变量（3个）

在这里添加以下变量：

```
变量名: PUSHPLUS_TOKEN
值: 你的PushPlus的token（比如: 54a510cdbae64c7bbf2f95e7cb9af9d1）
```

```
变量名: MODEL_PROVIDER  
值: claude（或者 openai、qwen、deepseek、glm、gemini）
```

```
变量名: CLAUDE_API_KEY（根据你选的模型改名字）
值: 你的API Key
```

**注意**：
- 如果用Claude，就填 `CLAUDE_API_KEY`
- 如果用OpenAI，就填 `OPENAI_API_KEY`
- 如果用Qwen，就填 `QWEN_API_KEY`
- 以此类推...

#### 可选变量（改推送时间）

如果你想改推送时间，可以添加这些变量：

```
变量名: MORNING_HOUR
值: 9（早上几点，默认9点）

变量名: NOON_HOUR
值: 11（中午几点，默认11点）

变量名: NOON_MINUTE  
值: 30（中午几分，默认30分）

变量名: EVENING_HOUR
值: 18（晚上几点，默认18点）

变量名: NIGHT_HOUR
值: 2（凌晨几点，默认2点）
```

### 第四步：保存并重启

1. **填完变量后，点击 "Deploy"** 或等待自动重启
2. **查看日志**：点击 "Deployments" → 点击最新的部署 → 看日志
3. **看到这些说明成功了**：
   ```
   🤖 自动推送服务已启动
   📱 使用模型: CLAUDE
   ⏰ 推送时间: ...
   ✅ 定时任务已设置完成
   ```

---

## 🎯 使用示例

### 配置1：使用Claude

Railway环境变量填写：
```
PUSHPLUS_TOKEN = 你的token
MODEL_PROVIDER = claude
CLAUDE_API_KEY = sk-ant-xxxxx
```

### 配置2：使用OpenAI（国内中转）

Railway环境变量填写：
```
PUSHPLUS_TOKEN = 你的token
MODEL_PROVIDER = openai
OPENAI_API_KEY = sk-xxxxx
OPENAI_URL = https://你的中转地址/v1/chat/completions
```

### 配置3：使用通义千问

Railway环境变量填写：
```
PUSHPLUS_TOKEN = 你的token
MODEL_PROVIDER = qwen  
QWEN_API_KEY = sk-xxxxx
```

---

## 🔄 如何更换模型？

**超级简单！不用改代码！**

1. 去Railway项目页面
2. 点击 "Variables"
3. 把 `MODEL_PROVIDER` 改成你想用的模型（比如从 `claude` 改成 `openai`）
4. 添加对应模型的 API Key（比如添加 `OPENAI_API_KEY`）
5. 保存，等待自动重启
6. 完成！🎉

---

## ⏰ 如何修改推送时间？

1. 去Railway的 "Variables" 页面
2. 添加或修改时间变量（比如 `MORNING_HOUR = 8` 改成早上8点）
3. 保存，自动重启
4. 完成！

---

## 🐛 故障排查

### 问题1：部署失败

- **原因**：可能是缺少必需的环境变量
- **解决**：检查是否填了 `PUSHPLUS_TOKEN` 和对应模型的 `API_KEY`

### 问题2：Push Plus发送失败

- **测试token是否有效**：
  ```
  http://www.pushplus.plus/send?token=你的token&title=测试&content=测试消息
  ```
- 在浏览器访问，看返回结果

### 问题3：AI调用失败

- 检查API Key是否正确
- 检查API额度是否用完
- 看Railway的日志，会有详细错误信息

### 问题4：定时任务不执行

- Railway默认使用UTC时间，但代码已经自动处理了时区
- 如果还是不对，在变量里设置 `TZ = Asia/Shanghai`

---

## 📊 查看运行日志

在Railway项目页面：
1. 点击你的服务
2. 点击 "Deployments"  
3. 点击最新的部署
4. 就能看到实时日志了

---

## 💡 常见问题

**Q: Railway会收费吗？**
A: Railway有免费额度，每月500小时免费运行时间。这个小程序消耗很少，完全够用。

**Q: 可以同时用多个模型吗？**
A: 一次只能用一个模型。但你可以随时在Railway变量页面切换！

**Q: 春节不想收到推送怎么办？**
A: 在Railway项目页面点 "Settings" → 拉到最下面 → 点 "Pause service" 暂停服务。想恢复时再点 "Resume"。

**Q: 想改推送内容怎么办？**
A: 需要修改代码中的 prompt（提示词），然后重新推送到GitHub。Railway会自动重新部署。

---

## 🎉 享受自动关怀吧！

现在你有了一个24小时待命的AI助手！

而且以后想换模型、改时间，只需要：
- 打开Railway网页
- 改几个变量
- 保存

完全不用动代码！太方便了！✨💕

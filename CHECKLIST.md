# ✅ 部署检查清单

## 📦 文件清单

### 重新部署需要替换的文件

#### 核心文件（必须替换）✅

- [ ] `telegram_client.py` - 智能实体查找
- [ ] `add_target.py` - 支持连续添加
- [ ] `deploy.sh` - 集成配置向导
- [ ] `README.md` - 完整文档
- [ ] `QUICKSTART.md` - 快速开始

#### 新增文件（必须上传）🆕

- [ ] `setup_targets.py` - 配置向导（核心）
- [ ] `list_groups.py` - 群组查找工具
- [ ] `DEPLOYMENT_SUMMARY.md` - 部署说明
- [ ] `CHECKLIST.md` - 本文件

#### 可选文件（建议更新）📄

- [ ] `checkin.py` - 如已支持多目标可不换
- [ ] `config.py` - 如已支持多目标可不换
- [ ] `MULTI_TARGET_GUIDE.md` - 文档更新

#### 保留文件（绝对不要替换）❌

- [ ] `.env` - 你的配置
- [ ] `telegram_session.session*` - 登录会话
- [ ] `*.log` - 日志文件

---

## 🚀 部署步骤检查

### 第一步：准备工作

- [ ] 已获取 Telegram API 凭证（API_ID, API_HASH）
- [ ] 已准备好手机号（包含国际区号，如 +86）
- [ ] 已知道要签到的机器人/群组名称
- [ ] 服务器可以访问 Telegram（无墙）

### 第二步：备份现有配置（如果是更新）

```bash
mkdir -p ~/telegram-backup
cp .env ~/telegram-backup/
cp telegram_session.session* ~/telegram-backup/ 2>/dev/null || true
```

- [ ] 已备份 `.env` 文件
- [ ] 已备份 session 文件

### 第三步：停止服务（如果正在运行）

```bash
sudo systemctl stop telegram-auto-checkin
```

- [ ] 服务已停止

### 第四步：上传文件

- [ ] 已上传所有必需文件到服务器
- [ ] 文件权限正确

### 第五步：运行部署

```bash
chmod +x deploy.sh
./deploy.sh
```

- [ ] deploy.sh 有执行权限
- [ ] 虚拟环境创建成功
- [ ] Python 依赖安装成功
- [ ] API 凭证配置完成
- [ ] 签到目标配置完成

### 第六步：首次登录

```bash
source venv/bin/activate
python test_login.py
```

- [ ] 收到验证码
- [ ] 验证码输入成功
- [ ] 两步验证通过（如启用）
- [ ] Session 文件已生成

### 第七步：测试签到

```bash
python manual_checkin.py
```

- [ ] 所有目标签到成功
- [ ] 无错误信息
- [ ] 日志正常

### 第八步：设置服务

```bash
sudo ./setup_service.sh
```

- [ ] systemd 服务创建成功
- [ ] 服务启动成功
- [ ] 开机自启已设置

### 第九步：验证运行

```bash
sudo systemctl status telegram-auto-checkin
```

- [ ] 服务状态：`active (running)`
- [ ] 无错误信息
- [ ] 日志正常输出

---

## 🔧 后续操作检查

### 添加新签到目标

```bash
cd ~/telegram-auto-checkin
source venv/bin/activate
python add_target.py
python manual_checkin.py
sudo systemctl restart telegram-auto-checkin
```

- [ ] 新目标添加成功
- [ ] 配置已保存到 .env
- [ ] 测试签到成功
- [ ] 服务已重启

---

## 🛠️ 工具使用检查

### 列出群组工具

```bash
python list_groups.py
```

- [ ] 能看到所有群组列表
- [ ] 显示群组名称和 ID
- [ ] 显示所有机器人

### 查看按钮工具

```bash
python test_buttons.py
```

- [ ] 能看到机器人的按钮
- [ ] 按钮文字显示清晰

### 测试群组工具

```bash
python test_group.py
```

- [ ] 能向群组发送消息
- [ ] 能查看群组回复

---

## 📊 配置验证检查

### .env 文件检查

```bash
cat .env
```

必需配置项：
- [ ] `API_ID` - 已填写，是纯数字
- [ ] `API_HASH` - 已填写，32位字符串
- [ ] `PHONE_NUMBER` - 已填写，包含 +
- [ ] `CHECKIN_TARGETS` - 已配置，JSON 格式正确

可选配置项：
- [ ] `CHECKIN_HOUR` - 签到小时（0-23）
- [ ] `CHECKIN_MINUTE` - 签到分钟（0-59）
- [ ] `TIMEZONE` - 时区设置
- [ ] `RANDOM_DELAY_MIN` - 最小延迟
- [ ] `RANDOM_DELAY_MAX` - 最大延迟

### 目标配置检查

每个签到目标应包含：
- [ ] `name` - 显示名称
- [ ] `target` - 目标标识（@username / 群组名 / ID）
- [ ] `command` - 签到命令
- [ ] `button_text` - 按钮文字（可为空）

---

## 🔍 日志检查

### 程序日志

```bash
tail -f auto_checkin.log
```

- [ ] 日志文件存在
- [ ] 无 ERROR 级别日志
- [ ] 调度器正常运行
- [ ] 显示下次签到时间

### 签到历史

```bash
cat checkin_history.log
```

- [ ] 文件存在
- [ ] 记录了签到历史
- [ ] 时间戳正确

### 系统日志

```bash
sudo journalctl -u telegram-auto-checkin -n 20
```

- [ ] 服务日志正常
- [ ] 无错误信息
- [ ] 启动信息正确

---

## 🎯 功能测试检查

### 多目标签到

- [ ] 能配置多个目标（2个以上）
- [ ] 每个目标独立配置
- [ ] 按钮/命令方式可混用
- [ ] 所有目标都能签到成功

### 按钮点击

- [ ] 能发送命令显示按钮
- [ ] 能识别按钮文字
- [ ] 能成功点击按钮
- [ ] 能接收点击后的回复

### 文本命令

- [ ] 能发送文本命令
- [ ] 能接收机器人回复

### 群组签到

- [ ] 能识别群组名称
- [ ] 能在群组中发送消息
- [ ] 能接收群组回复

### 定时调度

- [ ] 定时任务已设置
- [ ] 时间配置正确
- [ ] 随机延迟正常

---

## 🛡️ 安全检查

- [ ] `.env` 文件权限正确（不对外公开）
- [ ] Session 文件已备份
- [ ] 未将敏感信息提交到 Git
- [ ] API 凭证保密

---

## 📱 退出前最终检查

```bash
# 1. 服务状态
sudo systemctl status telegram-auto-checkin
```
- [ ] 显示 `active (running)`

```bash
# 2. 查看进程
ps aux | grep main.py
```
- [ ] 进程存在

```bash
# 3. 查看最新日志
tail -20 auto_checkin.log
```
- [ ] 无错误

```bash
# 4. 测试能否自动重启
sudo systemctl restart telegram-auto-checkin
sudo systemctl status telegram-auto-checkin
```
- [ ] 重启成功

---

## ✅ 全部完成

如果以上所有项目都打勾 ✅，恭喜你！

**可以安全退出 SSH 了！**

```bash
exit
```

服务会在后台持续运行，每天自动签到。

---

## 🆘 故障排查快速参考

### 找不到群组
```bash
python list_groups.py  # 查看所有群组
```

### 找不到按钮
```bash
python test_buttons.py  # 查看所有按钮
```

### 签到失败
```bash
python manual_checkin.py  # 手动测试
tail -f auto_checkin.log  # 查看详细日志
```

### 服务异常
```bash
sudo systemctl status telegram-auto-checkin  # 查看状态
sudo journalctl -u telegram-auto-checkin -n 50  # 查看日志
sudo systemctl restart telegram-auto-checkin  # 重启服务
```

### 配置错误
```bash
python -c "import config; print('配置正确')"  # 验证配置
python setup_targets.py  # 重新配置
```

---

**📝 建议：打印或保存此清单，按步骤逐项检查！**

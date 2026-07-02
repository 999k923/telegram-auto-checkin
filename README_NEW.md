# Telegram 自动签到 - 统一管理控制台

> 本项目已在主菜单统一管理下重构。原始脚本保留不变，所有操作通过 `manager.py` 入口完成。

## 快速开始

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动统一管理控制台
python manager.py
```

## 功能一览

| 选项 | 功能 | 原脚本 |
|------|------|--------|
| 1 | 一键安装/部署 | deploy.sh + install.sh |
| 2 | 配置签到目标（增/删/改/查） | setup_targets.py + add_target.py |
| 3 | 登录验证测试 | test_login.py |
| 4 | 列出群组和机器人 | list_groups.py |
| 5 | 查看机器人按钮 | test_buttons.py |
| 6 | 测试群组签到 | test_group.py |
| 7 | 手动执行签到 | manual_checkin.py |
| 8 | 服务管理（启动/停止/重启/状态） | run.sh + stop.sh |
| 9 | 安装 systemd 系统服务 | setup_service.sh |
| 10 | 查看日志 | - |
| 11 | 查看签到历史 | - |
| 12 | 编辑签到时间配置 | - |
| 13 | 备份配置 | - |
| 14 | 恢复配置 | - |
| 15 | 一键卸载 | uninstall.sh |

## 核心逻辑不变

- `main.py` — 定时签到调度器
- `checkin.py` — 签到逻辑
- `telegram_client.py` — Telegram 客户端
- `config.py` — 配置管理
- `.env` — 环境变量（自动维护）

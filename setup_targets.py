"""
交互式配置签到目标 - 支持添加无限个目标
用于首次部署时配置
"""
import json
import os
from pathlib import Path


def add_single_target():
    """添加单个签到目标"""
    print("\n" + "=" * 60)
    print("配置签到目标")
    print("=" * 60)
    
    # 显示名称
    name = input("\n1️⃣  显示名称 (如: @okemby_bot 或 Cloud Cat Group): ").strip()
    if not name:
        print("❌ 名称不能为空")
        return None
    
    # 目标标识
    print("\n2️⃣  目标标识:")
    print("   • 机器人: 使用 @username 格式 (如: @okemby_bot)")
    print("   • 群组: 使用完整群组名称 (如: Cloud Cat Group)")
    print("   • 或使用 ID (如: -1001234567890)")
    print("   提示: 运行 'python list_groups.py' 可查看所有群组")
    target = input("   输入目标: ").strip()
    if not target:
        print("❌ 目标不能为空")
        return None
    
    # 签到命令
    print("\n3️⃣  签到命令:")
    print("   常用命令: /start, /checkin, /signin, /daily")
    command = input("   输入命令 (默认: /start): ").strip()
    if not command:
        command = "/start"
    
    # 签到方式
    print("\n4️⃣  签到方式:")
    print("   [1] 按钮点击 - 发送命令后点击按钮")
    print("   [2] 文本命令 - 直接发送命令即可")
    method = input("   选择方式 (1/2, 默认: 1): ").strip()
    
    button_text = ""
    if method != "2":
        print("\n5️⃣  按钮文字:")
        print("   常见按钮: 签到, 打卡, Check in, 每日签到")
        print("   提示: 运行 'python test_buttons.py' 可查看机器人的所有按钮")
        button_text = input("   输入按钮文字: ").strip()
    
    # 创建目标对象
    target_config = {
        'name': name,
        'target': target,
        'command': command,
        'button_text': button_text
    }
    
    # 预览
    print("\n" + "-" * 60)
    print("配置预览:")
    print(f"  名称: {target_config['name']}")
    print(f"  目标: {target_config['target']}")
    print(f"  命令: {target_config['command']}")
    print(f"  方式: {'按钮点击 - ' + target_config['button_text'] if target_config['button_text'] else '文本命令'}")
    print("-" * 60)
    
    confirm = input("\n确认添加此目标? (y/n, 默认: y): ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ 已取消")
        return None
    
    return target_config


def setup_all_targets():
    """配置所有签到目标"""
    print("\n" + "=" * 60)
    print("🎯 Telegram 自动签到 - 目标配置向导")
    print("=" * 60)
    print("\n欢迎使用！此工具将帮助您配置签到目标。")
    print("您可以添加无限个机器人或群组。")
    
    targets = []
    target_count = 0
    
    while True:
        target_count += 1
        
        if target_count == 1:
            print(f"\n配置第 {target_count} 个签到目标:")
        else:
            print(f"\n当前已配置 {len(targets)} 个目标。")
            add_more = input(f"是否添加第 {target_count} 个签到目标? (y/n, 默认: n): ").strip().lower()
            if add_more != 'y':
                break
        
        target = add_single_target()
        if target:
            targets.append(target)
            print(f"\n✅ 第 {len(targets)} 个目标已添加!")
        else:
            print("\n⚠️  未添加目标，继续...")
            continue
    
    if not targets:
        print("\n❌ 未配置任何签到目标")
        return False
    
    # 显示所有目标
    print("\n" + "=" * 60)
    print("📋 配置汇总")
    print("=" * 60)
    print(f"\n共配置 {len(targets)} 个签到目标:\n")
    
    for idx, t in enumerate(targets):
        print(f"{idx + 1}. {t['name']}")
        print(f"   目标: {t['target']}")
        print(f"   命令: {t['command']}")
        print(f"   方式: {'按钮 - ' + t['button_text'] if t['button_text'] else '命令'}")
        print()
    
    # 确认保存
    print("-" * 60)
    final_confirm = input("确认保存配置? (y/n, 默认: y): ").strip().lower()
    if final_confirm and final_confirm != 'y':
        print("\n❌ 已取消，未保存配置")
        return False
    
    # 保存到 .env
    return save_targets_to_env(targets)


def save_targets_to_env(targets):
    """保存目标配置到 .env 文件"""
    env_file = Path('.env')
    
    # 读取现有内容
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # 查找是否已有 CHECKIN_TARGETS
    targets_line_idx = None
    for idx, line in enumerate(lines):
        if line.startswith('CHECKIN_TARGETS='):
            targets_line_idx = idx
            break
    
    # 生成 JSON 配置
    json_config = json.dumps(targets, ensure_ascii=False)
    new_line = f'CHECKIN_TARGETS={json_config}\n'
    
    # 更新或添加配置
    if targets_line_idx is not None:
        # 替换现有行
        lines[targets_line_idx] = new_line
    else:
        # 查找合适的位置插入（在 PHONE_NUMBER 后面）
        insert_idx = None
        for idx, line in enumerate(lines):
            if line.startswith('PHONE_NUMBER='):
                insert_idx = idx + 1
                break
        
        if insert_idx is not None:
            lines.insert(insert_idx, '\n')
            lines.insert(insert_idx + 1, '# 签到目标配置（可配置多个）\n')
            lines.insert(insert_idx + 2, new_line)
        else:
            # 没找到 PHONE_NUMBER，添加到末尾
            lines.append('\n# 签到目标配置\n')
            lines.append(new_line)
    
    # 注释掉旧的单目标配置（如果存在）
    for idx, line in enumerate(lines):
        if line.startswith('BOT_USERNAME=') or \
           line.startswith('CHECKIN_COMMAND=') or \
           line.startswith('CHECKIN_BUTTON_TEXT='):
            if not line.startswith('#'):
                lines[idx] = '# (已迁移到 CHECKIN_TARGETS) ' + line
    
    # 保存
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("\n" + "=" * 60)
        print("✅ 配置已成功保存到 .env 文件!")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\n❌ 保存失败: {e}")
        return False


def main():
    """主函数"""
    success = setup_all_targets()
    
    if success:
        print("\n📝 下一步操作:")
        print("-" * 60)
        print("1. 查看所有群组和机器人:")
        print("   python list_groups.py")
        print()
        print("2. 测试签到配置:")
        print("   python manual_checkin.py")
        print()
        print("3. 如需修改配置:")
        print("   • 重新运行: python setup_targets.py")
        print("   • 或手动编辑: nano .env")
        print()
        print("4. 设置定时任务:")
        print("   sudo ./setup_service.sh")
        print("-" * 60)
    else:
        print("\n提示: 可以随时运行 'python setup_targets.py' 重新配置")


if __name__ == '__main__':
    main()

"""
交互式添加签到目标工具 - 支持连续添加多个
"""
import json
import os
from pathlib import Path


def load_current_targets():
    """加载当前的签到目标"""
    env_file = Path('.env')
    if not env_file.exists():
        return [], None, []
    
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    targets = []
    targets_line_idx = None
    
    # 查找 CHECKIN_TARGETS
    for idx, line in enumerate(lines):
        if line.startswith('CHECKIN_TARGETS='):
            targets_line_idx = idx
            try:
                json_str = line.split('=', 1)[1].strip()
                targets = json.loads(json_str)
            except:
                pass
            break
        elif line.startswith('BOT_USERNAME='):
            # 旧版单目标配置
            bot_username = line.split('=', 1)[1].strip()
            command = '/start'
            button_text = ''
            
            for l in lines:
                if l.startswith('CHECKIN_COMMAND='):
                    command = l.split('=', 1)[1].strip()
                elif l.startswith('CHECKIN_BUTTON_TEXT='):
                    button_text = l.split('=', 1)[1].strip()
            
            if bot_username:
                targets.append({
                    'name': bot_username,
                    'target': bot_username,
                    'command': command,
                    'button_text': button_text
                })
    
    return targets, targets_line_idx, lines


def display_targets(targets):
    """显示当前所有目标"""
    if not targets:
        print("\n当前没有配置任何签到目标")
        return
    
    print(f"\n当前已配置 {len(targets)} 个签到目标：")
    print("-" * 60)
    for idx, target in enumerate(targets):
        print(f"{idx + 1}. {target['name']}")
        print(f"   目标: {target['target']}")
        print(f"   命令: {target['command']}")
        print(f"   方式: {'按钮 - ' + target['button_text'] if target['button_text'] else '文本命令'}")
        print()


def add_single_target():
    """添加单个目标"""
    print("\n" + "=" * 60)
    print("添加新的签到目标")
    print("=" * 60)
    
    name = input("\n1️⃣  显示名称 (如: Cloud Cat Group): ").strip()
    if not name:
        print("❌ 名称不能为空")
        return None
    
    print("\n2️⃣  目标标识:")
    print("   • 机器人: @username (如: @okemby_bot)")
    print("   • 群组: 完整名称 (如: Cloud Cat Group)")
    print("   • 或使用 ID (如: -1001234567890)")
    print("   💡 提示: 运行 'python list_groups.py' 查看所有群组")
    target = input("   输入目标: ").strip()
    if not target:
        print("❌ 目标不能为空")
        return None
    
    print("\n3️⃣  签到命令 (如: /start, /checkin):")
    command = input("   输入命令 (默认: /checkin): ").strip()
    if not command:
        command = "/checkin"
    
    print("\n4️⃣  签到方式:")
    print("   [1] 按钮点击 - 发送命令后点击按钮")
    print("   [2] 文本命令 - 直接发送命令")
    use_button = input("   选择方式 (1/2, 默认: 2): ").strip()
    
    button_text = ""
    if use_button == '1':
        print("\n5️⃣  按钮文字 (如: 签到, 打卡):")
        print("   💡 运行 'python test_buttons.py' 查看机器人按钮")
        button_text = input("   输入按钮文字: ").strip()
    
    return {
        'name': name,
        'target': target,
        'command': command,
        'button_text': button_text
    }


def save_targets(targets, lines, targets_line_idx):
    """保存目标配置"""
    env_file = Path('.env')
    
    # 生成 JSON
    json_config = json.dumps(targets, ensure_ascii=False)
    new_line = f'CHECKIN_TARGETS={json_config}\n'
    
    # 更新配置
    if targets_line_idx is not None:
        lines[targets_line_idx] = new_line
    else:
        # 查找插入位置
        for idx, line in enumerate(lines):
            if line.startswith('PHONE_NUMBER='):
                lines.insert(idx + 1, '\n')
                lines.insert(idx + 2, '# 签到目标配置\n')
                lines.insert(idx + 3, new_line)
                break
    
    # 注释旧配置
    for idx, line in enumerate(lines):
        if line.startswith('BOT_USERNAME=') or \
           line.startswith('CHECKIN_COMMAND=') or \
           line.startswith('CHECKIN_BUTTON_TEXT='):
            if not line.startswith('#'):
                lines[idx] = '# ' + line
    
    # 保存文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def main():
    print("=" * 60)
    print("🎯 添加签到目标 - 交互式工具")
    print("=" * 60)
    
    # 检查 .env 文件
    if not Path('.env').exists():
        print("\n❌ 未找到 .env 文件")
        print("请先运行: python setup_targets.py")
        return
    
    # 加载现有配置
    targets, targets_line_idx, lines = load_current_targets()
    
    # 显示现有目标
    display_targets(targets)
    
    # 循环添加目标
    while True:
        print("\n" + "=" * 60)
        if targets:
            add_more = input(f"是否添加第 {len(targets) + 1} 个签到目标? (y/n, 默认: n): ").strip().lower()
            if add_more != 'y':
                break
        else:
            print("开始添加第 1 个签到目标")
        
        # 添加目标
        new_target = add_single_target()
        if new_target:
            targets.append(new_target)
            print(f"\n✅ 已添加目标: {new_target['name']}")
            
            # 显示更新后的列表
            display_targets(targets)
        else:
            print("\n⚠️  未添加目标")
            retry = input("是否重试? (y/n): ").strip().lower()
            if retry != 'y':
                break
    
    # 保存配置
    if not targets:
        print("\n❌ 没有任何签到目标，未保存")
        return
    
    print("\n" + "=" * 60)
    print("📋 配置汇总")
    print("=" * 60)
    display_targets(targets)
    
    print("-" * 60)
    confirm = input("确认保存配置? (y/n, 默认: y): ").strip().lower()
    if confirm and confirm != 'y':
        print("\n❌ 已取消，未保存")
        return
    
    # 保存
    save_targets(targets, lines, targets_line_idx)
    
    print("\n" + "=" * 60)
    print("✅ 配置已保存到 .env")
    print("=" * 60)
    print("\n📝 下一步:")
    print("1. 测试配置: python manual_checkin.py")
    print("2. 查看群组: python list_groups.py")
    print("3. 重启服务: sudo systemctl restart telegram-auto-checkin")
    print("=" * 60)


if __name__ == '__main__':
    main()


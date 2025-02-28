import hashlib
import os
import shutil
import sys
from aivk.kernel.tee.tee_impl import Tee

def clear_screen():
    """清理屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """简单的TEE加密解密测试程序"""
    tee = Tee()
    
    while True:
        clear_screen()
        print("\n=== TEE 加密解密测试 ===")
        print("1. 初始化密码")
        print("2. 加密数据")
        print("3. 解密数据")
        print("4. 显示所有TEE信息")
        print("5. 清除所有数据")
        print("6. 退出")
        
        choice = input("\n请选择操作 (1-6): ")
        
        if choice == '1':
            try:
                # 获取Metadata字典
                metadata = tee.meta.Metadata()
                if metadata and 'AIVKey' in metadata:
                    print("密码已经设置过了！")
                    print("如需重置，请先使用选项5清除所有数据")
                else:
                    tee.setup_key()
                    print("密码设置成功！")
            except Exception as e:
                print(f"设置失败: {str(e)}")
                
        elif choice == '2':
            try:
                # 检查密码是否已设置
                metadata = tee.meta.Metadata()
                if not metadata or 'AIVKey' not in metadata:
                    print("请先初始化密码！")
                    continue
                
                data = input("请输入要加密的数据: ")
                desc = input("请输入数据描述: ")
                
                # 确保tee节点存在
                if 'tee' not in metadata:
                    tee.meta.Metadata.tee({})  # 使用函数调用初始化空字典
                
                tee_id = tee.encrypt(data, desc)
                print(f"\n加密成功！")
                print(f"TEE ID: {tee_id}")
                print("请保存好这个ID，解密时会用到")
            except Exception as e:
                print(f"加密失败: {str(e)}")
                
        elif choice == '3':
            try:
                metadata = tee.meta.Metadata()
                if not metadata or 'AIVKey' not in metadata:
                    print("请先初始化密码！")
                    continue
                
                tee_id = input("请输入TEE ID: ")
                decrypted = tee.decrypt(tee_id)
                print(f"\n解密成功！")
                print(f"解密数据: {decrypted}")
            except Exception as e:
                print(f"解密失败: {str(e)}")
                
        elif choice == '4':
            try:
                metadata = tee.meta.Metadata()
                if not metadata or 'tee' not in metadata:
                    print("暂无加密数据")
                    continue
                
                print("\n=== 已加密数据列表 ===")
                tee_data = metadata['tee']
                for key, value in tee_data.items():
                    if key.endswith('.description'):
                        tee_id = key.split('.')[0]
                        desc = value[0]
                        suffix = value[1]
                        print(f"TEE ID: {tee_id}")
                        print(f"描述: {desc}")
                        print(f"数据后缀: {suffix}")
                        print("-" * 30)
            except Exception as e:
                print(f"查看失败: {str(e)}")
                
        elif choice == '5':
            confirm = input("警告：这将删除所有加密数据！确定继续吗？(y/N): ")
            if confirm.lower() == 'y':
                try:
                    # 删除 Meta.toml
                    meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           '..', 'src', 'aivk', 'kernel', 'tee', 'Meta.toml')
                    if os.path.exists(meta_path):
                        os.remove(meta_path)
                    
                    # 删除安全存储目录
                    secure_path = os.path.join(os.path.expanduser('~'), '.aivk', 'secure')
                    if os.path.exists(secure_path):
                        shutil.rmtree(secure_path)
                    
                    print("所有数据已清除！")
                    print("程序将退出，请重新启动...")
                    sys.exit(0)
                except Exception as e:
                    print(f"清除失败: {str(e)}")
            else:
                print("操作已取消")
        
        elif choice == '6':
            print("\n感谢使用！再见！")
            sys.exit(0)
            
        else:
            print("\n无效的选择，请重试。")
            
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断。")
        sys.exit(0)

def verify_integrity(self):
    """验证密钥系统完整性"""
    try:
        if not self._last_password:
            return False
            
        password_hash = hashlib.sha256(self._last_password.encode()).hexdigest()
        stored_hash = self.meta.Metadata.AIVKey()
        
        return password_hash == stored_hash
    except:
        return False
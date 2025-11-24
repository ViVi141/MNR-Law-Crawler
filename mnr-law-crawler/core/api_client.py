"""
API客户端模块 - 处理所有HTTP请求
适配自然资源部政府信息公开平台API
"""

import requests
import time
import random
import json
import warnings
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 禁用 urllib3 的 HeaderParsingError 警告
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.HeaderParsingError)
except (ImportError, AttributeError):
    pass

from .config import Config


# User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]


class APIClient:
    """API客户端类 - 适配自然资源部API"""
    
    def __init__(self, config: Config):
        """初始化API客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.session = self._create_session()
        self.request_count = 0
        self.current_proxy = None
        
        # 初始化代理（如果启用）
        self._init_proxy()
    
    def _create_session(self) -> requests.Session:
        """创建新的会话"""
        session = requests.Session()
        
        # 随机选择User-Agent
        user_agent = random.choice(USER_AGENTS)
        
        # 设置请求头（自然资源部API）
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.config.get("base_url", "https://gi.mnr.gov.cn/"),
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        return session
    
    def _init_proxy(self):
        """初始化代理"""
        if not self.config.use_proxy:
            return
        
        api_key = self.config.kuaidaili_api_key
        if not api_key:
            return
        
        try:
            # 尝试导入快代理SDK
            import kdl
            
            if ':' in api_key:
                secret_id, secret_key = api_key.split(':', 1)
                auth = kdl.Auth(secret_id, secret_key)
                self.kuaidaili_client = kdl.Client(auth, timeout=(8, 12), max_retries=3)
                print("[信息] 快代理已启用")
            else:
                print("[警告] 快代理API密钥格式错误，需要 secret_id:secret_key")
        except ImportError:
            print("[警告] 快代理SDK未安装: pip install kdl")
        except Exception as e:
            print(f"[警告] 快代理初始化失败: {e}")
    
    def _get_proxy(self, force_new: bool = False) -> Optional[Dict[str, str]]:
        """获取代理IP
        
        Args:
            force_new: 是否强制获取新代理
            
        Returns:
            代理配置字典
        """
        if not self.config.use_proxy:
            return None
        
        if force_new or self.current_proxy is None:
            try:
                if hasattr(self, 'kuaidaili_client'):
                    proxy_list = self.kuaidaili_client.get_dps(1, format='json')
                    if proxy_list and len(proxy_list) > 0:
                        self.current_proxy = proxy_list[0]
                        print(f"  [代理] 获取新代理: {self.current_proxy[:50]}...")
            except Exception as e:
                if force_new:
                    print(f"  [警告] 获取代理失败: {e}")
                self.current_proxy = None
        
        if self.current_proxy:
            return {
                'http': f'http://{self.current_proxy}',
                'https': f'http://{self.current_proxy}',
            }
        
        return None
    
    def _rotate_session(self):
        """轮换会话"""
        if hasattr(self.session, 'close'):
            try:
                self.session.close()
            except Exception:
                pass
        
        self.session = self._create_session()
        self.request_count = 0
        print("  [会话轮换] 已创建新会话")
    
    def _check_and_rotate_session(self):
        """检查并轮换会话"""
        self.request_count += 1
        if self.request_count >= self.config.get("session_rotate_interval", 50):
            self._rotate_session()
    
    def search_policies(
        self,
        keywords: List[str] = None,
        page: int = 1,
        start_date: str = None,
        end_date: str = None,
        data_source: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """搜索政策列表（自然资源部API）
        
        Args:
            keywords: 关键词列表
            page: 页码
            start_date: 起始日期 yyyy-MM-dd
            end_date: 结束日期 yyyy-MM-dd
            data_source: 数据源配置（如果为None，使用默认配置）
            
        Returns:
            搜索结果（可能是JSON或HTML）
        """
        if keywords is None:
            keywords = []
        
        # 如果提供了数据源配置，使用它；否则使用默认配置
        if data_source:
            search_api = data_source.get("search_api", "https://search.mnr.gov.cn/was5/web/search")
            channel_id = data_source.get("channel_id", "216640")
            base_url = data_source.get("base_url", "https://gi.mnr.gov.cn/")
            # 更新Referer
            self.session.headers.update({'Referer': base_url})
        else:
            search_api = self.config.get("search_api", "https://search.mnr.gov.cn/was5/web/search")
            channel_id = self.config.get("channel_id", "216640")
            base_url = self.config.get("base_url", "https://gi.mnr.gov.cn/")
        
        perpage = self.config.get("perpage", 20)
        
        # 构建搜索关键词
        search_word = ' '.join(keywords) if keywords else ''
        
        params = {
            'channelid': channel_id,
            'searchword': search_word,
            'page': page,
            'perpage': perpage,
            'searchtype': 'title',  # 搜索标题
            'orderby': 'RELEVANCE'  # 按相关性排序
        }
        
        # 添加时间过滤
        if start_date:
            params['starttime'] = start_date
        if end_date:
            params['endtime'] = end_date
        
        self._check_and_rotate_session()
        
        max_retries = self.config.get("max_retries", 3)
        for retry in range(max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                response = self.session.get(
                    search_api,
                    params=params,
                    timeout=self.config.get("timeout", 30),
                    proxies=proxies
                )
                response.raise_for_status()
                
                # 尝试解析为JSON
                try:
                    result = response.json()
                    return {'type': 'json', 'data': result}
                except json.JSONDecodeError:
                    # 如果不是JSON，返回HTML文本
                    return {'type': 'html', 'data': response.text}
                    
            except Exception as e:
                print(f"[X] 搜索请求异常: {e}")
                
                if retry < max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    print(f"  [重试 {retry + 1}/{max_retries}] 等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def get_policy_detail(self, url: str, data_source: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取政策详情页正文和附件（自然资源部API）
        
        Args:
            url: 政策详情页URL
            data_source: 数据源配置（如果为None，根据URL自动判断）
            
        Returns:
            包含content和attachments的字典
            {
                'content': str,  # 正文内容
                'attachments': List[Dict]  # 附件列表，每个附件包含 {'url': str, 'name': str}
            }
        """
        # 如果没有提供数据源，根据URL自动判断
        if not data_source:
            data_sources = self.config.get("data_sources", [])
            for ds in data_sources:
                if ds.get("base_url", "") in url:
                    data_source = ds
                    break
        
        # 如果找到数据源，更新Referer
        if data_source:
            base_url = data_source.get("base_url", "https://gi.mnr.gov.cn/")
            self.session.headers.update({'Referer': base_url})
        
        self._check_and_rotate_session()
        
        max_retries = self.config.get("max_retries", 3)
        for retry in range(max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                response = self.session.get(
                    url,
                    timeout=self.config.get("timeout", 30),
                    proxies=proxies
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尝试多种正文容器
                content_div = soup.find('div', class_='TRS_Editor')
                if not content_div:
                    content_div = soup.find('div', class_='content')
                if not content_div:
                    content_div = soup.find('div', id='content')
                if not content_div:
                    content_div = soup.find('div', class_='article-content')
                if not content_div:
                    content_div = soup.find('div', class_='main-content')
                if not content_div:
                    content_div = soup.find('div', class_='article')
                
                # 提取正文内容
                content = ''
                if content_div:
                    content = content_div.get_text(strip=True)
                else:
                    # 兜底：返回全页文本
                    content = soup.get_text(strip=True)
                
                # 提取附件链接
                attachments = self._extract_attachments(soup, url)
                
                return {
                    'content': content,
                    'attachments': attachments
                }
                
            except Exception as e:
                print(f"[X] 获取详情失败: {e}")
                
                if retry < max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    time.sleep(wait_time)
                else:
                    return {'content': '', 'attachments': []}
        
        return {'content': '', 'attachments': []}
    
    def _extract_attachments(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """从HTML中提取附件链接
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL，用于拼接相对链接
            
        Returns:
            附件列表，每个附件包含 {'url': str, 'name': str}
        """
        attachments = []
        
        # 常见的附件文件扩展名（按长度从长到短排序，优先匹配长扩展名如.tar.gz）
        attachment_extensions = [
            '.tar.gz', '.tar.bz2', '.tar.xz',
            '.zip', '.tar', '.rar', '.7z', '.gz', '.bz2',
            '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.csv', '.xml', '.json'
        ]
        
        # 查找所有链接
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '').strip()
            if not href:
                continue
            
            # 过滤无效链接
            href_lower = href.lower()
            
            # 跳过无效链接
            if href_lower.startswith('javascript:') or href_lower.startswith('mailto:') or href_lower.startswith('#'):
                continue
            
            # 跳过空链接或只有#的链接
            if href == '#' or href == 'javascript:;' or href == 'javascript:void(0)':
                continue
            
            # 检查是否是附件链接
            is_attachment = False
            
            # 方法1: 检查文件扩展名（优先匹配长扩展名）
            for ext in attachment_extensions:
                if href_lower.endswith(ext):
                    is_attachment = True
                    break
            
            # 方法2: 检查链接文本是否包含"下载"、"附件"等关键词
            link_text = link.get_text(strip=True).lower()
            if any(keyword in link_text for keyword in ['下载', '附件', 'download', 'attachment']):
                # 但需要确保链接本身是有效的（不是javascript:）
                if not href_lower.startswith('javascript:'):
                    is_attachment = True
            
            # 方法3: 检查链接是否指向常见的附件路径
            if any(keyword in href_lower for keyword in ['/attach/', '/attachment/', '/file/', '/download/']):
                is_attachment = True
            
            if is_attachment:
                # 构建完整URL
                full_url = None
                if not href.startswith('http://') and not href.startswith('https://'):
                    if href.startswith('/'):
                        # 绝对路径
                        from urllib.parse import urlparse
                        parsed = urlparse(base_url)
                        full_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                    else:
                        # 相对路径
                        full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # 再次验证URL是否有效（避免javascript:等无效链接）
                if not full_url or full_url.lower().startswith(('javascript:', 'mailto:', '#')):
                    continue
                
                # 验证URL格式（必须包含协议）
                if not full_url.startswith('http://') and not full_url.startswith('https://'):
                    continue
                
                # 获取附件名称
                attachment_name = link.get_text(strip=True)
                if not attachment_name or len(attachment_name) < 2:
                    # 如果没有文本，尝试从URL中提取文件名
                    attachment_name = href.split('/')[-1].split('?')[0]
                    # 如果还是没有，使用URL的一部分
                    if not attachment_name or len(attachment_name) < 2:
                        attachment_name = f"附件_{len(attachments) + 1}"
                
                # 避免重复
                if not any(att['url'] == full_url for att in attachments):
                    attachments.append({
                        'url': full_url,
                        'name': attachment_name
                    })
        
        return attachments
    
    def download_file(
        self,
        file_path: str,
        save_path: str,
        chunk_size: int = 8192
    ) -> bool:
        """下载文件
        
        Args:
            file_path: 文件URL或路径
            save_path: 保存路径（本地）
            chunk_size: 分块大小
            
        Returns:
            是否下载成功
        """
        # 如果是完整URL，直接使用；否则拼接base_url
        if file_path.startswith('http://') or file_path.startswith('https://'):
            url = file_path
        else:
            base_url = self.config.get("base_url", "https://gi.mnr.gov.cn/")
            url = urljoin(base_url, file_path)
        
        self._check_and_rotate_session()
        
        max_retries = self.config.get("max_retries", 3)
        for retry in range(max_retries):
            try:
                proxies = self._get_proxy(force_new=(retry > 0))
                
                # 禁用 urllib3 的 HeaderParsingError 警告
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.HeaderParsingError)
                    except (ImportError, AttributeError):
                        pass
                    
                    response = self.session.get(
                        url,
                        stream=True,
                        timeout=60,
                        proxies=proxies
                    )
                    response.raise_for_status()
                
                # 下载文件
                import os
                try:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                    
                    # 检查文件是否成功下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        return True
                    else:
                        print("  [X] 下载失败：文件为空或不存在")
                        return False
                        
                except Exception as download_error:
                    # 即使下载过程中出错，也检查文件是否已部分下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        # 文件已部分下载，可能是 HeaderParsingError 导致的
                        error_str = str(download_error)
                        if 'HeaderParsingError' in error_str or 'NoBoundaryInMultipartDefect' in error_str:
                            # 忽略这个解析错误，文件已成功下载
                            return True
                    raise  # 重新抛出异常
                
            except Exception as e:
                # 检查是否是 HeaderParsingError（文件可能已成功下载）
                import os
                error_str = str(e)
                error_type = type(e).__name__
                
                if 'HeaderParsingError' in error_type or 'NoBoundaryInMultipartDefect' in error_str:
                    # 检查文件是否已成功下载
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        # 文件已成功下载，忽略这个解析错误
                        return True
                
                print(f"  [X] 下载失败: {e}")
                
                if retry < max_retries - 1:
                    wait_time = self.config.get("retry_delay", 5) * (retry + 1)
                    print(f"  [重试 {retry + 1}/{max_retries}] 等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    return False
        
        return False
    
    def close(self):
        """关闭客户端"""
        if hasattr(self.session, 'close'):
            try:
                self.session.close()
            except Exception:
                pass

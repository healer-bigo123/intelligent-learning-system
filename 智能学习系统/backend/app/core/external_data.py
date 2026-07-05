"""
外部数据源连接管理模块

该模块负责：
1. 管理外部数据源的配置和连接
2. 提供统一的数据访问接口
3. 实现身份验证和安全机制
4. 处理数据同步和错误恢复
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from enum import Enum
from datetime import datetime
import requests
import json
import time
import hashlib
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 类型变量
T = TypeVar('T')

# ================ 错误处理 ================

class ExternalDataError(Exception):
    """外部数据访问异常"""
    def __init__(self, message: str, error_code: Optional[int] = None, response: Any = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response
        self.timestamp = datetime.utcnow()

class DataSourceNotFoundError(ExternalDataError):
    """数据源未找到异常"""
    pass

class AuthenticationError(ExternalDataError):
    """认证失败异常"""
    pass

class SyncError(ExternalDataError):
    """数据同步异常"""
    pass

class RateLimitError(ExternalDataError):
    """请求频率超限异常"""
    pass


# ================ 数据源类型枚举 ================

class DataSourceType(Enum):
    """外部数据源类型"""
    EDUCATION_API = "education_api"      # 教育数据API
    KNOWLEDGE_BASE = "knowledge_base"    # 知识库
    EXERCISE_BANK = "exercise_bank"      # 外部题库
    LEARNING_PLATFORM = "learning_platform"  # 学习平台
    CUSTOM_API = "custom_api"            # 自定义API

# ================ 认证类型枚举 ================

class AuthType(Enum):
    """身份验证类型"""
    NONE = "none"                        # 无需认证
    API_KEY = "api_key"                  # API密钥
    OAUTH2 = "oauth2"                    # OAuth2.0
    BASIC = "basic"                      # 基础认证
    BEARER_TOKEN = "bearer_token"        # Bearer Token
    CUSTOM = "custom"                    # 自定义认证

# ================ 数据同步策略枚举 ================

class SyncStrategy(Enum):
    """数据同步策略"""
    MANUAL = "manual"                    # 手动同步
    SCHEDULED = "scheduled"              # 定时同步
    REALTIME = "realtime"                # 实时同步
    ON_DEMAND = "on_demand"              # 按需同步

# ================ 数据状态枚举 ================

class DataSyncStatus(Enum):
    """数据同步状态"""
    PENDING = "pending"                  # 待同步
    RUNNING = "running"                  # 同步中
    SUCCESS = "success"                  # 成功
    FAILED = "failed"                    # 失败
    PARTIAL = "partial"                  # 部分成功

# ================ 配置类 ================

@dataclass
class DataSourceConfig:
    """外部数据源配置"""
    id: str
    name: str
    type: DataSourceType
    base_url: str
    auth_type: AuthType
    auth_config: Dict[str, Any] = None
    sync_strategy: SyncStrategy = SyncStrategy.MANUAL
    sync_interval: int = 3600  # 默认1小时
    enabled: bool = True
    description: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.auth_config is None:
            self.auth_config = {}

# ================ 同步记录类 ================

@dataclass
class SyncRecord:
    """数据同步记录"""
    id: str
    source_id: str
    sync_type: str
    status: DataSyncStatus
    total_records: int = 0
    success_count: int = 0
    failed_count: int = 0
    error_message: str = ""
    started_at: datetime = None
    completed_at: datetime = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()

# ================ 认证处理器基类 ================

class AuthHandler(ABC):
    """身份验证处理器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token_cache = {}

    @abstractmethod
    def authenticate(self) -> Dict[str, Any]:
        """执行认证，返回请求头"""
        pass

    @abstractmethod
    def refresh_token(self):
        """刷新令牌（如需要）"""
        pass

    def get_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        return {}

# ================ 认证处理器实现 ================

class NoAuthHandler(AuthHandler):
    """无需认证处理器"""
    def authenticate(self) -> Dict[str, Any]:
        return {}
    
    def refresh_token(self):
        pass

class ApiKeyAuthHandler(AuthHandler):
    """API密钥认证处理器"""
    def authenticate(self) -> Dict[str, Any]:
        key = self.config.get('api_key', '')
        header_name = self.config.get('header_name', 'X-API-Key')
        return {header_name: key}
    
    def refresh_token(self):
        pass
    
    def get_headers(self) -> Dict[str, str]:
        return self.authenticate()

class BearerTokenAuthHandler(AuthHandler):
    """Bearer Token认证处理器"""
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = None
        self.token_expires_at = None

    def authenticate(self) -> Dict[str, Any]:
        if self.token and (not self.token_expires_at or datetime.utcnow() < self.token_expires_at):
            return {"Authorization": f"Bearer {self.token}"}
        
        # 获取新token
        token_url = self.config.get('token_url')
        if token_url:
            response = requests.post(
                token_url,
                data=self.config.get('token_params', {}),
                auth=(self.config.get('client_id'), self.config.get('client_secret')) if self.config.get('client_id') else None
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
        
        if not self.token:
            self.token = self.config.get('token', '')
        
        return {"Authorization": f"Bearer {self.token}"}
    
    def refresh_token(self):
        self.token = None
        self.token_expires_at = None
        return self.authenticate()
    
    def get_headers(self) -> Dict[str, str]:
        return self.authenticate()

class BasicAuthHandler(AuthHandler):
    """基础认证处理器"""
    def authenticate(self) -> Dict[str, Any]:
        username = self.config.get('username', '')
        password = self.config.get('password', '')
        return requests.auth.HTTPBasicAuth(username, password)
    
    def refresh_token(self):
        pass
    
    def get_headers(self) -> Dict[str, str]:
        # 基础认证会自动处理
        return {}

class CustomAuthHandler(AuthHandler):
    """自定义认证处理器"""
    def authenticate(self) -> Dict[str, Any]:
        # 允许自定义认证逻辑
        custom_func = self.config.get('auth_function')
        if custom_func and callable(custom_func):
            return custom_func(self.config)
        return {}
    
    def refresh_token(self):
        pass

# ================ 认证处理器工厂 ================

class AuthHandlerFactory:
    """认证处理器工厂"""
    
    @staticmethod
    def create(auth_type: AuthType, config: Dict[str, Any]) -> AuthHandler:
        """创建认证处理器"""
        handlers: Dict[AuthType, Type[AuthHandler]] = {
            AuthType.NONE: NoAuthHandler,
            AuthType.API_KEY: ApiKeyAuthHandler,
            AuthType.OAUTH2: BearerTokenAuthHandler,
            AuthType.BASIC: BasicAuthHandler,
            AuthType.BEARER_TOKEN: BearerTokenAuthHandler,
            AuthType.CUSTOM: CustomAuthHandler,
        }
        
        handler_class = handlers.get(auth_type)
        if not handler_class:
            raise ValueError(f"不支持的认证类型: {auth_type}")
        
        return handler_class(config)

# ================ 外部数据源基类 ================

class ExternalDataSource(ABC):
    """外部数据源基类"""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.auth_handler = AuthHandlerFactory.create(config.auth_type, config.auth_config)
        self.session = requests.Session()
        self.last_sync_time = None
        self.sync_record: Optional[SyncRecord] = None

    @abstractmethod
    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """获取数据"""
        pass

    @abstractmethod
    def search_data(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索数据"""
        pass

    @abstractmethod
    def sync_data(self, force: bool = False) -> SyncRecord:
        """同步数据"""
        pass

    def _make_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """执行HTTP请求"""
        url = self.config.base_url + path
        headers = kwargs.pop('headers', {})
        auth = None

        # 获取认证信息
        try:
            auth_info = self.auth_handler.authenticate()
            if isinstance(auth_info, dict):
                headers.update(auth_info)
            else:
                auth = auth_info
        except Exception as e:
            raise ExternalDataError(f"认证失败: {str(e)}")

        # 设置默认请求头
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept', 'application/json')

        # 执行请求
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                auth=auth,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ExternalDataError(f"请求失败 [{method} {url}]: {str(e)}")

    def _handle_response(self, response: requests.Response) -> Any:
        """处理响应"""
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    def _generate_sync_id(self, sync_type: str) -> str:
        """生成同步记录ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_str = hashlib.md5(f"{self.config.id}_{sync_type}_{timestamp}".encode()).hexdigest()[:8]
        return f"sync_{self.config.id[:8]}_{sync_type}_{hash_str}"

    def create_sync_record(self, sync_type: str) -> SyncRecord:
        """创建同步记录"""
        self.sync_record = SyncRecord(
            id=self._generate_sync_id(sync_type),
            source_id=self.config.id,
            sync_type=sync_type,
            status=DataSyncStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        return self.sync_record

    def update_sync_record(self, status: DataSyncStatus, success_count: int = 0, 
                          failed_count: int = 0, error_message: str = ""):
        """更新同步记录"""
        if self.sync_record:
            self.sync_record.status = status
            self.sync_record.success_count = success_count
            self.sync_record.failed_count = failed_count
            self.sync_record.error_message = error_message
            self.sync_record.completed_at = datetime.utcnow()
            self.sync_record.total_records = success_count + failed_count

# ================ 教育数据API源 ================

class EducationApiDataSource(ExternalDataSource):
    """教育数据API数据源"""

    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """获取数据"""
        response = self._make_request('GET', endpoint, params=params)
        return self._handle_response(response)

    def search_data(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索数据"""
        params = {'q': query}
        if filters:
            params.update(filters)
        response = self._make_request('GET', '/search', params=params)
        result = self._handle_response(response)
        return result.get('data', [])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
           retry=retry_if_exception_type(ExternalDataError))
    def sync_data(self, force: bool = False) -> SyncRecord:
        """同步数据"""
        now = datetime.utcnow()
        
        # 检查是否需要同步
        if not force and self.last_sync_time:
            time_since_last = (now - self.last_sync_time).total_seconds()
            if time_since_last < self.config.sync_interval:
                return SyncRecord(
                    id=self._generate_sync_id('recent'),
                    source_id=self.config.id,
                    sync_type='knowledge',
                    status=DataSyncStatus.SUCCESS,
                    success_count=0,
                    error_message="距上次同步时间不足，跳过"
                )

        # 创建同步记录
        self.create_sync_record('knowledge')
        
        try:
            # 同步知识点
            knowledge_data = self.fetch_data('/knowledge-points')
            success_count = self._process_knowledge_data(knowledge_data)
            
            # 同步题库
            exercise_data = self.fetch_data('/exercises')
            success_count += self._process_exercise_data(exercise_data)
            
            self.update_sync_record(
                status=DataSyncStatus.SUCCESS,
                success_count=success_count
            )
            self.last_sync_time = now
            
        except Exception as e:
            self.update_sync_record(
                status=DataSyncStatus.FAILED,
                failed_count=1,
                error_message=str(e)
            )
            raise
        
        return self.sync_record

    def _process_knowledge_data(self, data: Any) -> int:
        """处理知识点数据"""
        items = data.get('items', [])
        # 实际处理逻辑：保存到本地数据库或向量库
        for item in items:
            # 这里应该调用服务层保存数据
            print(f"处理知识点: {item.get('name')}")
        return len(items)

    def _process_exercise_data(self, data: Any) -> int:
        """处理题库数据"""
        items = data.get('items', [])
        for item in items:
            print(f"处理习题: {item.get('question')[:30]}...")
        return len(items)

# ================ 外部题库数据源 ================

class ExerciseBankDataSource(ExternalDataSource):
    """外部题库数据源"""

    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """获取数据"""
        response = self._make_request('GET', endpoint, params=params)
        return self._handle_response(response)

    def search_data(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索题目"""
        params = {'keyword': query}
        if filters:
            params.update({k: v for k, v in filters.items() if v})
        
        response = self._make_request('GET', '/api/exercises/search', params=params)
        result = self._handle_response(response)
        return result.get('exercises', [])

    def get_exercises_by_subject(self, subject: str, difficulty: Optional[int] = None, 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """按学科获取习题"""
        params = {'subject': subject, 'limit': limit}
        if difficulty:
            params['difficulty'] = difficulty
        return self.search_data('', params)

    def get_exercise_detail(self, exercise_id: str) -> Dict[str, Any]:
        """获取题目详情"""
        response = self._make_request('GET', f'/api/exercises/{exercise_id}')
        return self._handle_response(response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def sync_data(self, force: bool = False) -> SyncRecord:
        """同步题库数据"""
        self.create_sync_record('exercises')
        
        try:
            subjects = ['数学', '英语', '物理', '化学', '生物']
            total_success = 0
            
            for subject in subjects:
                exercises = self.get_exercises_by_subject(subject, limit=50)
                total_success += self._import_exercises(exercises)
            
            self.update_sync_record(
                status=DataSyncStatus.SUCCESS,
                success_count=total_success
            )
            self.last_sync_time = datetime.utcnow()
            
        except Exception as e:
            self.update_sync_record(
                status=DataSyncStatus.FAILED,
                failed_count=1,
                error_message=str(e)
            )
            raise
        
        return self.sync_record

    def _import_exercises(self, exercises: List[Dict[str, Any]]) -> int:
        """导入习题到本地数据库"""
        # 实际导入逻辑
        for exercise in exercises:
            print(f"导入习题: {exercise.get('id')} - {exercise.get('subject')}")
        return len(exercises)

# ================ 学习平台数据源 ================

class LearningPlatformDataSource(ExternalDataSource):
    """学习平台数据源"""

    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """获取数据"""
        response = self._make_request('GET', endpoint, params=params)
        return self._handle_response(response)

    def search_data(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索学习资源"""
        params = {'query': query}
        if filters:
            params.update(filters)
        response = self._make_request('GET', '/resources/search', params=params)
        result = self._handle_response(response)
        return result.get('results', [])

    def get_courses(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取课程列表"""
        params = {}
        if category:
            params['category'] = category
        response = self._make_request('GET', '/courses', params=params)
        return self._handle_response(response).get('courses', [])

    def get_course_detail(self, course_id: str) -> Dict[str, Any]:
        """获取课程详情"""
        response = self._make_request('GET', f'/courses/{course_id}')
        return self._handle_response(response)

    def sync_data(self, force: bool = False) -> SyncRecord:
        """同步学习资源"""
        self.create_sync_record('courses')
        
        try:
            courses = self.get_courses()
            success_count = self._sync_courses(courses)
            
            self.update_sync_record(
                status=DataSyncStatus.SUCCESS,
                success_count=success_count
            )
            self.last_sync_time = datetime.utcnow()
            
        except Exception as e:
            self.update_sync_record(
                status=DataSyncStatus.FAILED,
                failed_count=1,
                error_message=str(e)
            )
            raise
        
        return self.sync_record

    def _sync_courses(self, courses: List[Dict[str, Any]]) -> int:
        """同步课程"""
        for course in courses:
            print(f"同步课程: {course.get('title')}")
        return len(courses)

# ================ 自定义API数据源 ================

class CustomApiDataSource(ExternalDataSource):
    """自定义API数据源"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.endpoints = config.auth_config.get('endpoints', {})

    def fetch_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """获取数据"""
        # 支持预配置的endpoint别名
        actual_endpoint = self.endpoints.get(endpoint, endpoint)
        response = self._make_request('GET', actual_endpoint, params=params)
        return self._handle_response(response)

    def search_data(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索数据"""
        params = {'search': query}
        if filters:
            params.update(filters)
        
        search_endpoint = self.endpoints.get('search', '/search')
        response = self._make_request('GET', search_endpoint, params=params)
        result = self._handle_response(response)
        
        # 尝试多种数据格式
        for key in ['results', 'data', 'items', 'list']:
            if key in result:
                return result[key]
        return result if isinstance(result, list) else [result]

    def sync_data(self, force: bool = False) -> SyncRecord:
        """同步数据"""
        self.create_sync_record('custom')
        
        try:
            # 获取所有配置的数据源
            data_endpoints = self.endpoints.get('sync_endpoints', [])
            total_success = 0
            
            for endpoint_info in data_endpoints:
                endpoint = endpoint_info.get('path')
                if endpoint:
                    data = self.fetch_data(endpoint)
                    processor = endpoint_info.get('processor')
                    if processor and callable(processor):
                        success_count = processor(data)
                    else:
                        success_count = len(data) if isinstance(data, list) else 1
                    total_success += success_count
            
            self.update_sync_record(
                status=DataSyncStatus.SUCCESS,
                success_count=total_success
            )
            self.last_sync_time = datetime.utcnow()
            
        except Exception as e:
            self.update_sync_record(
                status=DataSyncStatus.FAILED,
                failed_count=1,
                error_message=str(e)
            )
            raise
        
        return self.sync_record

# ================ 数据源工厂 ================

class DataSourceFactory:
    """外部数据源工厂"""

    @staticmethod
    def create(config: DataSourceConfig) -> ExternalDataSource:
        """创建数据源实例"""
        sources: Dict[DataSourceType, Type[ExternalDataSource]] = {
            DataSourceType.EDUCATION_API: EducationApiDataSource,
            DataSourceType.KNOWLEDGE_BASE: EducationApiDataSource,
            DataSourceType.EXERCISE_BANK: ExerciseBankDataSource,
            DataSourceType.LEARNING_PLATFORM: LearningPlatformDataSource,
            DataSourceType.CUSTOM_API: CustomApiDataSource,
        }

        source_class = sources.get(config.type)
        if not source_class:
            raise ValueError(f"不支持的数据源类型: {config.type}")

        return source_class(config)

# ================ 数据源管理器 ================

class DataSourceManager:
    """外部数据源管理器"""

    def __init__(self):
        self.sources: Dict[str, ExternalDataSource] = {}
        self.source_configs: Dict[str, DataSourceConfig] = {}
        self.sync_history: List[SyncRecord] = []

    def register_source(self, config: DataSourceConfig) -> ExternalDataSource:
        """注册数据源"""
        if not config.enabled:
            return None
        
        source = DataSourceFactory.create(config)
        self.sources[config.id] = source
        self.source_configs[config.id] = config
        return source

    def unregister_source(self, source_id: str):
        """注销数据源"""
        self.sources.pop(source_id, None)
        self.source_configs.pop(source_id, None)

    def get_source(self, source_id: str) -> Optional[ExternalDataSource]:
        """获取数据源"""
        return self.sources.get(source_id)

    def list_sources(self, type_filter: Optional[DataSourceType] = None) -> List[DataSourceConfig]:
        """列出所有数据源配置"""
        if type_filter:
            return [c for c in self.source_configs.values() if c.type == type_filter]
        return list(self.source_configs.values())

    def search_all(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """在所有数据源中搜索"""
        results = []
        
        for source_id, source in self.sources.items():
            try:
                data = source.search_data(query, filters)
                for item in data:
                    item['source_id'] = source_id
                    item['source_name'] = self.source_configs[source_id].name
                results.extend(data)
            except Exception as e:
                print(f"数据源 {source_id} 搜索失败: {e}")
        
        return results

    def sync_all(self, force: bool = False) -> List[SyncRecord]:
        """同步所有数据源"""
        records = []
        
        for source_id, source in self.sources.items():
            try:
                record = source.sync_data(force)
                records.append(record)
                self.sync_history.append(record)
            except Exception as e:
                # 记录失败但继续同步其他数据源
                record = SyncRecord(
                    id=f"sync_{source_id[:8]}_failed_{int(time.time())}",
                    source_id=source_id,
                    sync_type='full',
                    status=DataSyncStatus.FAILED,
                    failed_count=1,
                    error_message=str(e),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
                records.append(record)
                self.sync_history.append(record)
        
        return records

    def get_sync_history(self, source_id: Optional[str] = None, 
                        limit: int = 20) -> List[SyncRecord]:
        """获取同步历史"""
        history = self.sync_history
        if source_id:
            history = [h for h in history if h.source_id == source_id]
        return sorted(history, key=lambda x: x.started_at, reverse=True)[:limit]

    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        return {
            'total_sources': len(self.sources),
            'active_sources': len([s for s in self.sources.values() if s.config.enabled]),
            'last_sync_time': max([s.last_sync_time for s in self.sources.values() 
                                if s.last_sync_time], default=None),
            'sync_history_count': len(self.sync_history)
        }

# ================ 错误处理 ================

class ExternalDataError(Exception):
    """外部数据访问异常"""
    def __init__(self, message: str, error_code: Optional[int] = None, response: Any = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response
        self.timestamp = datetime.utcnow()

class DataSourceNotFoundError(ExternalDataError):
    """数据源未找到异常"""
    pass

class AuthenticationError(ExternalDataError):
    """认证失败异常"""
    pass

class SyncError(ExternalDataError):
    """数据同步异常"""
    pass

class RateLimitError(ExternalDataError):
    """请求频率超限异常"""
    pass

# ================ 全局管理器实例 ================

# 创建全局数据源管理器
data_source_manager = DataSourceManager()

# ================ 便捷函数 ================

def register_education_api(name: str, base_url: str, api_key: str, 
                          sync_interval: int = 3600) -> str:
    """注册教育API数据源"""
    config = DataSourceConfig(
        id=f"edu_{hashlib.md5(base_url.encode()).hexdigest()[:12]}",
        name=name,
        type=DataSourceType.EDUCATION_API,
        base_url=base_url,
        auth_type=AuthType.API_KEY,
        auth_config={'api_key': api_key, 'header_name': 'X-API-Key'},
        sync_strategy=SyncStrategy.SCHEDULED,
        sync_interval=sync_interval,
        enabled=True,
        description=f"教育数据API: {name}"
    )
    data_source_manager.register_source(config)
    return config.id

def register_exercise_bank(name: str, base_url: str, 
                           auth_type: AuthType = AuthType.NONE,
                           auth_config: Optional[Dict[str, Any]] = None) -> str:
    """注册外部题库数据源"""
    config = DataSourceConfig(
        id=f"bank_{hashlib.md5(base_url.encode()).hexdigest()[:12]}",
        name=name,
        type=DataSourceType.EXERCISE_BANK,
        base_url=base_url,
        auth_type=auth_type,
        auth_config=auth_config or {},
        sync_strategy=SyncStrategy.SCHEDULED,
        sync_interval=7200,
        enabled=True,
        description=f"外部题库: {name}"
    )
    data_source_manager.register_source(config)
    return config.id

# ================ 示例使用 ================

if __name__ == "__main__":
    # 示例1: 注册教育API数据源
    # edu_id = register_education_api(
    #     name="智慧教育平台",
    #     base_url="https://api.example.com/edu",
    #     api_key="your-api-key-here"
    # )
    
    # 示例2: 注册外部题库
    # bank_id = register_exercise_bank(
    #     name="高考题库",
    #     base_url="https://api.exercise-bank.com",
    #     auth_type=AuthType.API_KEY,
    #     auth_config={"api_key": "bank-api-key"}
    # )
    
    # 示例3: 搜索数据
    # results = data_source_manager.search_all("三角函数", {"subject": "数学"})
    # print(f"搜索结果: {len(results)} 条")
    
    # 示例4: 同步所有数据源
    # records = data_source_manager.sync_all()
    # for record in records:
    #     print(f"同步 {record.source_id}: {record.status} ({record.success_count} 条)")
    
    print("外部数据源管理器初始化完成")
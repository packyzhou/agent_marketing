-- 创建数据库
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ai_agent_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_agent_platform;

-- 用户表
CREATE TABLE IF NOT EXISTS tb_user (
    id BIGINT PRIMARY KEY COMMENT '雪花算法ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    referral_id BIGINT COMMENT '推荐人ID',
    group_id BIGINT COMMENT '分组ID',
    role ENUM('ADMIN', 'USER') DEFAULT 'USER' COMMENT '角色',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_group_id (group_id),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 分组表
CREATE TABLE IF NOT EXISTS tb_group (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '分组ID',
    group_name VARCHAR(100) NOT NULL COMMENT '分组名称',
    owner_id BIGINT NOT NULL COMMENT '所有者ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分组表';

-- 租户表
CREATE TABLE IF NOT EXISTS tb_tenant (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    app_key VARCHAR(64) UNIQUE NOT NULL COMMENT '应用密钥',
    app_secret VARCHAR(128) NOT NULL COMMENT '应用秘钥',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    tenant_name VARCHAR(100) COMMENT '租户名称',
    group_binding_json TEXT COMMENT '绑定信息JSON',
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_app_key (app_key),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户表';

-- 供应商表
CREATE TABLE IF NOT EXISTS tb_provider (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商ID',
    name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '供应商代码',
    base_url VARCHAR(255) NOT NULL COMMENT '基础URL',
    config_guide TEXT COMMENT '配置说明',
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';

-- 供应商密钥表
CREATE TABLE IF NOT EXISTS tb_provider_key (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '密钥ID',
    app_key VARCHAR(64) NOT NULL COMMENT '租户AppKey',
    provider_id BIGINT NOT NULL COMMENT '供应商ID',
    api_key VARCHAR(255) NOT NULL COMMENT 'API密钥',
    model_name VARCHAR(100) COMMENT '模型名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_app_key (app_key),
    INDEX idx_provider_id (provider_id),
    UNIQUE KEY uk_app_key (app_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商密钥表';

-- 分组成员与AppKey绑定表
CREATE TABLE IF NOT EXISTS tb_group_member_app_binding (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    owner_user_id BIGINT NOT NULL COMMENT '所有者用户ID',
    member_id BIGINT NOT NULL COMMENT '成员用户ID',
    app_key VARCHAR(64) DEFAULT NULL COMMENT '绑定的AppKey',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_owner_user_id (owner_user_id),
    INDEX idx_member_id (member_id),
    INDEX idx_binding_app_key (app_key),
    UNIQUE KEY uk_owner_member (owner_user_id, member_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分组成员AppKey绑定表';

-- Token汇总表
CREATE TABLE IF NOT EXISTS tb_token_summary (
    app_key VARCHAR(64) PRIMARY KEY COMMENT '应用密钥',
    total_tokens BIGINT DEFAULT 0 COMMENT '总Token数',
    last_month_tokens BIGINT DEFAULT 0 COMMENT '上月Token数',
    current_month_tokens BIGINT DEFAULT 0 COMMENT '本月Token数',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Token汇总表';

-- Token每日统计表
CREATE TABLE IF NOT EXISTS tb_token_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    app_key VARCHAR(64) NOT NULL COMMENT '应用密钥',
    date DATE NOT NULL COMMENT '日期',
    token_count BIGINT DEFAULT 0 COMMENT 'Token数量',
    request_count INT DEFAULT 0 COMMENT '请求次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_app_key_date (app_key, date),
    UNIQUE KEY uk_app_key_date (app_key, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Token每日统计表';

-- 对话记录表
CREATE TABLE IF NOT EXISTS tb_conversation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    app_key VARCHAR(64) NOT NULL COMMENT '应用密钥',
    round_number INT NOT NULL COMMENT '对话轮次',
    user_message TEXT NOT NULL COMMENT '用户消息',
    ai_response TEXT NOT NULL COMMENT 'AI响应',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_app_key_round (app_key, round_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话记录表';

-- 记忆元数据表
CREATE TABLE IF NOT EXISTS tb_memory_meta (
    app_key VARCHAR(64) PRIMARY KEY COMMENT '应用密钥',
    last_processed_round INT DEFAULT 0 COMMENT '最后处理轮次',
    kv_file_path VARCHAR(255) COMMENT 'KV存储文件路径',
    digest_file_path VARCHAR(255) COMMENT '摘要文件路径',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='记忆元数据表';

-- 初始管理员 (密码: admin123)
INSERT INTO tb_user (id, username, password_hash, real_name, role) VALUES
(1000000000000000001, 'admin', '$2b$12$7PClnwmUNx.zogr/0ZUTSerDKm2V9TWdsZ13XImNaA/A/TSkkWMCC', '系统管理员', 'ADMIN');

-- 初始供应商
INSERT INTO tb_provider (id, name, code, base_url, config_guide, status) VALUES
(1, '阿里千问', 'qwen', 'https://dashscope.aliyuncs.com/compatible-mode/v1', '1. 访问阿里云控制台\n2. 开通DashScope服务\n3. 创建API Key\n4. 填入下方API Key配置', 'ACTIVE'),
(2, '字节豆包', 'doubao', 'https://ark.cn-beijing.volces.com/api/v3', '1. 访问火山引擎控制台\n2. 开通豆包大模型服务\n3. 创建API Key\n4. 填入下方API Key配置', 'ACTIVE'),
(3, 'Deepseek', 'deepseek', 'https://api.deepseek.com/v1', '1. 访问 platform.deepseek.com\n2. 注册并登录账号\n3. 在API Keys页面创建密钥\n4. 填入下方API Key配置', 'ACTIVE');

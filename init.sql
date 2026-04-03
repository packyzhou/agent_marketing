-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_agent_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_agent_platform;

-- 用户表
CREATE TABLE IF NOT EXISTS tb_user (
    id BIGINT PRIMARY KEY COMMENT '雪花算法ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    referral_id BIGINT COMMENT '推荐人ID',
    group_id BIGINT COMMENT '分组ID',
    role ENUM('ADMIN', 'USER') DEFAULT 'USER' COMMENT '角色',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_group_id (group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 分组表
CREATE TABLE IF NOT EXISTS tb_group (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '分组ID',
    group_name VARCHAR(100) NOT NULL COMMENT '分组名称',
    owner_id BIGINT NOT NULL COMMENT '所有者ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分组表';

-- 租户表
CREATE TABLE IF NOT EXISTS tb_tenant (
    app_key VARCHAR(64) PRIMARY KEY COMMENT '应用密钥',
    app_secret VARCHAR(128) NOT NULL COMMENT '应用秘钥',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    group_binding_json TEXT COMMENT '绑定信息JSON',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户表';

-- 供应商表
CREATE TABLE IF NOT EXISTS tb_provider (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商ID',
    name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    base_url VARCHAR(255) NOT NULL COMMENT '基础URL',
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 供应商密钥表
CREATE TABLE IF NOT EXISTS tb_provider_key (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '密钥ID',
    tenant_id VARCHAR(64) NOT NULL COMMENT '租户ID',
    provider_id BIGINT NOT NULL COMMENT '供应商ID',
    api_key VARCHAR(255) NOT NULL COMMENT 'API密钥',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_provider_id (provider_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商密钥表';

-- Token汇总表
CREATE TABLE IF NOT EXISTS tb_token_summary (
    app_key VARCHAR(64) PRIMARY KEY COMMENT '应用密钥',
    total_tokens BIGINT DEFAULT 0 COMMENT '总Token数',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Token汇总表';

-- Token每日统计表
CREATE TABLE IF NOT EXISTS tb_token_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    app_key VARCHAR(64) NOT NULL COMMENT '应用密钥',
    date DATE NOT NULL COMMENT '日期',
    token_count BIGINT DEFAULT 0 COMMENT 'Token数量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_app_key_date (app_key, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Token每日统计表';

-- 记忆元数据表
CREATE TABLE IF NOT EXISTS tb_memory_meta (
    app_key VARCHAR(64) PRIMARY KEY COMMENT '应用密钥',
    last_processed_round INT DEFAULT 0 COMMENT '最后处理轮次',
    file_path VARCHAR(255) COMMENT '文件路径',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记忆元数据表';

-- 插入初始管理员用户 (密码: admin123)
INSERT INTO tb_user (id, username, password_hash, role) VALUES
(1000000000000000001, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEiW.u', 'ADMIN');

-- 插入初始供应商
INSERT INTO tb_provider (id, name, base_url, status) VALUES
(1, '阿里千问', 'https://dashscope.aliyuncs.com/api/v1', 'ACTIVE'),
(2, '字节豆包', 'https://ark.cn-beijing.volces.com/api/v3', 'ACTIVE'),
(3, 'Deepseek', 'https://api.deepseek.com/v1', 'ACTIVE');

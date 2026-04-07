export default {
  lang: { zh: '中文', en: 'English', ja: '日本語' },
  nav: {
    home: '首页',
    docs: '文档',
    about: '关于',
    marketplace: '浏览市场'
  },
  home: {
    subtitle: 'Clone Human Intelligence',
    heroTitle1: '复制顶尖人才的',
    heroTitle2: '思维引擎',
    heroDesc: '极简化的个人能力交易中心。通过神经抽取技术，将专家经验转化为可弹性扩展的数字资产。',
    quickStart: '快速开始',
    learnMore: '了解更多',
    hirePrice: '雇用价格',
    memory: '记忆',
    duration: '时长',
    hires: '次雇用'
  },
  footer: {
    desc: '我们正在重新定义"雇佣"的含义。将个人经验商品化，是实现全球生产力平权的第一步。',
    navigate: '导航',
    connect: '链接',
    copyright: 'Mr.Joe © 2026 AI Agent Market.',
    slogan: '为智能时代而设计'
  },
  about: {
    title: '关于',
    titleHighlight: 'Agent Market',
    subtitle: '连接合作伙伴，共建智能未来',
    formTitle: '合作意向',
    formDesc: '请填写以下信息，我们将尽快与您取得联系',
    company: '公司名称',
    companyPh: '请输入公司名称',
    contact: '联系方式',
    contactPh: '邮箱或电话',
    intention: '合作意向',
    intentionPh: '请选择合作意向',
    intentionOpts: {
      tech: '技术合作',
      business: '商务合作',
      invest: '投资合作',
      other: '其他'
    },
    purpose: '项目用途',
    purposePh: '请简述您的项目用途和需求...',
    submit: '提交',
    submitSuccess: '提交成功，我们将尽快与您联系！',
    submitFail: '请填写完整信息',
    visionTitle: '项目愿景',
    visionQuote: '通过AI技术复制人类能力，实现专业经验的商业化变现',
    visionDesc: '我们相信每个人的专业知识和经验都具有不可估量的价值。通过神经抽取技术，将专家经验转化为可弹性扩展的数字资产，实现全球生产力平权。',
    initiator: '发起人',
    founder: '创始人'
  },
  docs: {
    title: '文档中心',
    subtitle: '部署、配置和运行 AI Agent 营销平台所需的全部信息',
    sections: {
      overview: '项目概述',
      techStack: '技术栈',
      prerequisites: '前置要求',
      quickStart: '快速开始',
      access: '访问凭据',
      architecture: '系统架构',
      configuration: '配置说明',
      commands: '常用命令'
    },
    overviewDesc: 'AI Agent 营销平台是一个功能完整的AI智能体SaaS平台，支持多租户、推荐分组、双层记忆系统和Token使用分析。通过AI驱动的智能体复制，实现人类专业技能的商业化。',
    features: {
      multiTenant: '多租户架构',
      multiTenantDesc: 'AppKey/AppSecret认证，租户级API隔离，分组用户绑定。',
      dualMemory: '双层记忆',
      dualMemoryDesc: 'KV事实记忆 + 递归行为摘要压缩，跨层引用检测。',
      tokenAnalytics: 'Token分析',
      tokenAnalyticsDesc: '实时用量统计，月度对比，30天趋势可视化。',
      referralGroups: '推荐分组',
      referralGroupsDesc: '基于推荐的用户分组，自动创建分组和租户共享。'
    },
    backend: '后端',
    frontend: '前端',
    option1: '方式一：Docker Compose（推荐）',
    option2: '方式二：启动脚本（Windows）',
    option2Desc: '脚本自动检查Docker环境，构建并启动所有服务。',
    option3: '方式三：本地开发',
    defaultAdmin: '默认管理员账号',
    dockerSteps: {
      step1: '克隆仓库',
      step2: '启动所有服务',
      step3: '等待启动（1-2分钟），验证状态'
    },
    archBlocks: {
      proxy: 'AI代理',
      proxyDesc: '统一API对接多个LLM供应商，支持流式响应',
      memory: '双层记忆',
      memoryDesc: 'KV事实存储 + 递归行为摘要压缩',
      analytics: 'Token分析',
      analyticsDesc: '实时用量追踪，30天趋势可视化'
    },
    memorySystem: '记忆系统',
    envVars: '环境变量',
    commands: {
      viewLogs: '查看全部日志',
      restart: '重启服务',
      stop: '停止服务',
      resetDb: '重置数据库',
      rebuild: '代码更改后重新构建'
    }
  },
  login: {
    welcome: '欢迎',
    back: '回来',
    subtitle: '登录以访问AI智能体平台',
    signIn: '登录',
    register: '注册',
    username: '用户名',
    usernamePh: '请输入用户名',
    password: '密码',
    passwordPh: '请输入密码',
    phone: '手机号',
    phonePh: '请输入手机号',
    realName: '真实姓名',
    optional: '选填',
    passwordRule: '密码长度需大于6位',
    referrerPhone: '推荐人手机号',
    signInBtn: '登录',
    registerBtn: '创建账号',
    loginSuccess: '登录成功',
    loginFail: '登录失败',
    registerSuccess: '注册成功，请登录',
    registerFail: '注册失败',
    required: '用户名、手机号和密码为必填项',
    passwordTooShort: '密码长度必须大于6位'
  },
  admin: {
    title: '管理控制台',
    menu: {
      users: '用户管理',
      roles: '角色权限',
      groups: '分组管理',
      tenants: '租户管理',
      providers: '供应商管理',
      tokens: 'Token统计',
      memory: '记忆查看',
      systemPrompts: '提示词管理',
      chatDebug: '对话调试'
    }
  },
  user: {
    title: '用户中心',
    menu: {
      dashboard: '数据中心',
      tenants: '我的租户',
      groups: '分组管理',
      groupTenants: '分组租户',
      tokens: 'Token统计',
      memory: '记忆查看',
      chatDebug: '对话调试'
    }
  },
  profile: {
    title: '个人信息',
    username: '用户名',
    phone: '手机号',
    realName: '真实姓名',
    newPassword: '新密码',
    newPasswordPh: '不修改可留空',
    cancel: '取消',
    save: '保存',
    signOut: '退出登录',
    saveSuccess: '保存成功',
    saveFail: '保存失败',
    loadFail: '加载用户信息失败',
    passwordTooShort: '密码长度必须大于6位'
  }
}

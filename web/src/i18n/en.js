export default {
  lang: { zh: '中文', en: 'English', ja: '日本語' },
  nav: {
    home: 'Home',
    docs: 'Docs',
    about: 'About',
    marketplace: 'Marketplace'
  },
  home: {
    subtitle: 'Clone Human Intelligence',
    heroTitle1: 'Clone Top Talent\'s',
    heroTitle2: 'Thinking Engine',
    heroDesc: 'A minimalist personal capability trading center. Transform expert experience into elastically scalable digital assets through neural extraction technology.',
    quickStart: 'Quick Start',
    learnMore: 'Learn More',
    hirePrice: 'Hire Price',
    memory: 'Memory',
    duration: 'Duration',
    hires: 'Hires'
  },
  footer: {
    desc: 'We are redefining the meaning of "hiring". Commercializing personal experience is the first step towards global productivity equality.',
    navigate: 'Navigate',
    connect: 'Connect',
    copyright: 'Mr.Joe © 2026 AI Agent Market.',
    slogan: 'Designed for the intelligence era.'
  },
  about: {
    title: 'About',
    titleHighlight: 'Agent Market',
    subtitle: 'Connect with partners, build an intelligent future together',
    formTitle: 'Cooperation Inquiry',
    formDesc: 'Fill in your details and we\'ll get back to you shortly',
    company: 'Company Name',
    companyPh: 'Enter company name',
    contact: 'Contact Info',
    contactPh: 'Email or phone',
    intention: 'Cooperation Type',
    intentionPh: 'Select cooperation type',
    intentionOpts: {
      tech: 'Technical Cooperation',
      business: 'Business Partnership',
      invest: 'Investment',
      other: 'Other'
    },
    purpose: 'Project Purpose',
    purposePh: 'Briefly describe your project and requirements...',
    submit: 'Submit',
    submitSuccess: 'Submitted! We\'ll contact you shortly.',
    submitFail: 'Please fill in all fields',
    visionTitle: 'Project Vision',
    visionQuote: 'Monetize human capabilities through AI technology, commercializing professional expertise',
    visionDesc: 'We believe everyone\'s expertise has immeasurable value. Through neural extraction technology, we convert expert experience into scalable digital assets, enabling global productivity equality.',
    initiator: 'Initiator',
    founder: 'Founder'
  },
  docs: {
    title: 'Documentation',
    subtitle: 'Everything you need to deploy, configure, and run the AI Agent Marketing Platform.',
    sections: {
      overview: 'Project Overview',
      techStack: 'Tech Stack',
      prerequisites: 'Prerequisites',
      quickStart: 'Quick Start',
      access: 'Access & Credentials',
      architecture: 'Architecture',
      configuration: 'Configuration',
      commands: 'Common Commands'
    },
    overviewDesc: 'AI Agent Marketing Platform is a full-featured AI agent SaaS platform supporting multi-tenancy, referral grouping, dual-layer memory system, and token usage analytics. It enables the commercialization of human expertise through AI-powered agent replication.',
    features: {
      multiTenant: 'Multi-Tenancy',
      multiTenantDesc: 'AppKey/AppSecret auth, tenant-level API isolation, group user binding.',
      dualMemory: 'Dual Memory',
      dualMemoryDesc: 'KV fact memory + recursive behavior digest with cross-layer reference detection.',
      tokenAnalytics: 'Token Analytics',
      tokenAnalyticsDesc: 'Real-time usage stats, monthly comparison, 30-day trend visualization.',
      referralGroups: 'Referral Groups',
      referralGroupsDesc: 'Referral-based user grouping, automatic group creation and tenant sharing.'
    },
    backend: 'Backend',
    frontend: 'Frontend',
    option1: 'Option 1: Docker Compose (Recommended)',
    option2: 'Option 2: Startup Script (Windows)',
    option2Desc: 'The script auto-checks Docker, builds, and starts all services.',
    option3: 'Option 3: Local Development',
    defaultAdmin: 'Default Admin Account',
    dockerSteps: {
      step1: 'Clone the repository',
      step2: 'Start all services',
      step3: 'Wait for startup (1-2 min), then verify'
    },
    archBlocks: {
      proxy: 'AI Proxy',
      proxyDesc: 'Unified API to multiple LLM providers with stream support',
      memory: 'Dual Memory',
      memoryDesc: 'KV fact storage + recursive behavior digest compression',
      analytics: 'Token Analytics',
      analyticsDesc: 'Real-time usage tracking with 30-day trend visualization'
    },
    memorySystem: 'Memory System',
    envVars: 'Environment Variables',
    commands: {
      viewLogs: 'View all logs',
      restart: 'Restart services',
      stop: 'Stop services',
      resetDb: 'Reset database',
      rebuild: 'Rebuild after code changes'
    }
  },
  login: {
    welcome: 'Welcome',
    back: 'Back',
    subtitle: 'Sign in to access the AI Agent platform',
    signIn: 'Sign In',
    register: 'Register',
    username: 'Username',
    usernamePh: 'Enter username',
    password: 'Password',
    passwordPh: 'Enter password',
    phone: 'Phone',
    phonePh: 'Phone number',
    realName: 'Real Name',
    optional: 'Optional',
    passwordRule: 'Must be longer than 6 characters',
    referrerPhone: 'Referrer Phone',
    signInBtn: 'Sign In',
    registerBtn: 'Create Account',
    loginSuccess: 'Login successful',
    loginFail: 'Login failed',
    registerSuccess: 'Registration successful, please sign in',
    registerFail: 'Registration failed',
    required: 'Username, phone, and password are required',
    passwordTooShort: 'Password must be longer than 6 characters'
  },
  admin: {
    title: 'Admin Console',
    menu: {
      users: 'Users',
      roles: 'Roles',
      groups: 'Groups',
      tenants: 'Tenants',
      providers: 'Providers',
      tokens: 'Tokens',
      memory: 'Memory',
      systemPrompts: 'Prompts',
      chatDebug: 'Chat Debug'
    }
  },
  user: {
    title: 'User Dashboard',
    menu: {
      dashboard: 'Dashboard',
      tenants: 'My Tenants',
      groups: 'Groups',
      groupTenants: 'Group Tenants',
      tokens: 'Tokens',
      memory: 'Memory',
      chatDebug: 'Chat Debug'
    }
  },
  profile: {
    title: 'Profile',
    username: 'Username',
    phone: 'Phone',
    realName: 'Real Name',
    newPassword: 'New Password',
    newPasswordPh: 'Leave blank to keep current',
    cancel: 'Cancel',
    save: 'Save',
    signOut: 'Sign Out',
    saveSuccess: 'Saved successfully',
    saveFail: 'Save failed',
    loadFail: 'Failed to load profile',
    passwordTooShort: 'Password must be longer than 6 characters'
  }
}

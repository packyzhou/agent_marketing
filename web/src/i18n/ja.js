export default {
  lang: { zh: '中文', en: 'English', ja: '日本語' },
  nav: {
    home: 'ホーム',
    docs: 'ドキュメント',
    about: '概要',
    marketplace: 'マーケット'
  },
  home: {
    subtitle: 'Clone Human Intelligence',
    heroTitle1: 'トップ人材の',
    heroTitle2: '思考エンジン',
    heroDesc: 'ミニマルな個人能力取引センター。ニューラル抽出技術により、専門家の経験を弾力的に拡張可能なデジタル資産に変換します。',
    quickStart: 'クイックスタート',
    learnMore: '詳細を見る',
    hirePrice: '雇用価格',
    memory: 'メモリ',
    duration: '期間',
    hires: '回雇用'
  },
  footer: {
    desc: '私たちは「雇用」の意味を再定義しています。個人の経験を商品化することは、グローバルな生産性の平等を実現するための第一歩です。',
    navigate: 'ナビゲーション',
    connect: '接続',
    copyright: 'Mr.Joe © 2026 AI Agent Market.',
    slogan: 'インテリジェンス時代のために設計'
  },
  about: {
    title: '概要',
    titleHighlight: 'Agent Market',
    subtitle: 'パートナーと連携し、インテリジェントな未来を共に築く',
    formTitle: '提携のお問い合わせ',
    formDesc: '以下の情報をご記入ください。折り返しご連絡いたします',
    company: '会社名',
    companyPh: '会社名を入力',
    contact: '連絡先',
    contactPh: 'メールまたは電話番号',
    intention: '提携種別',
    intentionPh: '提携種別を選択',
    intentionOpts: {
      tech: '技術提携',
      business: 'ビジネスパートナーシップ',
      invest: '投資',
      other: 'その他'
    },
    purpose: 'プロジェクト用途',
    purposePh: 'プロジェクトの用途と要件を簡潔にご記入ください...',
    submit: '送信',
    submitSuccess: '送信完了。折り返しご連絡いたします。',
    submitFail: 'すべての項目をご記入ください',
    visionTitle: 'プロジェクトビジョン',
    visionQuote: 'AI技術により人間の能力を複製し、専門知識の商業化を実現',
    visionDesc: '私たちは、すべての人の専門知識と経験が計り知れない価値を持つと信じています。ニューラル抽出技術により、専門家の経験をスケーラブルなデジタル資産に変換し、グローバルな生産性の平等を可能にします。',
    initiator: '発起人',
    founder: '創設者'
  },
  docs: {
    title: 'ドキュメント',
    subtitle: 'AI Agent マーケティングプラットフォームのデプロイ、設定、実行に必要なすべての情報。',
    sections: {
      overview: 'プロジェクト概要',
      techStack: '技術スタック',
      prerequisites: '前提条件',
      quickStart: 'クイックスタート',
      access: 'アクセス情報',
      architecture: 'アーキテクチャ',
      configuration: '設定',
      commands: 'よく使うコマンド'
    },
    overviewDesc: 'AI Agent マーケティングプラットフォームは、マルチテナント、紹介グループ、二層メモリシステム、トークン使用量分析をサポートする完全なAIエージェントSaaSプラットフォームです。',
    features: {
      multiTenant: 'マルチテナント',
      multiTenantDesc: 'AppKey/AppSecret認証、テナントレベルAPI分離、グループユーザーバインディング。',
      dualMemory: '二層メモリ',
      dualMemoryDesc: 'KVファクトメモリ + 再帰的行動ダイジェスト圧縮、クロスレイヤー参照検出。',
      tokenAnalytics: 'トークン分析',
      tokenAnalyticsDesc: 'リアルタイム使用統計、月次比較、30日トレンド可視化。',
      referralGroups: '紹介グループ',
      referralGroupsDesc: '紹介ベースのユーザーグループ、自動グループ作成とテナント共有。'
    },
    backend: 'バックエンド',
    frontend: 'フロントエンド',
    option1: '方法1：Docker Compose（推奨）',
    option2: '方法2：起動スクリプト（Windows）',
    option2Desc: 'スクリプトはDocker環境を自動チェックし、ビルドして全サービスを起動します。',
    option3: '方法3：ローカル開発',
    defaultAdmin: 'デフォルト管理者アカウント',
    dockerSteps: {
      step1: 'リポジトリをクローン',
      step2: '全サービスを起動',
      step3: '起動を待機（1-2分）、状態を確認'
    },
    archBlocks: {
      proxy: 'AIプロキシ',
      proxyDesc: '複数のLLMプロバイダーへの統一API、ストリーム対応',
      memory: '二層メモリ',
      memoryDesc: 'KVファクトストレージ + 再帰的行動ダイジェスト圧縮',
      analytics: 'トークン分析',
      analyticsDesc: 'リアルタイム使用追跡、30日トレンド可視化'
    },
    memorySystem: 'メモリシステム',
    envVars: '環境変数',
    commands: {
      viewLogs: '全ログを表示',
      restart: 'サービスを再起動',
      stop: 'サービスを停止',
      resetDb: 'データベースをリセット',
      rebuild: 'コード変更後に再ビルド'
    }
  },
  login: {
    welcome: 'ようこそ',
    back: '',
    subtitle: 'AIエージェントプラットフォームにサインイン',
    signIn: 'ログイン',
    register: '新規登録',
    username: 'ユーザー名',
    usernamePh: 'ユーザー名を入力',
    password: 'パスワード',
    passwordPh: 'パスワードを入力',
    phone: '電話番号',
    phonePh: '電話番号を入力',
    realName: '氏名',
    optional: '任意',
    passwordRule: '6文字以上',
    referrerPhone: '紹介者の電話番号',
    signInBtn: 'ログイン',
    registerBtn: 'アカウント作成',
    loginSuccess: 'ログイン成功',
    loginFail: 'ログイン失敗',
    registerSuccess: '登録成功。ログインしてください',
    registerFail: '登録失敗',
    required: 'ユーザー名、電話番号、パスワードは必須です',
    passwordTooShort: 'パスワードは6文字以上必要です'
  },
  admin: {
    title: '管理コンソール',
    menu: {
      users: 'ユーザー管理',
      roles: 'ロール権限',
      groups: 'グループ管理',
      tenants: 'テナント管理',
      providers: 'プロバイダー管理',
      tokens: 'トークン統計',
      memory: 'メモリ閲覧',
      chatDebug: 'チャットデバッグ'
    }
  },
  user: {
    title: 'ユーザーダッシュボード',
    menu: {
      dashboard: 'ダッシュボード',
      tenants: 'マイテナント',
      groups: 'グループ管理',
      groupTenants: 'グループテナント',
      tokens: 'トークン統計',
      memory: 'メモリ閲覧',
      chatDebug: 'チャットデバッグ'
    }
  },
  profile: {
    title: 'プロフィール',
    username: 'ユーザー名',
    phone: '電話番号',
    realName: '氏名',
    newPassword: '新しいパスワード',
    newPasswordPh: '変更しない場合は空欄',
    cancel: 'キャンセル',
    save: '保存',
    signOut: 'ログアウト',
    saveSuccess: '保存しました',
    saveFail: '保存に失敗しました',
    loadFail: 'プロフィールの読み込みに失敗しました',
    passwordTooShort: 'パスワードは6文字以上必要です'
  }
}

import { createI18n } from 'vue-i18n'
import zh from './zh.js'
import en from './en.js'
import ja from './ja.js'

const savedLocale = localStorage.getItem('locale') || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { zh, en, ja }
})

export default i18n

import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

let locale = navigator.language.split('-')[0]
if (locale) {
    locale = ['es', 'en', 'fr', 'de'].indexOf(locale) === -1 ? 'en' : locale
} else {
    locale = 'en'
}

function loadLocaleMessages() {
    const locales = require.context(
        './locales',
        true,
        /[A-Za-z0-9-_,\s]+\.json$/i
    )
    const messages = {}
    locales.keys().forEach(key => {
        const matched = key.match(/([A-Za-z0-9-_]+)\./i)
        if (matched && matched.length > 1) {
            const locale = matched[1]
            messages[locale] = locales(key)
        }
    })
    return messages
}

export default new VueI18n({
    locale,
    fallbackLocale: 'en',
    messages: loadLocaleMessages(),
})

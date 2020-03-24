import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import VueAnalytics from 'vue-analytics'
import i18n from './i18n'
import mixin from './mixin'
import 'material-design-icons-iconfont/dist/material-design-icons.css'

Vue.config.productionTip = false
Vue.mixin(mixin)
Vue.use(VueAnalytics, {
    id: 'UA-226788719-1',
    checkDuplicatedScript: true,
})

new Vue({
    vuetify,
    i18n,
    render: h => h(App),
}).$mount('#app')

import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import i18n from './i18n'
import mixin from './mixin'
import 'material-design-icons-iconfont/dist/material-design-icons.css'

Vue.config.productionTip = false
Vue.mixin(mixin)

new Vue({
    vuetify,
    i18n,
    render: h => h(App),
}).$mount('#app')

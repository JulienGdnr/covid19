<template>
    <v-app>
        <v-col>
            <v-card-actions class="justify-space-between blue-grey lighten-5">
                <v-btn text @click="prev">
                    <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-item-group v-model="window" class="text-center" mandatory>
                    <v-item
                        v-for="n in 2"
                        :key="`btn-${n}`"
                        v-slot:default="{ active, toggle }"
                    >
                        <v-btn :input-value="active" icon @click="toggle">
                            <v-icon>mdi-record</v-icon>
                        </v-btn>
                    </v-item>
                </v-item-group>
                <v-btn text @click="next">
                    <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
            </v-card-actions>
            <v-row :justify="breakpoint == 'xs' ? '' : 'space-around'">
                <v-col :cols="breakpoint == 'xs' ? '' : '2'">
                    <v-select
                        outlined
                        dense
                        :label="$t('choose') + ' ' + $t('measure')"
                        width="100"
                        :items="measures"
                        v-model="measure"
                    ></v-select>
                </v-col>
                <v-col :cols="breakpoint == 'xs' ? '' : '2'">
                    <v-select
                        outlined
                        dense
                        :label="$t('choose') + ' ' + $t('lang')"
                        width="100"
                        :items="langs"
                        v-model="lang"
                    ></v-select>
                </v-col>
                <v-col :cols="breakpoint == 'xs' ? '' : '2'">
                    <v-select
                        outlined
                        dense
                        max-width="50"
                        :label="$t('top') + ' ' + $t('countries')"
                        :items="items"
                        type="number"
                        v-model="top"
                    ></v-select>
                </v-col>
                <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    v-if="mode == 'bar'"
                >
                    <v-radio-group
                        class="mt-n3"
                        :dense="breakpoint == 'xs'"
                        v-model="choice"
                    >
                        <v-radio
                            v-for="c in choices"
                            :key="c"
                            :value="c"
                            :label="$t(c)"
                        ></v-radio>
                    </v-radio-group>
                </v-col>
            </v-row>
            <v-row justify="center" v-if="mode == 'bar'"
                ><v-subheader
                    :class="breakpoint == 'xs' ? 'pa-0 ma-0' : 'title'"
                    v-html="vertical_description"
                ></v-subheader
            ></v-row>
            <bar-chart
                :top="top"
                :lang="lang"
                :choice="choice"
                :measures="measures"
                :measure="measure"
                @getData="choice = 'stacked'"
                v-if="window == 0 && !moving"
            />
            <race-chart
                :top="top"
                :lang="lang"
                :measures="measures"
                :measure="measure"
                v-if="window == 1 && !moving"
            />
        </v-col>
        <v-footer dark padless>
            <v-card light class="flex" flat tile>
                <v-card-title class="blue-grey lighten-5">
                    <strong class="subheading"
                        >In support of all the volunteers on the planet</strong
                    >

                    <v-spacer></v-spacer>

                    <a
                        style="text-decoration:none"
                        v-for="icon in icons"
                        :key="icon.i"
                        class="mx-4"
                        dark
                        :href="icon.l"
                        target="_blank"
                        icon
                    >
                        <v-icon size="24px">{{ icon.i }}</v-icon>
                    </a>
                </v-card-title>

                <v-card-text dark class="py-2 white--text text-center black">
                    {{ new Date().getFullYear() }} —
                    <strong
                        >Designed with ❤️ by
                        <a
                            target="_blank"
                            href="https://github.com/JulienGdnr/covid19"
                            >@julien godenir</a
                        >
                        to help raise awareness on covid19</strong
                    >
                </v-card-text>
            </v-card>
        </v-footer>
    </v-app>
</template>

<script>
import BarChart from '@/components/BarChart'
import RaceChart from '@/components/RaceChart'
let items = []
for (let i = 1; i <= 20; i++) {
    items.push(i)
}
export default {
    name: 'App',
    components: {
        BarChart,
        RaceChart,
    },
    data: () => ({
        top: 10,
        choice: 'stacked',
        choices: ['stacked', 'percent'],
        measure: 'confirmed_deaths_recovered',
        lang: 'en',
        items,
        window: 0,
        moving: false,
        icons: [
            {
                i: 'fab fa-facebook',
                l: 'https://www.facebook.com/vidacolombiaorg/',
            },
            { i: 'fas fa-globe', l: 'https://vidacolombia.org/' },
            { i: 'fab fa-twitter', l: 'https://twitter.com/VidaColombia1' },
            {
                i: 'fab fa-linkedin',
                l: 'https://www.linkedin.com/in/julien-godenir/',
            },
            {
                i: 'fab fa-instagram',
                l: 'https://www.instagram.com/vidacolombia/',
            },
        ],
    }),
    computed: {
        breakpoint() {
            return this.$vuetify.breakpoint.name
        },
        mode() {
            return ['bar', 'race'][this.window]
        },
        color() {
            return {
                confirmed_deaths_recovered: 'orange',
                confirmed: 'blue',
                deaths: 'red',
                recovered: 'green',
            }[this.measure]
        },
        vertical_description() {
            return this.$t('vertical_desc')
                .replace(
                    '[x]',
                    `<b style="color:${this.color}">&nbsp;${this.measureNames[
                        this.measure
                    ].toLowerCase()}&nbsp;</b>`
                )
                .replace('[y]', this.$t('countries'))
                .replace('[z]', this.$t('top').toLowerCase() + ' ' + this.top)
        },
        measures() {
            if (this.mode == 'bar') {
                return [
                    'confirmed_deaths_recovered',
                    'confirmed',
                    'deaths',
                    'recovered',
                ].map(value => ({ value, text: this.$t(value) }))
            } else {
                return [
                    'confirmed_deaths_recovered',
                    'confirmed',
                    'deaths',
                    'recovered',
                    'deaths_pop',
                    'deaths_area',
                    'recovered_pop',
                    'recovered_area',
                    'confirmed_pop',
                    'confirmed_area',
                    'confirmed_deaths_recovered_pop',
                    'confirmed_deaths_recovered_area',
                ].map(value => ({ value, text: this.$t(value) }))
            }
        },
        measureNames() {
            return this.measures.reduce((p, c) => {
                p[c.value] = c.text
                return p
            }, {})
        },
        langs() {
            return ['en', 'fr', 'es'].map(value => ({
                value,
                text: this.$t(value, value),
            }))
        },
    },
    methods: {
        prev() {
            if (this.window == 0) {
                this.window = 1
            } else {
                this.window--
            }
        },
        next() {
            if (this.window == 1) {
                this.window = 0
            } else {
                this.window++
            }
        },
    },
    mounted() {
        this.lang = this.$i18n.locale
    },
    watch: {
        lang(val) {
            this.$i18n.locale = val
        },
        window(val) {
            if (
                val == 0 &&
                [
                    'confirmed_deaths_recovered',
                    'confirmed',
                    'deaths',
                    'recovered',
                ].indexOf(this.measure) == -1
            ) {
                this.measure = 'confirmed_deaths_recovered'
                this.moving = true
                setTimeout(
                    () => {
                        this.moving = false
                    },
                    500,
                    this
                )
            }
        },
    },
}
</script>
<style></style>

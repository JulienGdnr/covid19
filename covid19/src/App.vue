<template>
    <v-app>
        <v-col>
            <v-card-actions class="justify-space-between blue-grey lighten-5">
                <v-btn text @click="prev">
                    <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-item-group v-model="window" class="text-center" mandatory>
                    <v-item
                        v-for="(n, i) in windows"
                        :key="`btn-${i}`"
                        v-slot:default="{ active, toggle }"
                    >
                        <v-btn :input-value="active" icon @click="toggle">
                            <v-icon :style="i == 0 ? 'transform:rotate(90deg)' : ''">{{ n }}</v-icon>
                        </v-btn>
                    </v-item>
                </v-item-group>
                <v-btn text @click="next">
                    <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
            </v-card-actions>
            <v-row
                :justify="breakpoint == 'xs' ? '' : 'space-around'"
                :class="breakpoint == 'xs' ? 'mt-3 mx-1' : ''"
            >
                <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                >
                    <v-select
                        outlined
                        dense
                        :label="
                            $t('choose') +
                            ' ' +
                            $t('measure') +
                            (mode == 'bubble' ? ' X' : '')
                        "
                        width="100"
                        :items="measures"
                        v-model="measure"
                    ></v-select>
                </v-col>
                <v-col
                    v-if="mode == 'bubble'"
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                >
                    <v-select
                        outlined
                        dense
                        :label="$t('choose') + ' ' + $t('measure') + ' Y'"
                        width="100"
                        :items="measures"
                        v-model="measure2"
                    ></v-select>
                </v-col>
                <v-col
                    v-if="mode == 'map'"
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                >
                    <v-select
                        outlined
                        dense
                        :label="$t('choose') + ' ' + $t('projection')"
                        width="100"
                        :items="projections"
                        v-model="projection"
                    ></v-select>
                </v-col>
                <!-- <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                    v-if="mode != 'bar'"
                >
                    <v-radio-group class="mt-n3" :dense="breakpoint == 'xs'" v-model="log">
                        <v-radio :value="false" :label="$t('Normal')"></v-radio>
                        <v-radio :value="true" :label="$t('Logarithmic')"></v-radio>
                    </v-radio-group>
                </v-col>-->
                <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                    v-if="mode != 'map'"
                >
                    <v-radio-group class="mt-n3" :dense="breakpoint == 'xs'" v-model="continent">
                        <v-radio :value="false" :label="$t('by')+' '+$t('country')"></v-radio>
                        <v-radio :value="true" :label="$t('by')+' '+$t('continent')"></v-radio>
                    </v-radio-group>
                </v-col>
                <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                    v-if="mode == 'bar'"
                >
                    <v-radio-group class="mt-n3" :dense="breakpoint == 'xs'" v-model="cumulated">
                        <v-radio :value="true" :label="$t('cumulated')"></v-radio>
                        <v-radio :value="false" :label="$t('not_cumulated')"></v-radio>
                    </v-radio-group>
                </v-col>
                <v-col
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                    v-if="mode == 'bar'"
                >
                    <v-radio-group class="mt-n3" :dense="breakpoint == 'xs'" v-model="choice">
                        <v-radio v-for="c in choices" :key="c" :value="c" :label="$t(c)"></v-radio>
                    </v-radio-group>
                </v-col>
                <v-col
                    v-if="['race', 'bar'].indexOf(mode) != -1"
                    :cols="breakpoint == 'xs' ? '' : '2'"
                    :class="breakpoint == 'xs' ? 'pa-1' : ''"
                >
                    <v-select
                        :disabled="continent"
                        outlined
                        dense
                        max-width="50"
                        :label="$t('top') + ' ' + $t('countries')"
                        :items="items"
                        type="number"
                        v-model="top"
                    ></v-select>
                </v-col>
            </v-row>
            <race-chart
                :top="top"
                :lang="lang"
                :measures="measures"
                :measure="measure"
                :continent="continent"
                v-if="mode == 'race'"
                :remove="remove"
            />
            <bar-chart
                :delta="delta"
                :continent="continent"
                :top="top"
                :lang="lang"
                :choice="choice"
                :measures="measures"
                :measure="measure"
                @getData="choice = 'stacked'"
                v-if="mode == 'bar'"
                :remove="remove"
            />
            <bubble-chart
                :top="top"
                :continent="continent"
                :lang="lang"
                :measures="measures"
                :measureX="measure"
                :measureY="measure2"
                :log="log"
                v-if="mode == 'bubble'"
                :remove="remove"
            />
            <line-chart
                :top="top"
                :lang="lang"
                :continent="continent"
                :measures="measures"
                :measure="measure"
                :log="log"
                v-if="mode == 'line'"
                :remove="remove"
            />
            <map-chart :proj="projection" :measure="measure" :lang="lang" v-if="mode == 'map'" />
        </v-col>
        <v-footer dark padless>
            <v-card light class="flex" flat tile>
                <v-card-title wrap class="blue-grey lighten-5">
                    <strong
                        class="subheading"
                        style="
                            overflow-wrap: normal;
                            text-align: left;
                            word-break: normal;
                        "
                    >{{ $t('volunteer') }}</strong>
                    <v-col
                        align="center"
                        justify="center"
                        class="ma-0 pa-0"
                        :cols="breakpoint == 'xs' ? '' : '2'"
                    >
                        <v-select
                            class="my-0 ml-2 px-0 pt-5"
                            height="25"
                            width="50"
                            outlined
                            dense
                            :label="$t('choose') + ' ' + $t('lang')"
                            :items="langs"
                            v-model="lang"
                        ></v-select>
                    </v-col>
                    <v-spacer></v-spacer>
                    <v-row align="end" justify="start">
                        <a
                            style="text-decoration: none;"
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
                    </v-row>
                </v-card-title>

                <v-card-text dark class="py-2 white--text text-center black">
                    {{ new Date().getFullYear() }} —
                    <strong>
                        Designed with ❤️ by
                        <a
                            target="_blank"
                            href="https://github.com/JulienGdnr/covid19"
                        >@julien godenir</a>
                        to help raise awareness on covid19
                    </strong>
                </v-card-text>
            </v-card>
        </v-footer>
    </v-app>
</template>

<script>
import BarChart from '@/components/BarChart'
import RaceChart from '@/components/RaceChart'
import LineChart from '@/components/LineChart'
import BubbleChart from '@/components/BubbleChart'
import MapChart from '@/components/MapChart'
let items = []
for (let i = 1; i <= 20; i++) {
    items.push(i)
}
export default {
    name: 'App',
    components: {
        BarChart,
        RaceChart,
        LineChart,
        MapChart,
        BubbleChart,
    },
    data: () => ({
        top: 10,
        choice: 'stacked',
        choices: ['stacked', 'percent'],
        measure: 'confirmed_deaths_recovered',
        measure2: 'deaths',
        cumulated: true,
        continent: false,
        lang: 'en',
        items,
        window: 0,
        windows: [
            'bar_chart',
            'multiline_chart',
            'bubble_chart',
            // 'language',
            'bar_chart',
        ],
        log: false,
        projection: 'geoOrthographic',
        projections: [
            'geoOrthographic',
            'geoMiller',
            'geoAitoff',
            'geoLagrange',
            'geoBromley',
            'geoGilbert',
        ].map(value => ({ value, text: value.replace('geo', '') })),
        icons: [
            {
                i: 'fab fa-github',
                l: 'https://github.com/JulienGdnr/covid19',
            },
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
        baseMeasures: [
            'confirmed_deaths_recovered',
            'confirmed',
            'deaths',
            'recovered',
        ],
        remove: false,
    }),
    computed: {
        delta() {
            return !this.cumulated
        },
        mode() {
            return ['race', 'line', 'bubble', 'bar'][this.window]
        },
        color() {
            return {
                confirmed_deaths_recovered: 'orange',
                confirmed: 'blue',
                deaths: 'red',
                recovered: 'green',
            }[this.measure]
        },
        measures() {
            if (this.mode == 'bar') {
                return this.baseMeasures
                    .filter(
                        m =>
                            m.indexOf('confirmed_deaths_recovered') == -1 ||
                            !this.delta
                    )
                    .map(value => ({ value, text: this.$t(value) }))
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
                ]
                    .filter(
                        m =>
                            m.indexOf('confirmed_deaths_recovered') == -1 ||
                            !this.delta
                    )
                    .map(value => ({ value, text: this.$t(value) }))
            }
        },
        measureNames() {
            return this.measures.reduce((p, c) => {
                p[c.value] = c.text
                return p
            }, {})
        },
        langs() {
            return ['en', 'fr', 'es', 'de'].map(value => ({
                value,
                text: this.$t(value, value),
            }))
        },
    },
    methods: {
        prev() {
            this.remove = !this.remove
            this.$nextTick(() => {
                if (this.window == 0) {
                    this.window = this.windows.length - 1
                } else {
                    this.window--
                }
            }, this)
        },
        next() {
            this.remove = !this.remove
            this.$nextTick(() => {
                if (this.window == this.windows.length - 1) {
                    this.window = 0
                } else {
                    this.window++
                }
            }, this)
        },
    },
    mounted() {
        this.lang = this.$i18n.locale
    },
    watch: {
        delta(val) {
            if (
                val &&
                this.measure.indexOf('confirmed_deaths_recovered') != -1
            ) {
                this.measure = 'confirmed'
            }
        },
        continent(val) {
            if (val) {
                this.top = 10
            }
        },
        lang(val) {
            this.$i18n.locale = val
        },
        mode(val) {
            if (val == 'bubble') {
                if (this.measure == this.measure2) {
                    // we need to change this.measure2
                    const sufixes = ['_pop', '_area']
                    let found = false
                    sufixes.forEach(_ => {
                        if (this.measure.indexOf(_) != -1) {
                            found = true
                            let start = this.measure.replace(_, '')
                            for (let i of this.baseMeasures) {
                                if (i != start) {
                                    this.measure2 = i + _
                                    break
                                }
                            }
                        }
                    })
                    if (!found) {
                        for (let i of this.baseMeasures) {
                            if (i != this.measure) {
                                this.measure2 = i
                                break
                            }
                        }
                    }
                }
            } else if (
                val == 'bar' &&
                [
                    'confirmed_deaths_recovered',
                    'confirmed',
                    'deaths',
                    'recovered',
                ].indexOf(this.measure) == -1
            ) {
                this.measure = 'confirmed_deaths_recovered'
            }
        },
    },
}
</script>
<style>
text {
    font: 10px sans-serif;
}

.axis path,
.axis line {
    fill: none;
    stroke: #000;
    shape-rendering: crispEdges;
}

div.tooltip {
    position: absolute;
    text-align: center;
    width: auto;
    height: auto;
    padding: 10px;
    margin: 2px;
    white-space: nowrap;
    color: #000;
    font: 13px sans-serif;
    border-radius: 8px;
    background-color: #fff;
    box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1),
        0 5px 15px rgba(0, 0, 0, 0.07);
    pointer-events: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    opacity: 1;
    z-index: 1000;
}
.legendOrdinal path {
    fill: white;
    stroke: black;
    opacity: 0.8;
}
rect {
    opacity: 0.7;
    cursor: pointer;
}
#test_0_0 > rect:hover {
    background: red;
}
rect:hover {
    opacity: 1;
}
</style>

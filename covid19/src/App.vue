<template>
    <v-app>
        <v-col>
            <v-row justify="space-around">
                <v-col cols="2">
                    <v-select
                        outlined
                        dense
                        :label="$t('choose', lang) + ' ' + $t('measure', lang)"
                        width="100"
                        :items="measures"
                        v-model="measure"
                    ></v-select>
                </v-col>
                <v-col cols="2">
                    <v-select
                        outlined
                        dense
                        :label="$t('choose', lang) + ' ' + $t('lang', lang)"
                        width="100"
                        :items="langs"
                        v-model="lang"
                    ></v-select>
                </v-col>
                <v-col cols="2">
                    <v-select
                        outlined
                        dense
                        max-width="50"
                        :label="$t('top', lang) + ' ' + $t('countries', lang)"
                        :items="items"
                        type="number"
                        v-model="top"
                    ></v-select>
                </v-col>
                <v-col cols="2">
                    <v-radio-group
                        class="mt-n4"
                        :label="
                            $t('choose', lang) + ' ' + $t('graph_type', lang)
                        "
                        v-model="choice"
                    >
                        <v-radio
                            v-for="c in choices"
                            :key="c"
                            :value="c"
                            :label="$t(c, lang)"
                        ></v-radio>
                    </v-radio-group>
                </v-col>
            </v-row>
            <v-row justify="center"
                ><v-subheader
                    class="title"
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
            />
        </v-col>
    </v-app>
</template>

<script>
import BarChart from '@/components/BarChart'
let items = []
for (let i = 1; i < 20; i++) {
    items.push(i)
}
export default {
    name: 'App',
    components: {
        BarChart,
    },
    data: () => ({
        top: 10,
        choice: 'stacked',
        choices: ['stacked', 'percent'],
        measure: 'confirmed_deaths_recovered',
        lang: 'en',
        items,
    }),
    computed: {
        color() {
            return {
                confirmed_deaths_recovered: 'orange',
                confirmed: 'blue',
                deaths: 'red',
                recovered: 'green',
            }[this.measure]
        },
        vertical_description() {
            return this.$t('vertical_desc', this.lang)
                .replace(
                    '[x]',
                    `<b style="color:${this.color}">&nbsp;${this.measureNames[
                        this.measure
                    ].toLowerCase()}&nbsp;</b>`
                )
                .replace('[y]', this.$t('countries', this.lang))
                .replace(
                    '[z]',
                    this.$t('top', this.lang).toLowerCase() + ' ' + this.top
                )
        },
        measures() {
            return [
                'confirmed_deaths_recovered',
                'confirmed',
                'deaths',
                'recovered',
            ].map(value => ({ value, text: this.$t(value, this.lang) }))
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
}
</script>
<style></style>

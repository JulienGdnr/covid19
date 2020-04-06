<template>
    <v-col>
        <v-row align="center" justify="center" class="mb-3">
            <p class="title" v-html="sentence"></p>
            <v-btn
                v-if="i == dates.length - 1"
                rounded
                :icon="breakpoint == 'xs'"
                class="ml-4"
                :outlined="breakpoint != 'xs'"
                @click=";(i = 0), iterate()"
            >
                <v-icon>refresh</v-icon>
                {{ breakpoint != 'xs' ? $t('refresh') : '' }}
            </v-btn>
        </v-row>
        <v-slider
            @end="iterate()"
            @mouseup="iterate()"
            :max="Math.max(dates.length - 1, 0)"
            :min="0"
            v-model="i"
            :disabled="!stopped && false"
        >
            <template v-slot:append>
                <v-btn
                    style="transform: translateY(-5px);"
                    icon
                    color="blue"
                    @click="stopped = !stopped"
                >
                    <v-icon>{{ stopped ? 'play_arrow' : 'pause' }}</v-icon>
                </v-btn>
            </template>
        </v-slider>

        <v-row align="center" justify="center">
            <v-spacer></v-spacer>
            <v-progress-circular indeterminate size="50" color="primary" v-if="loading"></v-progress-circular>
            <div id="containerRaceChart" :style="!loading ? style : ''"></div>
            <v-spacer></v-spacer>
        </v-row>
    </v-col>
</template>

<script>
import countries from '@/../public/countries.json'
import continents from '@/../public/continents.json'
import * as d3 from 'd3'
import { schemeCategory10 } from 'd3-scale-chromatic'
import { easeLinear } from 'd3-ease'
import { format } from 'date-fns'
import { de, fr, es } from 'date-fns/locale'
const locales = { de, fr, es }

export default {
    name: 'raceChart',
    props: {
        measure: {
            type: String,
            required: true,
        },
        lang: {
            type: String,
            required: true,
        },
        top: {
            type: Number,
            required: true,
        },
        continent: {
            type: Boolean,
            required: true,
        },
        remove: {
            type: Boolean,
            required: true,
        },
        measures: {
            type: Array,
        },
    },
    data: () => ({
        loading: false,
        getting: false,
        stopped: false,
        height: 600,
        barSize: 48,
        width: 960,
        duration: 800,
        dateSlice: null,

        k: 10,
        svg: null,
        title: null,
        subtitle: null,
        caption: null,
        rawData: { data: [], dates: [] },
        countryMap: countries,
        continentMap: continents,
        i: 0,
        dateText: null,
        locales,
        ticker: null,
    }),
    computed: {
        margin() {
            return {
                top: 35,
                right: 50,
                bottom: 25,
                left: 80,
            }
        },
        sentence() {
            return `${!this.continent ? this.top : ''} ${this.$t(
                'most'
            ).replace(
                '[c]',
                this.continent
                    ? this.toTitleCase(this.$t('continent'))
                    : this.$t('countries')
            )} <span style="color:${this.textColor}">&nbsp;${this.$t(
                this.measure
            ).toLowerCase()}&nbsp;</span> ${this.nice_date}`
        },
        nice_date() {
            return this.lang == 'en'
                ? format(new Date(this.date), 'd MMMM')
                : format(new Date(this.date), 'd MMMM', {
                      locale: locales[this.lang],
                  })
        },
        x() {
            return d3.scaleLinear(
                [0, 1],
                [this.margin.left, this.width - this.margin.right]
            )
        },
        y() {
            return d3
                .scaleLinear()
                .domain([this.top, 0])
                .range([this.height - this.margin.bottom, this.margin.top])
        },
        xAxis() {
            return d3
                .axisTop()
                .scale(this.x)
                .ticks(this.width > 500 ? 5 : 2)
                .tickSize(-(this.height - this.margin.top - this.margin.bottom))
                .tickFormat(d => d3.format(',')(d))
        },
        date() {
            return this.dates.length > this.i
                ? this.dates[this.i]
                : '2000-01-01'
        },
        data() {
            return this.rawData.data.map(d => ({
                ...d,
                color: this.has_color[d.code]
                    ? this.has_color[d.code]
                    : this.countryColor[d.code],
                name: this.countryNames[d.code],
            }))
        },
        barPadding() {
            return (
                (this.height - (this.margin.bottom + this.margin.top)) /
                (this.top * 5)
            )
        },
        dates() {
            return this.rawData.dates
        },
        codes() {
            return new Set(this.rawData.data.map(d => d.code))
        },
        arrayCodes() {
            return Array.from(this.codes).sort((a, b) => a - b)
        },
        countryColor() {
            return this.arrayCodes
                .map((code, i) => {
                    return { code, color: schemeCategory10[i % 10] }
                })
                .reduce((p, c) => {
                    p[c.code] = c.color
                    return p
                }, {})
        },
        countryNames() {
            return Array.from(this.codes).reduce((p, c) => {
                if (this.continent) {
                    p[c] = this.continentMap[c]['continent_' + this.lang]
                } else {
                    p[c] = this.countryMap[c]['country_' + this.lang]
                }
                return p
            }, {})
        },
        dateValues() {
            let o = {}
            for (let row of this.rawData.data) {
                o[row.date] = o[row.date] ? o[row.date] : {}
                o[row.date][row.code] = o[row.date][row.code]
                    ? o[row.date][row.code]
                    : row.value
            }
            return this.dates.map(d => {
                const m = Array.from(this.codes).reduce((p, c) => {
                    p[c] = o[d][c]
                    return p
                }, {})
                return [new Date(d), m]
            })
        },
    },
    methods: {
        toTitleCase(str) {
            return str.replace(/\w\S*/g, function(txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
            })
        },

        halo(text, strokeWidth) {
            text.select(function() {
                return this.parentNode.insertBefore(this.cloneNode(true), this)
            })
                .style('fill', '#ffffff')
                .style('stroke', '#ffffff')
                .style('stroke-width', strokeWidth)
                .style('stroke-linejoin', 'round')
                .style('opacity', 1)
        },
        formatNumber() {
            return d3.format(',d')
        },
        formatDate() {
            return d3.utcFormat('%Y')
        },
        textTween(a, b) {
            const i = d3.interpolateNumber(a, b)
            return t => {
                this.textContent = this.formatNumber(i(t))
            }
        },
        rank(value) {
            const data = Array.from(this.codes, code => ({
                code,
                value: value(code),
            }))
            data.sort((a, b) => d3.descending(a.value, b.value))
            for (let i = 0; i < data.length; ++i)
                data[i].rank = Math.min(this.top, i)
            return data
        },
        getData() {
            if (!this.getting) {
                // if (!this.stopped) {
                //     this.i = 0
                //     this.rawData = { data: [], dates: [] }
                // }
                this.getting = true
                this.loading = true
                const d = format(new Date(), 'd-M-Y')
                d3.selectAll('svg').remove()
                return fetch(
                    `/race${this.continent ? '-continent' : ''}/${
                        this.measure
                    }.json?d=${d}`
                )
                    .then(resp => resp.json())
                    .then(res => {
                        this.rawData = res
                        setTimeout(
                            () => {
                                this.loading = false
                                this.getting = false
                                this.mount()
                            },
                            500,
                            this
                        )
                    })
            }
        },
        mount() {
            this.width = Math.min(window.innerWidth - 20, 1000)
            this.height = Math.min(this.width, this.height)
            this.svg = d3
                .select('#containerRaceChart')
                .append('svg')
                .attr('width', this.width)
                .attr('height', this.height)

            this.dateSlice = this.data
                .filter(d => d.date == this.date && !isNaN(d.value))
                .sort((a, b) => b.value - a.value)
                .slice(0, this.top)
                .map((d, i) => (d.rank = i))

            this.svg
                .append('g')
                .attr('class', 'axis xAxis')
                .attr('transform', `translate(0, ${this.margin.top})`)
                .call(this.xAxis)
                .selectAll('.tick line')
                .classed('origin', d => d == 0)

            this.svg
                .selectAll('rect.bar')
                .data(this.dateSlice, d => d.name)
                .enter()
                .append('rect')
                .attr('class', 'bar')
                .attr('x', this.x(0) + 1)
                .attr('width', d =>
                    Math.max(this.x(d.value) - this.x(0) - 1, 0)
                )
                .attr('y', d => this.y(d.rank) + 5 || 0)
                .attr('height', this.y(1) - this.y(0) - this.barPadding)
                .style('fill', d => d.color)

            this.svg
                .selectAll('text.label')
                .data(this.dateSlice, d => d.name)
                .enter()
                .append('text')
                .attr('class', 'label')
                .attr('x', d => this.x(d.value) - 8)
                .attr(
                    'y',
                    d =>
                        this.y(d.rank) + 5 + (this.y(1) - this.y(0)) / 2 + 1 ||
                        0
                )
                .style('text-anchor', 'end')
                .html(d => d.name)

            this.svg
                .selectAll('text.valueLabel')
                .data(this.dateSlice, d => d.name)
                .enter()
                .append('text')
                .attr('class', 'valueLabel')
                .attr('x', d => this.x(d.value) + 5)
                .attr(
                    'y',
                    d =>
                        this.y(d.rank) + 5 + (this.y(1) - this.y(0)) / 2 + 1 ||
                        0
                )
                .text(d => d3.format(',.0f')(d.lastValue))

            if (!this.stopped) {
                this.iterate()
            }
        },
        iterate() {
            console.log(this.i)
            // this.$nextTick(() => {
            let ctx = this
            if (!this.ticker) {
                this.ticker = d3.interval(() => {
                    ctx.dateSlice = ctx.data
                        .filter(d => d.date == ctx.date && !isNaN(d.value))
                        .sort((a, b) => b.value - a.value)
                        .slice(0, ctx.top)

                    ctx.dateSlice.forEach((d, i) => (d.rank = i))

                    ctx.x.domain([0, d3.max(ctx.dateSlice, d => d.value)])

                    ctx.svg
                        .select('.xAxis')
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .call(ctx.xAxis)

                    let bars = ctx.svg
                        .selectAll('.bar')
                        .data(ctx.dateSlice, d => d.name)

                    bars.enter()
                        .append('rect')
                        .attr('class', d => `bar ${d.code.replace(/\s/g, '_')}`)
                        .attr('x', ctx.x(0) + 1)
                        .attr('width', d =>
                            Math.max(ctx.x(d.value) - ctx.x(0) - 1, 0)
                        )
                        .attr('y', () => ctx.y(ctx.top + 1) + 5 || 0)
                        .attr('height', ctx.y(1) - ctx.y(0) - ctx.barPadding)
                        .style('fill', d => d.color)
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('y', d => ctx.y(d.rank) + 5 || 0)

                    bars.transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('width', d =>
                            Math.max(ctx.x(d.value) - ctx.x(0) - 1, 0)
                        )
                        .attr('y', d => ctx.y(d.rank) + 5 || 0)

                    bars.exit()
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('width', d =>
                            Math.max(ctx.x(d.value) - ctx.x(0) - 1, 0)
                        )
                        .attr('y', () => ctx.y(ctx.top + 1) + 5 || 0)
                        .remove()

                    let labels = ctx.svg
                        .selectAll('.label')
                        .data(ctx.dateSlice, d => d.name)

                    labels
                        .enter()
                        .append('text')
                        .attr('class', 'label')
                        .attr('x', d => ctx.x(d.value) - 8)
                        .attr(
                            'y',
                            () =>
                                ctx.y(ctx.top + 1) +
                                5 +
                                (ctx.y(1) - ctx.y(0)) / 2
                        )
                        .style('text-anchor', 'end')
                        .html(d => d.name)
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr(
                            'y',
                            d =>
                                ctx.y(d.rank) +
                                5 +
                                (ctx.y(1) - ctx.y(0)) / 2 +
                                1
                        )

                    labels
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('x', d => ctx.x(d.value) - 8)
                        .attr(
                            'y',
                            d =>
                                ctx.y(d.rank) +
                                5 +
                                (ctx.y(1) - ctx.y(0)) / 2 +
                                1
                        )

                    labels
                        .exit()
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('x', d => ctx.x(d.value) - 8)
                        .attr('y', () => ctx.y(ctx.top + 1) + 5)
                        .remove()

                    let valueLabels = ctx.svg
                        .selectAll('.valueLabel')
                        .data(ctx.dateSlice, d => d.name)

                    valueLabels
                        .enter()
                        .append('text')
                        .attr('class', 'valueLabel')
                        .attr('x', d => ctx.x(d.value) + 5)
                        .attr('y', () => ctx.y(ctx.top + 1) + 5)
                        .text(d => d3.format(',.0f')(d.lastValue))
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr(
                            'y',
                            d =>
                                ctx.y(d.rank) +
                                5 +
                                (ctx.y(1) - ctx.y(0)) / 2 +
                                1
                        )

                    valueLabels
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('x', d => ctx.x(d.value) + 5)
                        .attr(
                            'y',
                            d =>
                                ctx.y(d.rank) +
                                5 +
                                (ctx.y(1) - ctx.y(0)) / 2 +
                                1
                        )
                        .tween('text', function(d) {
                            if (
                                ctx.measure.endsWith('p') ||
                                ctx.measure.endsWith('a')
                            ) {
                                let i = d3.interpolateRound(
                                    d.lastValue,
                                    d.value
                                )
                                return function(t) {
                                    this.textContent = d3.format(',')(i(t))
                                }
                            } else {
                                let i = d3.interpolateRound(
                                    d.lastValue,
                                    d.value
                                )
                                return function(t) {
                                    this.textContent = d3.format(',')(i(t))
                                }
                            }
                        })

                    valueLabels
                        .exit()
                        .transition()
                        .duration(ctx.duration)
                        .ease(easeLinear)
                        .attr('x', d => ctx.x(d.value) + 5)
                        .attr('y', () => ctx.y(ctx.top + 1) + 5)
                        .remove()

                    if (
                        ctx.date == ctx.dates[ctx.dates.length - 1] ||
                        ctx.stopped
                    ) {
                        ctx.ticker.stop()
                        ctx.ticker = null
                    } else {
                        ctx.i += 1
                    }
                }, ctx.duration)
            }
        },
    },
    mounted() {
        this.getData()
    },
    watch: {
        remove() {
            d3.selectAll('svg').remove()
        },
        stopped(val) {
            if (!val) {
                this.iterate()
            }
        },
        continent() {
            this.getData()
        },
        measure() {
            this.getData()
        },
        lang() {
            this.getData()
        },
        top() {
            this.getData()
        },
        choice() {
            this.change()
        },
    },
}
</script>

<style></style>

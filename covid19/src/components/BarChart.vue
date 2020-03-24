<template>
    <v-row align="center" justify="center">
        <v-spacer></v-spacer>
        <v-progress-circular
            indeterminate
            size="50"
            color="primary"
            v-if="loading"
        ></v-progress-circular>
        <div
            id="container"
            style="background:#e9e9e9;border-radius:10px"
            v-if="data.length > 0"
        ></div>
        <v-spacer></v-spacer>
    </v-row>
</template>

<script>
import countries from '@/../public/countries.json'
import continents from '@/../public/continents.json'
import * as d3 from 'd3'
import * as d3Scale from 'd3-scale-chromatic'
import * as d3Legend from 'd3-svg-legend'
import { format } from 'date-fns'
import { de, fr, es } from 'date-fns/locale'
const locales = { de, fr, es }
let items = []
for (let i = 1; i < 20; i++) {
    items.push(i)
}
export default {
    name: 'barChart',
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
        choice: {
            type: String,
            required: true,
        },
        measures: {
            type: Array,
        },
    },
    data: () => ({
        dimension: 'country',
        h: 500,
        w: 800,
        x: null,
        y: null,
        svg: null,
        layer: null,
        rect: null,
        layers: [],
        yStackMax: null,
        yGroupMax: null,
        xAxis: null,
        yAxis: null,
        formatNumber: null,
        formatPercent: null,
        formatTime: null,
        tmt: null,
        div: null,
        color: null,
        reversedColor: null,
        legend: null,
        rawData: { data: [], dates: [] },
        countryMap: countries,
        continentMap: continents,
        items,
        i18n: {
            others: {
                fr: 'Autres',
                en: 'Others',
                es: 'Otros',
                de: 'Others',
            },
        },
        locales,
        loading: false,
        has_color: {
            CHN: '#DE2910',
            FRA: '#0055A4',
            ITA: '#008C45',
            ESP: '#F1BF00',
            USA: '#3C3B6E',
            NLD: 'orange',
            IRN: '#C8102E',
            GBR: '#00247D',
            DEU: '#000000',
            others: 'grey',
        },
        getting: false,
    }),
    methods: {
        formatDate(d) {
            return this.lang == 'en'
                ? format(new Date(d), 'd MMM')
                : format(new Date(d), 'd MMM', {
                      locale: locales[this.lang],
                  })
        },
        getData() {
            if (!this.getting) {
                this.$emit('getData')
                this.getting = true
                this.loading = true
                this.rawData = { dates: [], data: [] }
                d3.selectAll('svg').remove()
                return fetch(
                    '/vertical/' + this.measure + '/' + this.top + '.json'
                )
                    .then(resp => resp.json())
                    .then(res => {
                        // this.loading = false
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
            this.w = Math.min(window.innerWidth, 1000)
            this.h = Math.min(0.5 * this.w, this.h)
            if (this.svg) d3.selectAll('svg').remove()
            clearTimeout(this.tmt)
            this.tmt = setTimeout(
                () => {
                    let ctx = this
                    var stack = d3.stack()
                    ctx.div = d3
                        .select('#container')
                        .append('div')
                        .attr('class', 'tooltip')
                        .style('opacity', 0)

                    ctx.formatPercent = d3.format('.0%')
                    ctx.formatNumber = d3.format('')

                    ctx.layers = stack.keys(d3.range(ctx.n))(ctx.data)
                    ctx.yStackMax = d3.max(ctx.layers, layer =>
                        d3.max(layer, d => d[1])
                    )

                    ctx.yGroupMax = d3.max(ctx.layers, layer =>
                        d3.max(layer, d => d[1] - d[0])
                    )

                    ctx.x = d3
                        .scaleBand()
                        .domain(d3.range(ctx.m))
                        .range([0, ctx.width])
                        .padding(0.1)
                        .align(0.1)

                    ctx.y = d3
                        .scaleLinear()
                        .domain([0, ctx.yStackMax])
                        .rangeRound([ctx.height, 0])
                    ctx.color = d3.scaleOrdinal(ctx.colorArray)
                    const reversedArray = []
                    for (let i = ctx.colorArray.length - 1; i >= 0; i--) {
                        reversedArray.push(ctx.colorArray[i])
                    }
                    ctx.reversedColor = d3.scaleOrdinal(reversedArray)

                    ctx.xAxis = d3
                        .axisBottom()
                        .scale(ctx.x)

                        .tickSize(0)
                        .tickPadding(8)
                        .tickFormat((d, i) =>
                            i % ctx.tickBreak == 0
                                ? ctx.formatDate(ctx.dates[i])
                                : ''
                        )

                    ctx.yAxis = d3
                        .axisLeft()
                        .scale(ctx.y)
                        .tickSize(2)
                        .tickPadding(6)

                    ctx.svg = d3
                        .select('#container')
                        .append('svg')
                        .attr(
                            'width',
                            ctx.width + ctx.margin.left + ctx.margin.right
                        )
                        .attr(
                            'height',
                            ctx.height + ctx.margin.top + ctx.margin.bottom
                        )
                        .append('g')
                        .attr(
                            'transform',
                            'translate(' +
                                ctx.margin.left +
                                ',' +
                                ctx.margin.top +
                                ')'
                        )

                    ctx.layer = ctx.svg
                        .selectAll('.layer')
                        .data(ctx.layers)
                        .enter()
                        .append('g')
                        .attr('class', 'layer')
                        .attr('id', (d, i) => 'rect_' + d.key + '_' + i)
                        .style('fill', function(d, i) {
                            return ctx.color(i)
                        })
                    ctx.rect = ctx.layer
                        .selectAll('rect')
                        .data(d => {
                            return d
                        })
                        .enter()
                        .append('rect')
                        .attr('x', function(d, i) {
                            return ctx.x(i)
                        })
                        .attr('y', ctx.height)
                        .attr('width', ctx.x.bandwidth())
                        .attr('height', 0)

                    ctx.rect
                        .transition()
                        .delay(function(d, i) {
                            return i * 10
                        })
                        .attr('y', function(d) {
                            return ctx.y(d[1])
                        })
                        .attr('height', function(d) {
                            return ctx.y(d[0]) - ctx.y(d[1])
                        })

                    ctx.svg
                        .selectAll('rect')
                        .on('mouseover', (d, e) => {
                            let total = d.data.reduce((a, b) => a + b, 0)
                            const indx = Math.floor(e / ctx.m)
                            let dateIndx = e - indx * ctx.m

                            let s = `<div style="text-align:left"><b>${
                                ctx.measureNames[ctx.measure]
                            }</b>, ${ctx.formatDate(
                                ctx.dates[dateIndx]
                            )}<br><br>`
                            const arr = []
                            for (let i in ctx.countries) {
                                let b = i == indx ? '<b>' : ''
                                let bb = i == indx ? '</b>' : ''
                                arr.push(
                                    `${b}${
                                        ctx.countryNames[ctx.countries[i]]
                                    } : ${
                                        ctx.choice == 'stacked'
                                            ? d.data[i]
                                            : Math.floor(
                                                  (d.data[i] / total) * 100
                                              ) + '%'
                                    }${bb}<br>`
                                )
                            }
                            s += arr.reverse().join('')
                            s += '</div>'
                            ctx.div
                                .transition()
                                .duration(200)
                                .style('opacity', 1)
                            ctx.div
                                .html(s)
                                .style('left', d3.event.pageX + 30 + 'px')
                                .style('top', d3.event.pageY - 28 + 'px')
                        })
                        .on('mouseout', () => {
                            ctx.div
                                .transition()
                                .duration(500)
                                .style('opacity', 0)
                        })

                    ctx.svg
                        .append('g')
                        .attr('class', 'x axis')
                        .attr('transform', 'translate(0,' + ctx.height + ')')
                        .call(ctx.xAxis)
                        .selectAll('text')
                        .style('text-anchor', 'end')
                        .attr('dx', '-.8em')
                        .attr('dy', '.15em')
                        .attr('transform', 'rotate(-65)')

                    ctx.svg
                        .append('g')
                        .attr('class', 'y axis')
                        .attr('transform', 'translate(' + 0 + ',0)')
                        .style('font-size', '10px')
                        .call(ctx.yAxis)

                    ctx.svg
                        .append('g')
                        .attr('class', 'legendOrdinal')
                        .attr(
                            'transform',
                            'translate(' +
                                String(
                                    Number(this.w) -
                                        Number(this.margin.right) -
                                        20
                                ) +
                                ',20)'
                        )
                    var legendOrdinal = d3Legend
                        .legendColor()
                        .shape(
                            'path',
                            d3
                                .symbol()
                                .type(d3.symbolCircle)
                                .size(150)()
                        )
                        .shapePadding(10)
                        .scale(
                            ctx.reversedColor.domain(
                                ctx.countries
                                    .map(c => ctx.countryNames[c])
                                    .reverse()
                            )
                        )
                    ctx.svg.select('.legendOrdinal').call(legendOrdinal)
                    ctx.change()
                },
                100,
                this
            )
        },
        transitionPercent() {
            let ctx = this
            ctx.y.domain([0, 1])

            ctx.rect
                .transition()
                .duration(500)
                .delay(function(d, i) {
                    return i * 10
                })
                .attr('y', function(d) {
                    var total = d3.sum(d3.values(d.data))
                    return ctx.y(d[1] / total)
                })
                .attr('height', function(d) {
                    var total = d3.sum(d3.values(d.data))
                    return ctx.y(d[0] / total) - ctx.y(d[1] / total)
                })
                .transition()
                .attr('x', function(d, i) {
                    return ctx.x(i)
                })
                .attr('width', ctx.x.bandwidth())

            ctx.yAxis.tickFormat(ctx.formatPercent)

            ctx.svg
                .selectAll('.y.axis')
                .transition()
                .delay(500)
                .duration(500)
                .call(ctx.yAxis)
        },
        transitionStacked() {
            let ctx = this
            ctx.y.domain([0, ctx.yStackMax])

            ctx.rect
                .transition()
                .duration(500)
                .delay(function(d, i) {
                    return i * 10
                })
                .attr('y', function(d) {
                    return ctx.y(d[1])
                })
                .attr('height', function(d) {
                    return ctx.y(d[0]) - ctx.y(d[1])
                })
                .transition()
                .attr('x', function(d, i) {
                    return ctx.x(i)
                })
                .attr('width', ctx.x.bandwidth())

            ctx.yAxis.tickFormat(ctx.formatNumber)
            ctx.svg
                .selectAll('.y.axis')
                .transition()
                .delay(500)
                .duration(500)
                .call(ctx.yAxis)
        },
        Measure(r) {
            if (this.measure.indexOf('_') == -1) return r[this.measure]
            else {
                const a = this.measure.split('_')
                return r[a[0]] / r[a[1]]
            }
        },
        change() {
            if (this.choice === 'stacked') this.transitionStacked()
            else if (this.choice === 'percent') this.transitionPercent()
        },
    },
    computed: {
        margin() {
            return {
                top: this.breakpoint == 'xs' ? 10 : 40,
                right: this.lang == 'es' ? 160 : 110,
                bottom: 40,
                left: 35,
            }
        },

        colorArray() {
            return this.countries.map((c, i) => {
                if (this.has_color[c]) {
                    return this.has_color[c]
                }
                let idx = Math.floor(i % 10)
                return d3Scale.schemeCategory10[idx]
            })
        },
        tickBreak() {
            if (this.w >= 1000) {
                return 2
            } else if (this.w >= 800) {
                return 4
            } else if (this.w >= 600) {
                return 10
            }
            return 20
        },
        breakpoint() {
            return this.$vuetify.breakpoint.name
        },
        measureNames() {
            return this.measures.reduce((p, c) => {
                p[c.value] = c.text
                return p
            }, {})
        },
        countryNames() {
            let o = {}
            for (let key in this.countryMap) {
                if (!o[key])
                    o[key] = this.countryMap[key]['country_' + this.lang]
            }
            o['others'] = this.i18n.others[this.lang]
            return o
        },
        dates() {
            return this.rawData.dates
        },
        n() {
            return this.top + 1
        },
        m() {
            return this.dates.length
        },
        data() {
            let output = []
            let l = this.rawData.data.length

            for (let i = l - 1; i >= 0; i--) {
                output.push(this.rawData.data[i].values)
            }

            output = output[0].map(function(col, i) {
                return output.map(function(row) {
                    return row[i]
                })
            })
            return output
        },
        countries() {
            return this.rawData.data.map(r => r.code).reverse()
        },
        country_date_measure() {
            let o = {}
            for (let row of this.rawData.data) {
                let code = row.code
                let values = row.values
                for (let i in this.dates) {
                    let date = this.dates[i]
                    if (!o[code]) o[code] = {}
                    if (!o[code][date]) o[code][date] = values[i]
                }
            }
            return o
        },
        width() {
            return this.w - this.margin.left - this.margin.right
        },
        height() {
            return this.h - this.margin.top - this.margin.bottom
        },
    },
    watch: {
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
    mounted() {
        this.getData()
    },
}
</script>

<style>
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: auto;
    position: relative;
    /* width: 960px; */
}

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

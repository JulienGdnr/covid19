<template>
    <v-col>
        <v-slider @end="iterate()" :max="n - 1" :min="0" v-model="i" :disabled="!stopped"></v-slider>

        <v-row align="center" justify="center">
            <v-spacer></v-spacer>
            <v-progress-circular indeterminate size="50" color="primary" v-if="loading"></v-progress-circular>
            <div
                id="containerBubbleChart"
                :style="
                    !loading ? `background:#e9e9e9;border-radius:10px;` : ''
                "
            ></div>
            <v-spacer></v-spacer>
        </v-row>
    </v-col>
</template>

<script>
import countries from '@/../public/countries.json'
import * as d3 from 'd3'
import { schemeCategory10 } from 'd3-scale-chromatic'
import { easeLinear } from 'd3-ease'
import { format } from 'date-fns'
import { de, fr, es } from 'date-fns/locale'
import { interpolatePath } from 'd3-interpolate-path'
const locales = { de, fr, es }
export default {
    name: 'bubbleChart',
    props: {
        measureX: {
            type: String,
            required: true,
        },
        measureY: {
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
        measures: {
            type: Array,
        },
        log: {
            type: Boolean,
            required: true,
        },
    },
    data: () => ({
        loading: false,
        getting: false,
        stopped: false,
        height: 600,
        width: 960,
        duration: 800,
        i: 10,
        margin: {
            top: 35,
            right: 50,
            bottom: 25,
            left: 120,
        },
        rawData: { data: [], range: 0 },
        locales,
        countryMap: countries,
        svg: null,
        xScale: null,
        yScale: null,
        xAxis: null,
        yAxis: null,
        line: null,
    }),
    computed: {
        n() {
            return this.rawData.range
        },
        nice_date() {
            return this.lang == 'en'
                ? format(new Date(this.date), 'd MMMM')
                : format(new Date(this.date), 'd MMMM', {
                      locale: locales[this.lang],
                  })
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
        data() {
            return this.rawData && this.rawData.data ? this.rawData.data : []
        },
        dataset() {
            let output = []
            let r = []
            let country = undefined
            let color = undefined
            let count = 0
            for (let row of this.data) {
                if (row.code != country) {
                    if (country != undefined) {
                        output.push(r)
                    }
                    color = this.has_color[row.code]
                        ? this.has_color[row.code]
                        : this.countryColor[row.code]
                    country = row.code
                    r = []
                    count = 0
                }
                if (count <= this.i)
                    r.push({
                        ...row,
                        value: this.log ? row.value + 1 : row.value,
                        lastValue: this.log ? row.lastValue + 1 : row.lastValue,
                        color,
                    })
                count += 1
            }
            if (r.length > 0) output.push(r)

            return output
                .map(r =>
                    r.length > 0
                        ? [r[0].code, r[0].color, r, r[r.length - 1]]
                        : [null, null, [], { value: 0 }]
                )
                .sort((a, b) => b.value - a.value)
        },
        extremums() {
            let maxX = 0,
                minX = 100000000,
                maxY = 0,
                minY = 100000000
            for (let r of this.data) {
                maxX = Math.max(maxX, r[this.measureX] ? r[this.measureX] : 0)
                minX = Math.min(minX, r[this.measureX] ? r[this.measureX] : 0)
                maxY = Math.max(maxY, r[this.measureY] ? r[this.measureY] : 0)
                minY = Math.min(minY, r[this.measureY] ? r[this.measureY] : 0)
            }
            return { x: [minX, maxX], y: [minY, maxY] }
        },
    },
    methods: {
        formatDate(d) {
            return this.lang == 'en'
                ? format(new Date(d), 'd MMM')
                : format(new Date(d), 'd MMM', {
                      locale: locales[this.lang],
                  })
        },
        mount() {
            this.width = Math.min(window.innerWidth, 1000)
            this.height = Math.min(this.width, this.height)
            this.xScale = d3
                .scaleLinear()
                .domain([this.extremums.x[0], this.extremums.x[1]]) // input
                .range([0, this.width])
            this.yScale = d3
                .scaleLinear()
                .domain([this.extremums.y[0], this.extremums.y[1]]) // input
                .range([this.height, 0])
            this.xAxis = d3.axisBottom(this.xScale)
            this.yAxis = d3.axisLeft(this.yScale)

            this.line = d3
                .line()
                .x(d => this.xScale(d[this.measureX])) // set the x values for the line generator
                .y(d => this.yScale(d[this.measureY])) // set the y values for the line generator
                .curve(d3.curveBasis)

            this.svg = d3
                .select('#containerBubbleChart')
                .append('svg')
                .attr(
                    'width',
                    this.width + this.margin.left + this.margin.right
                )
                .attr(
                    'height',
                    this.height + this.margin.top + this.margin.bottom
                )
                .append('g')
                .attr(
                    'transform',
                    'translate(' +
                        this.margin.left +
                        ',' +
                        this.margin.top +
                        ')'
                )

            this.svg
                .append('g')
                .attr('class', 'xAxis axis')
                .attr('transform', 'translate(0,' + this.height + ')')
                .call(this.xAxis)

            this.svg
                .append('g')
                .attr('class', 'yAxis axis')
                .call(this.yAxis)

            for (let [country, color, data] of this.dataset) {
                console.log(country, color)
                this.svg
                    .append('path')
                    .datum(data) // 10. Binds data to the line
                    .attr('class', 'line ' + country) // Assign a class for styling
                    .attr('fill', 'none')
                    .attr('stroke', color)
                    .attr('stroke-width', '3')
                    .attr('d', this.line)
            }
            this.div = d3
                .select('#containerLineChart')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0)

            this.iterate()
        },
        iterate() {
            let ctx = this
            let ticker = d3.interval(() => {
                ctx.xScale.domain([ctx.extremums.x[0], ctx.extremums.x[1]])
                ctx.yScale.domain([ctx.extremums.y[0], ctx.extremums.y[1]])
                ctx.line = d3
                    .line()
                    .x(d => this.xScale(d[ctx.measureX])) // set the x values for the line generator
                    .y(d => this.yScale(d[ctx.measureY])) // set the y values for the line generator
                    .curve(d3.curveBasis)

                ctx.svg
                    .select('.xAxis')
                    .transition()
                    .duration(ctx.duration * 2)
                    .ease(easeLinear)
                    .call(ctx.xAxis)

                ctx.svg
                    .select('.yAxis')
                    .transition()
                    .duration(ctx.duration * 2)
                    .ease(easeLinear)
                    .call(ctx.yAxis)

                for (let [country, color, data] of ctx.dataset) {
                    let line = ctx.svg.selectAll('.' + country).datum(data)
                    line.enter()
                        .append('path')
                        .attr('class', 'line ' + country) // Assign a class for styling
                        .attr('fill', 'none')
                        .attr('stroke', color)
                        .attr('stroke-width', '3')
                        .attr('d', ctx.line)
                        .merge(line)
                        .transition()
                        .duration(ctx.duration * 0.9)
                        .attrTween('d', function(d) {
                            var previous = d3.select(this).attr('d')
                            var current = ctx.line(d)
                            return interpolatePath(previous, current)
                        })
                }
                if (ctx.i == ctx.n || ctx.stopped) {
                    ticker.stop()
                } else {
                    ctx.i += 1
                }
            }, this.duration)
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
                return fetch(`/bubble.json?d=${d}`)
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
    },
    mounted() {
        this.getData()
    },
}
</script>

<style>
</style>
<template>
    <v-col>
        <v-row align="center" justify="center" class="mb-3">
            <p class="title" v-html="sentence"></p>
            <v-btn
                v-if="i == n - 1"
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
        <v-row justify="center">
            <p class="title">{{ $t('day') + ' ' + i }}</p>
        </v-row>
        <v-slider
            @end="iterate()"
            @mouseup="iterate()"
            :thumb-size="24"
            thumb-label="always"
            :max="Math.max(n - 1, 0)"
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
            <div id="containerLineChart" :style="!loading ? style : ''"></div>
            <v-spacer></v-spacer>
        </v-row>
    </v-col>
</template>

<script>
import countries from '@/../public/countries.json'
import continents from '@/../public/continents.json'
import * as d3 from 'd3'
import * as d3Scale from 'd3-scale-chromatic'
import * as d3Legend from 'd3-svg-legend'
import { easeLinear } from 'd3-ease'
import { interpolatePath } from 'd3-interpolate-path'

import { format } from 'date-fns'
import { de, fr, es } from 'date-fns/locale'
const locales = { de, fr, es }
export default {
    name: 'lineChart',
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
        log: {
            type: Boolean,
            required: true,
        },
    },
    data: () => ({
        loading: false,
        getting: false,
        stopped: false,
        inv_duration: 400,
        i: 0,
        duration: 800,
        margin: { top: 50, right: 50, bottom: 50, left: 50 },
        width: 100,
        height: 100,
        rawData: {
            data: [],
            range: 0,
        },
        countryMap: countries,
        continentMap: continents,
        xScale: null,
        yScale: null,
        xAxis: null,
        yAxis: null,
        colorScale: null,
        line: null,
        svg: null,
        locales,
        labels: null,
        logger: [],
        ticker: null,
    }),
    computed: {
        n() {
            return this.rawData.range
        },
        sentence() {
            return this.$t('line_sentence')
                .replace(
                    /\[c\]/g,
                    this.$t(this.continent ? 'continent' : 'country')
                )
                .replace(
                    '[x]',
                    `<span style="color:${this.textColor}">${this.$t(
                        this.measure
                    ).toLowerCase()}</span>`
                )
        },
        codes() {
            return new Set(this.data.map(d => d.code))
        },
        arrayCodes() {
            return Array.from(this.codes).sort((a, b) => a - b)
        },
        countryColor() {
            return this.arrayCodes
                .map((code, i) => {
                    return { code, color: d3Scale.schemeCategory10[i % 10] }
                })
                .reduce((p, c) => {
                    p[c.code] = c.color
                    return p
                }, {})
        },
        orderedCountries() {
            return this.dataset
                .map(d => ({
                    name: this.countryNames[d[0]],
                    value: d[3].value,
                }))
                .sort((a, b) => b.value - a.value)
                .filter((v, i) => i < this.top)
                .map(c => c.name)
        },
        orderedColors() {
            return this.dataset
                .map(d => ({ color: d[1], value: d[3].value }))
                .sort((a, b) => b.value - a.value)
                .filter((v, i) => i < this.top)
                .map(c => c.color)
        },
        colorArray() {
            return this.arrayCodes.map(c => {
                return this.countryColor[c]
            })
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
        data() {
            return this.rawData && this.rawData.data ? this.rawData.data : []
        },
        dataset() {
            let output = []
            let r = []
            let country = undefined
            let color = undefined
            let max = 0
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
                    max = 0
                }
                if (max <= this.i) {
                    if (max < this.i || this.stopped || this.i == this.n - 1) {
                        r.push({
                            ...row,
                            value: this.log ? row.value + 1 : row.value,
                            lastValue: this.log ? row.value + 1 : row.value,
                            color,
                        })
                    } else if (max == this.i) {
                        r.push({
                            ...row,
                            value: this.log ? row.value + 1 : row.value,
                            lastValue: this.log
                                ? row.lastValue + 1
                                : row.lastValue,
                            color,
                        })
                    }
                }
                max += 1
            }
            if (r.length > 0) output.push(r)

            return output
                .map(r =>
                    r.length > 0
                        ? [r[0].code, r[0].color, r, r[r.length - 1]]
                        : [null, null, [], { value: 0 }]
                )
                .sort((a, b) => b.value - a.value)
            // .filter((a, i) => i < this.top)
        },
        max() {
            let max = 0
            for (let d of this.dataset) {
                for (let r of d[2]) {
                    max = Math.max(max, r.value)
                }
            }
            return max
        },
        min() {
            let min = 1000
            for (let d of this.dataset) {
                for (let r of d[2]) {
                    min = Math.min(min, r.value)
                }
            }
            return min + (this.log ? 0.0001 : 0)
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
        getData() {
            if (!this.getting) {
                this.getting = true
                this.loading = true

                const d = format(new Date(), 'd-M-Y')
                d3.selectAll('svg').remove()
                return fetch(
                    `/line${this.continent ? '-continent' : ''}/${
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
            this.width = Math.min(window.innerWidth - 110, 1000)
            this.height = Math.min(this.width, this.height)
            this.xScale = d3
                .scaleLinear()
                .domain([0, this.i]) // input
                .range([0, this.width])
            this.yScale = this.log
                ? d3
                      .scaleLog()
                      .domain([this.min, this.max + 1]) // input
                      .range([this.height, 0])
                : d3
                      .scaleLinear()
                      .domain([this.min, this.max]) // input
                      .range([this.height, 0])
            this.xAxis = d3.axisBottom(this.xScale)
            this.yAxis = d3.axisLeft(this.yScale)
            this.line = d3
                .line()
                .x((d, i) => this.xScale(i)) // set the x values for the line generator
                .y(d => this.yScale(d.value)) // set the y values for the line generator
                .curve(d3.curveBasis)
            this.colorScale = d3.scaleOrdinal(this.orderedColors)
            this.svg = d3
                .select('#containerLineChart')
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

            for (let [country, color, data, lastValue] of this.dataset) {
                this.svg
                    .append('path')
                    .datum(data) // 10. Binds data to the line
                    .attr('class', 'line ' + country) // Assign a class for styling
                    .attr('fill', 'none')
                    .attr('stroke', color)
                    .attr('stroke-width', '3')
                    .attr('d', this.line)

                this.svg
                    .append('circle')
                    .datum(lastValue)
                    .attr('class', 'circle circle' + country)
                    .attr(
                        'cy',
                        this.yScale(lastValue.value ? lastValue.value : 0)
                    )
                    .attr('cx', this.xScale(data.length - 1))
                    .attr('fill', color)
                    .style('stroke', color)
                    .attr('r', '8')
                    .style('stroke-opacity', 0)
                    .style('fill-opacity', 0)
            }
            this.div = d3
                .select('#containerLineChart')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0)
            let ctx = this

            ctx.svg
                .selectAll('circle')
                .on('mouseover', d => {
                    const s = ctx.makeHtml(d.code)
                    ctx.div
                        .transition()
                        .duration(100)
                        .style('opacity', 1)
                    ctx.div
                        .html(s)
                        .style('left', d3.event.pageX + 30 + 'px')
                        .style('top', d3.event.pageY - 100 + 'px')
                })
                .on('mouseout', () => {
                    ctx.div
                        .transition()
                        .duration(500)
                        .style('opacity', 0)
                })

            ctx.svg
                .selectAll('path')
                .on('mouseover', d => {
                    const s = ctx.makeHtml(d[0].code)
                    ctx.div
                        .transition()
                        .duration(100)
                        .style('opacity', 1)
                    ctx.div
                        .html(s)
                        .style('left', d3.event.pageX + 30 + 'px')
                        .style('top', d3.event.pageY - 100 + 'px')
                })
                .on('mouseout', () => {
                    ctx.div
                        .transition()
                        .duration(500)
                        .style('opacity', 0)
                })
            this.svg
                .append('g')
                .attr('class', 'legendOrdinal')
                .attr('transform', 'translate(' + this.margin.left + ',20)')
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
                .scale(this.colorScale.domain(this.orderedCountries))
            this.labels = this.svg
                .selectAll('text.countryLabel')
                .data(this.dataset, d => d[0])
                .enter()
                .append('text')
                .attr('class', 'countryLabel')
                .attr('x', d => this.xScale(d[3].value) - 8)
                .attr(
                    'y',
                    d =>
                        this.yScale(d[3].value) +
                        5 +
                        (this.yScale(1) - this.yScale(0)) / 2 +
                        1
                )
                .style('text-anchor', 'end')
                .html(d => this.countryNames[d[0]])

            this.svg
                .selectAll('text.valueLabel')
                .data(this.dataset, d => d[0])
                .enter()
                .append('text')
                .attr('class', 'valueLabel')
                .attr('x', d => this.xScale(d[3].value) + 5)
                .attr(
                    'y',
                    d =>
                        this.yScale(d[3].value) +
                        5 +
                        (this.yScale(1) - this.yScale(0)) / 2 +
                        1
                )
                .text(d => d3.format(',.0f')(d[3].lastValue))

            this.svg.select('.legendOrdinal').call(legendOrdinal)
            if (!this.stopped) {
                this.iterate()
            }
        },
        makeHtml(code) {
            const d = this.dataset.find(d => d[0] == code)
            if (d) {
                const [code, color, data, lastValue] = d
                const start = data[0]
                return `<div>
                <div><div style="height:10px;width:10px;border-radius:50%;background:${color}"></div><b>${
                    this.countryNames[code]
                }</b></div><br><span>${this.$t(
                    'started'
                )}</span> : <b>${this.formatDate(
                    start.date
                )}</b><br><span>${this.$t(this.measure)} ${this.$t(
                    'on'
                )} ${this.formatDate(lastValue.date)}</span> : <b>${Math.round(
                    lastValue.value
                )} </b></div>`
            }
            return ''
        },
        iterate() {
            let ctx = this
            if (!this.ticker) {
                this.ticker = d3.interval(() => {
                    ctx.xScale.domain([0, ctx.i])
                    ctx.yScale.domain([ctx.min, ctx.max])
                    ctx.line = d3
                        .line()
                        .x((d, i) => this.xScale(i)) // set the x values for the line generator
                        .y(d => this.yScale(d.value)) // set the y values for the line generator
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

                    for (let [country, color, data, lastValue] of ctx.dataset) {
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

                        let circle = ctx.svg.selectAll('.circle' + country)
                        circle
                            .transition()
                            .duration(ctx.duration * 0.9)
                            .attr('fill', color)
                            .attr('cx', ctx.xScale(data.length - 1))
                            .attr('cy', ctx.yScale(lastValue.value))
                            .style('fill-opacity', 0.7)
                            .style('stroke-opacity', 1)
                    }

                    ctx.countryLabels() // animate country labels
                    ctx.countryValues() // animate values for countries
                    ctx.legendValues()
                    if (ctx.i == ctx.n || ctx.stopped) {
                        ctx.ticker.stop()
                        ctx.ticker = null
                    } else {
                        ctx.i += 1
                    }
                }, this.duration)
            }
        },
        legendValues() {
            this.colorScale = d3.scaleOrdinal(this.orderedColors)
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
                .scale(this.colorScale.domain(this.orderedCountries))
            this.svg
                .select('.legendOrdinal')
                // .transition()
                // .duration(this.duration)
                .call(legendOrdinal)
        },
        countryValues() {
            let valueLabels = this.svg
                .selectAll('.valueLabel')
                .data(this.dataset, d => d[0])

            valueLabels
                .enter()
                .append('text')
                .attr('class', 'valueLabel')
                .attr('x', d => this.xScale(d[3].i) + 5)
                .attr('y', () => this.yScale(this.min - 1) + 5)
                .text(d => d3.format(',.0f')(d[3].lastValue))
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr(
                    'y',
                    d =>
                        this.yScale(d[3].value) +
                        10 +
                        (this.yScale(1) - this.yScale(0)) / 2 +
                        1
                )

            valueLabels
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => {
                    // this.logger.push(this.xScale(d[3].i))
                    return this.xScale(d[3].i) + 5
                })
                .attr('y', d => {
                    let v = this.yScale(d[3].value)
                    return v - 10
                })
                // .attr('y', this.yScale(1))
                // .html(d => d[3].value)
                .tween('text', function(d) {
                    let val = d[3]
                    let i = d3.interpolateRound(val.lastValue, val.value)
                    return function(t) {
                        this.textContent = d3.format(',')(i(t))
                    }
                })

            valueLabels
                .exit()
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => this.xScale(d[3].i) + 5)
                .attr('y', () => this.yScale(this.min - 1) - 10)
                .remove()
        },
        countryLabels() {
            let labels = this.svg
                .selectAll('.countryLabel')
                .data(this.dataset, d => d[0])
            labels
                .enter()
                .append('text')
                .attr('class', 'countryLabel')
                .attr('x', d => this.xScale(d[3].i) - 8)
                .attr('y', () => this.yScale(0))
                .style('text-anchor', 'end')
                .html(d => this.countryNames[d[0]])
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('y', d => this.yScale(d[3].value) - 10)

            labels
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => this.xScale(d[3].i) - 8)
                .attr('y', d => this.yScale(d[3].value) - 10)

            labels
                .exit()
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => this.xScale(d[3].i) - 8)
                .attr('y', () => this.yScale(this.min + 1) - 10)
                .remove()
        },
        pathTween(d1, precision) {
            // An interpolator factory: a function that returns a function.
            // d1: The target path (a string containing a series of path descriptions).
            // precision: The precision to sample the source and target paths.
            // console.log(d1)
            return function() {
                var path0 = this,
                    path1 = path0.cloneNode(),
                    n0 = path0.getTotalLength(),
                    n1 = (path1.setAttribute('d', d1), path1).getTotalLength()

                // Uniformly sample either the source or target path, whichever is longer.
                var distances = [0],
                    i = 0,
                    dt = precision / Math.max(n0, n1)

                while ((i += dt) < 1) {
                    distances.push(i)
                }

                distances.push(1)

                // Get an interpolator for each pair of points.
                var points = distances.map(function(distance) {
                    var p0 = path0.getPointAtLength(distance * n0),
                        p1 = path1.getPointAtLength(distance * n1)
                    // console.log(p0, p1)
                    return d3.interpolate([p0.x, p0.y], [p1.x, p1.y])
                })
                // console.log(points)

                // Here, `p` is the current interpolator.
                // We join the interpolated points using the `Lineto` path command.
                return function(t) {
                    return t < 1
                        ? 'M' +
                              points
                                  .map(function(p) {
                                      return p(t)
                                  })
                                  .join('L')
                        : d1
                }
            }
        },
    },
    mounted() {
        this.width = window.innerWidth - this.margin.left - this.margin.right
        this.height =
            window.innerHeight * 0.7 - this.margin.top - this.margin.bottom
        this.getData()
    },
    watch: {
        remove() {
            d3.selectAll('svg').remove()
        },
        inv_duration(v) {
            this.duration = 1000 - v
        },
        stopped(val) {
            if (!val) {
                this.iterate()
            }
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
        continent() {
            this.getData()
        },
        log(val) {
            this.getData()
            if (val) {
                this.yScale = d3
                    .scaleLog()
                    .domain([this.min, this.max + 1]) // input
                    .range([this.height, 0])
            } else {
                this.yScale = d3
                    .scaleLinear()
                    .domain([this.min, this.max]) // input
                    .range([this.height, 0])
            }
        },
    },
}
</script>

<style></style>

<template>
    <v-col>
        <v-row align="center" justify="center">
            <v-subheader class="title">
                <p class="title mr-2" v-html="sentence"></p>
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
            </v-subheader>
        </v-row>
        <v-slider
            @end="iterate()"
            @mouseup="iterate()"
            :max="Math.max(0, n - 1)"
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
            <div id="containerBubbleChart" :style="!loading ? style : ''"></div>
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
import { interpolatePath } from 'd3-interpolate-path'
const locales = { de, fr, es }
Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf())
    date.setDate(date.getDate() + days)
    return date
}
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
        height: 600,
        width: 960,
        duration: 800,
        i: 0,
        margin: {
            top: 35,
            right: 50,
            bottom: 35,
            left: 50,
        },
        rawData: { data: [], range: 0 },
        locales,
        countryMap: countries,
        continentMap: continents,
        svg: null,
        xScale: null,
        yScale: null,
        xAxis: null,
        yAxis: null,
        line: null,
        labels: null,
        div: null,
        ticker: null,
        d: null,
    }),
    computed: {
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
        sentence() {
            return (
                `<span style="color:${this.getTextColor(
                    this.measureX
                )}">${this.$t(this.measureX)}</span>` +
                ' VS ' +
                `<span style="color:${this.getTextColor(
                    this.measureY
                )}">${this.$t(this.measureY)}</span> ${this.nice_date}`
            )
        },
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
        minDate() {
            let minDate = '2099-01-01'
            if (this.rawData && this.rawData.data) {
                for (let r of this.rawData.data) {
                    minDate = r.date < minDate ? r.date : minDate
                }
            }
            return minDate
        },
        maxDate() {
            let maxDate = '2000-01-01'
            if (this.rawData && this.rawData.data) {
                for (let r of this.rawData.data) {
                    maxDate = r.date > maxDate ? r.date : maxDate
                }
            }
            return maxDate
        },
        date() {
            return new Date(this.minDate).addDays(this.i)
        },
        data() {
            let output = []
            let notIn = new Set(this.codes)
            if (this.rawData && this.rawData.data) {
                for (let r of this.rawData.data) {
                    if (new Date(r.date) <= this.date) {
                        for (let m of this.measures.map(m => m.value)) {
                            r[m] = r[m] ? r[m] : 0
                        }
                        notIn.delete(r.code)
                        output.push(r)
                    }
                }
            }
            for (let code of notIn) {
                let r = { code, date: this.minDate }
                for (let m of this.measures.map(m => m.value)) {
                    r[m] = r[m] ? r[m] : 0
                }
                output.push(r)
            }
            return output
        },
        dataset() {
            let output = []
            let r = []
            let country = undefined
            let color = undefined
            for (let row of this.data) {
                if (row.code != country) {
                    if (country != undefined) {
                        if (r.length == 0) {
                            r = [
                                {
                                    code: country,
                                    date: this.minDate,
                                    color: this.has_color[country]
                                        ? this.has_color[country]
                                        : this.countryColor[country],
                                },
                            ]
                        }
                        output.push(r)
                    }
                    color = this.has_color[row.code]
                        ? this.has_color[row.code]
                        : this.countryColor[row.code]
                    country = row.code
                    r = []
                }
                r.push({
                    ...row,
                    value: this.log ? row.value + 1 : row.value,
                    lastValue: this.log ? row.lastValue + 1 : row.lastValue,
                    color,
                })
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
            this.width = Math.min(window.innerWidth - 110, 1000)
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
                .curve(d3.curveLinear)

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
                .append('text')
                .attr(
                    'transform',
                    'translate(' +
                        String(this.width - this.margin.right / 2) +
                        ' ,' +
                        String(this.height - this.margin.top / 2) +
                        ')'
                )
                .style('font-size', 'medium')
                .style('font-weight', 'bold')
                .style('text-anchor', 'end')
                .style('color', this.getTextColor(this.measureX))
                .text(this.$t(this.measureX))

            this.svg
                .append('g')
                .attr('class', 'yAxis axis')
                .call(this.yAxis)

            this.svg
                .append('text')
                // .attr('transform', 'rotate(-90)')
                .attr('y', 0)
                .attr('x', 20)
                .attr('dy', '1em')
                .style('font-size', 'medium')
                .style('font-weight', 'bold')
                .style('text-anchor', 'start')
                .style('color', this.getTextColor(this.measureY))
                .text(this.$t(this.measureY))

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
                        this.yScale(
                            lastValue[this.measureY]
                                ? lastValue[this.measureY]
                                : 0
                        )
                    )
                    .attr(
                        'cx',
                        this.xScale(
                            lastValue[this.measureX]
                                ? lastValue[this.measureX]
                                : 0
                        )
                    )
                    .attr('fill', color)
                    .style('stroke', color)
                    .attr('r', '20')
                    .style('stroke-opacity', 0)
                    .style('fill-opacity', 0)
            }
            this.labels = this.svg
                .selectAll('text.countryLabel')
                .data(this.dataset, d => d[0])
                .enter()
                .append('text')
                .attr('class', 'countryLabel')
                .attr('x', d => this.xScale(d[3][this.measureX]) - 8)
                .attr(
                    'y',
                    d =>
                        this.yScale(d[3][this.measureY]) +
                        5 +
                        (this.yScale(1) - this.yScale(0)) / 2 +
                        1
                )
                .attr('opacity', 0)
                .style('text-anchor', 'end')
                .html(d => this.countryNames[d[0]])

            this.div = d3
                .select('#containerBubbleChart')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0)
            let ctx = this
            ctx.svg
                .selectAll('circle')
                .on('mouseover', d => {
                    // s += arr.reverse().join('')
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
            this.$nextTick(() => {
                this.iterate()
            }, this)
        },
        makeHtml(code) {
            const l = this.dataset.find(d => d[0] == code)
            if (l) {
                const d = l[3]
                this.d = d
                return `<div>
                        <div><div style="height:10px;width:10px;border-radius:50%;background:${
                            d.color
                        }"></div><b>${
                    this.countryNames[d.code]
                }</b></div><br><span>${this.$t(this.measureX)} ${this.$t(
                    'on'
                )} ${this.formatDate(d.date)}</span> : <b>${Math.round(
                    d[this.measureX]
                )} </b><br><span>${this.$t(this.measureY)} ${this.$t(
                    'on'
                )} ${this.formatDate(d.date)}</span> : <b>${Math.round(
                    d[this.measureY]
                )}</b></div>`
            }
        },
        iterate() {
            let ctx = this
            if (!this.ticker) {
                this.ticker = d3.interval(() => {
                    ctx.xScale.domain([ctx.extremums.x[0], ctx.extremums.x[1]])
                    ctx.yScale.domain([ctx.extremums.y[0], ctx.extremums.y[1]])
                    ctx.line = d3
                        .line()
                        .x(d => ctx.xScale(d[ctx.measureX])) // set the x values for the line generator
                        .y(d => ctx.yScale(d[ctx.measureY])) // set the y values for the line generator
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
                        let y = lastValue[ctx.measureY]
                            ? lastValue[ctx.measureY]
                            : 0
                        let x = lastValue[ctx.measureX]
                            ? lastValue[ctx.measureX]
                            : 0
                        let circle = ctx.svg.selectAll('.circle' + country)
                        circle
                            .transition()
                            .duration(ctx.duration * 0.9)
                            .attr('fill', color)
                            .attr('cx', ctx.xScale(x))
                            .attr('cy', ctx.yScale(y))
                            .style('fill-opacity', x + y == 0 ? 0 : 0.7)
                            .style('stroke-opacity', x + y == 0 ? 0 : 1)
                    }
                    if (ctx.d) {
                        ctx.div.html(ctx.makeHtml(ctx.d.code))
                    }
                    ctx.countryLabels()
                    if (ctx.i == ctx.n - 1 || ctx.stopped) {
                        ctx.ticker.stop()
                        ctx.ticker = null
                    } else {
                        ctx.i += 1
                    }
                }, this.duration)
            }
        },
        countryLabels() {
            let labels = this.svg
                .selectAll('.countryLabel')
                .data(this.dataset, d => d[0])
            labels
                .enter()
                .append('text')
                .attr('class', 'countryLabel')
                .attr('x', d => this.xScale(d[3][this.measureX]) - 8)
                .attr('y', () => this.yScale(0))
                .style('text-anchor', 'end')
                .html(d => this.countryNames[d[0]])
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('y', d => this.yScale(d[3][this.measureY]) + 5)

            labels
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => this.xScale(d[3][this.measureX]) - 8)
                .attr('y', d => this.yScale(d[3][this.measureY]) + 5)
                .attr('opacity', d => (d[3][this.measureX] ? 1 : 0))
            // .style('text-anchor', 'end')
            // .html(d => this.countryNames[d[0]])

            labels
                .exit()
                .transition()
                .duration(this.duration)
                .ease(easeLinear)
                .attr('x', d => this.xScale(d[3][this.measureX]) - 8)
                .attr('y', () => this.yScale(0) + 5)
                .remove()
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
                    `/bubble${this.continent ? '-continent' : ''}.json?d=${d}`
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
        measureX() {
            this.getData()
        },
        measureY() {
            this.getData()
        },
        lang() {
            this.getData()
        },
        continent() {
            this.getData()
        },
        top() {
            this.getData()
        },
        log() {
            this.getData()
        },
    },
}
</script>

<style></style>

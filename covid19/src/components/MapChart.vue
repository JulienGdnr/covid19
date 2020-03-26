<template>
    <v-col>
        <v-row align="center" justify="center" class="mb-3">
            <div class="title" v-html="sentence"></div>
            <v-btn
                v-if="i == dates.length - 1"
                rounded
                class="ml-4"
                outlined
                @click=";(i = 0), iterate()"
            >
                <v-icon>refresh</v-icon>
                {{ $t('refresh') }}
            </v-btn>
        </v-row>
        <v-row align="center" justify="center">
            <v-subheader class="title">{{ formatDate(date) }}</v-subheader>
        </v-row>
        <v-row align="center" justify="center">
            <v-spacer></v-spacer>
            <v-progress-circular
                indeterminate
                size="50"
                color="primary"
                v-if="loading"
            ></v-progress-circular>
            <div
                id="containerMapChart"
                :style="
                    !loading ? `background:#e9e9e9;border-radius:10px;` : ''
                "
            ></div>

            <v-spacer></v-spacer>
        </v-row>
    </v-col>
</template>

<script>
import * as d3 from 'd3'
import * as d3Geo from 'd3-geo-projection'
import * as d3Drag from 'd3-drag'
import { format } from 'date-fns'
import { de, fr, es } from 'date-fns/locale'
import countries from '@/../public/countries.json'
import latlng from '@/../public/latlng.json'
const locales = { de, fr, es }
import { easeLinear } from 'd3-ease'

export default {
    name: 'mapChart',
    props: {
        measure: {
            type: String,
            required: true,
        },
        proj: {
            type: String,
            required: true,
        },
        lang: {
            type: String,
            required: true,
        },
    },
    data: () => ({
        loading: false,
        i: 0,
        getting: false,
        stopped: false,
        width: 1000,
        height: 600,
        rotate: [0, 0, 0],
        graticule: null,
        duration: 300,
        drag: null,
        svg: null,
        m0: null,
        o0: null,
        rawData: {
            data: [],
            dates: [],
        },
        projections: {
            geoMiller: d3Geo.geoMiller(),
            geoAitoff: d3Geo.geoAitoff(),
            geoLagrange: d3Geo.geoLagrange(),
            geoOrthographic: d3.geoOrthographic(),
            geoBromley: d3Geo.geoBromley(),
            geoGilbert: d3Geo.geoGilbert(),
        },
        mapData: null,
        zoom: null,
        locales,
        latlng,
        countryMap: countries,
    }),
    methods: {
        zoomed() {
            this.projection.scale(
                d3.event.transform.translate(this.projection).k *
                    this.windowScale
            )
            this.map.selectAll('path').attr('d', this.path)
        },
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
            this.svg = d3
                .select('#containerMapChart')
                .append('svg')
                .attr('width', this.width)
                .attr('height', this.height)
            this.projection = this.projections[this.proj]
                .scale(this.windowScale)
                .translate([this.width / 2, this.height / 2])
                .rotate(this.rotate)
            let ctx = this
            this.getMapData().then(data => {
                this.path = d3.geoPath().projection(this.projection)

                this.drag = d3Drag
                    .drag()
                    .on('start', function() {
                        var proj = ctx.projection.rotate()
                        ctx.m0 = [
                            d3.event.sourceEvent.pageX,
                            d3.event.sourceEvent.pageY,
                        ]
                        ctx.o0 = [-proj[0], -proj[1]]
                    })
                    .on('drag', function() {
                        if (ctx.m0) {
                            var m1 = [
                                    d3.event.sourceEvent.pageX,
                                    d3.event.sourceEvent.pageY,
                                ],
                                o1 = [
                                    ctx.o0[0] + (ctx.m0[0] - m1[0]) / 4,
                                    ctx.o0[1] + (m1[1] - ctx.m0[1]) / 4,
                                ]
                            ctx.projection.rotate([-o1[0], -o1[1]])
                        }
                        ctx.path = d3.geoPath().projection(ctx.projection)
                        d3.selectAll('path').attr('d', ctx.path)
                        ctx.svg
                            .selectAll('circle')
                            .attr('cx', d => ctx.projection([d.lng, d.lat])[0])
                            .attr('cy', d => ctx.projection([d.lng, d.lat])[1])
                            .attr('fill', d => {
                                const coordinate = [
                                    Number(d.lng),
                                    Number(d.lat),
                                ]
                                const t = d3.geoDistance(
                                    coordinate,
                                    ctx.projection.invert(ctx.center)
                                )
                                return t > 1.57 &&
                                    this.proj == 'geoOrthographic'
                                    ? 'none'
                                    : ctx.textColor
                            })
                    })

                this.svg
                    .append('path')
                    .datum(d3.geoGraticule())
                    .attr('class', 'graticule')
                    .attr('d', this.path)

                this.svg // draw countries and frontiers
                    .append('g')
                    .selectAll('path')
                    .data(data.features)
                    .enter()
                    .append('path')
                    .attr('fill', '#69b3a2')
                    .attr('d', this.path)
                    .style('stroke', '#fff')
                    .call(this.drag)

                this.svg
                    .selectAll('circle')
                    .data(this.dataset)
                    .enter()
                    .append('circle')
                    .attr('cx', d => this.projection([d.lng, d.lat])[0])
                    .attr('cy', d => this.projection([d.lng, d.lat])[1])
                    .attr('r', '1px')
                    .attr('fill-opacity', '50%')
                    .attr('fill', this.textColor)
                    .call(this.drag)

                // this.zoom = d3
                //     .zoom()
                //     .scaleExtent([0.75, 50]) //bound zoom
                //     .on('zoom', this.zoomed)

                // this.svg.call(this.zoom)

                this.div = d3
                    .select('#containerMapChart')
                    .append('div')
                    .attr('class', 'tooltip')
                    .style('opacity', 0)

                ctx.svg
                    .selectAll('circle')
                    .on('mouseover', d => {
                        let s = `<div>
                        <div style="text-align:left"><b>${
                            ctx.countryNames[d.code]
                        }</b></div>
                        <br>
                        <div>${ctx.$t(ctx.measure)} : ${d.value}</div>
                        </div>`
                        ctx.div
                            .transition()
                            .duration(200)
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

                this.iterate()
            })
        },
        size(d) {
            return Math.round((100 * d.value) / this.bigMax) + 4
        },
        getMapData() {
            if (!this.mapData) {
                return fetch('/map.json')
                    .then(res => res.json())
                    .then(d => {
                        this.mapData = d
                        return d
                    })
            } else {
                return new Promise(resolve => resolve(this.mapData))
            }
        },
        iterate() {
            let ctx = this
            let ticker = d3.interval(() => {
                d3.selectAll('circle')
                    .data(ctx.dataset)
                    .attr('cx', d => ctx.projection([d.lng, d.lat])[0])
                    .attr('cy', d => ctx.projection([d.lng, d.lat])[1])

                d3.selectAll('circle')
                    .transition()
                    .duration(ctx.duration)
                    .ease(easeLinear)
                    .attr(
                        'r',
                        d => Math.round((d.value / ctx.bigMax) * 100) + 'px'
                    )
                    .attr('fill', d => {
                        const coordinate = [Number(d.lng), Number(d.lat)]
                        const t = d3.geoDistance(
                            coordinate,
                            ctx.projection.invert(ctx.center)
                        )
                        return t > 1.57 ? 'none' : this.textColor
                    })

                if (ctx.date == ctx.dates[ctx.dates.length - 1]) {
                    ticker.stop()
                } else {
                    ctx.i += 1
                }
            }, ctx.duration)
        },
        getData() {
            if (!this.getting) {
                if (!this.stopped) {
                    this.i = 0
                }
                this.getting = true
                this.loading = true
                this.rawData = { data: [], dates: [] }
                const d = format(new Date(), 'd-M-Y')
                d3.selectAll('svg').remove()
                return fetch(`/race/${this.measure}.json?d=${d}`)
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
    computed: {
        center() {
            return [this.width / 2, this.height / 2]
        },
        windowScale() {
            return this.width / 1.3 / Math.PI
        },
        sentence() {
            return this.$t('map').replace(
                '[x]',
                `<span style="color:${this.textColor}">${this.$t(
                    this.measure
                ).toLowerCase()}</span>`
            )
        },
        countryNames() {
            return Array.from(this.codes).reduce((p, c) => {
                p[c] = this.countryMap[c]['country_' + this.lang]
                return p
            }, {})
        },
        codes() {
            return new Set(this.data.map(d => d.code))
        },
        bigMax() {
            let bigMax = 0
            for (let row of this.data) {
                bigMax = Math.max(row.value, bigMax)
            }
            return bigMax
        },
        min() {
            return this.dataset.length > 0
                ? this.dataset[this.dataset.length - 1].value
                : null
        },
        max() {
            return this.dataset.length > 0 ? this.dataset[0].value : null
        },
        data() {
            return this.rawData && this.rawData.data ? this.rawData.data : []
        },
        dates() {
            return this.rawData && this.rawData.dates ? this.rawData.dates : []
        },
        date() {
            return this.i < this.dates.length ? this.dates[this.i] : null
        },
        dataset() {
            let output = []
            for (let row of this.data) {
                if (row['date'] == this.date) {
                    output.push({ ...row, ...latlng[row['code']] })
                }
            }
            return output.sort((a, b) => b.value - a.value)
        },
    },
    watch: {
        proj: {
            handler: function(val) {
                this.rotate =
                    val == 'geoOrthographic' ? [-30, -30, 0] : [0, 0, 0]
                this.getData()
            },
            immediate: true,
        },
        measure() {
            this.getData()
        },
    },
}
</script>

<style>
.stroke {
    fill: none;
    stroke: #000;
    stroke-width: 3px;
}
.fill {
    fill: #fff;
}
.graticule {
    fill: none;
    stroke: #777;
    stroke-width: 0.5px;
    stroke-opacity: 0.5;
}
.land {
    fill: #222;
}
circle:hover {
    border: solid 1px black;
}
</style>

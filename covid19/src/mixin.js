export default {
    data: () => ({
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
            Europe: '#003399',
            Asia: '#FFCC01',
            America: '#00963F',
            Africa: 'orange',
            Oceania: 'red',
            others: 'grey',
        },
        style:
            'background:#ECEFF1;border-radius:10px;margin-left:5px;margin-right:5px;',
    }),
    methods: {
        getTextColor(c) {
            return {
                confirmed_deaths_recovered: 'orange',
                confirmed: 'blue',
                deaths: 'red',
                recovered: 'green',
                deaths_area: 'red',
                deaths_pop: 'red',
                confirmed_area: 'blue',
                confirmed_pop: 'blue',
                recovered_pop: 'green',
                recovered_area: 'green',
                confirmed_deaths_recovered_area: 'orange',
                confirmed_deaths_recovered_pop: 'orange',
            }[c]
        },
    },
    computed: {
        breakpoint() {
            return this.$vuetify.breakpoint.name
        },
        textColor() {
            return this.getTextColor(this.measure)
        },
    },
}

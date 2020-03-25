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
            others: 'grey',
        },
    }),
    computed: {
        textColor() {
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
            }[this.measure]
        },
    },
}

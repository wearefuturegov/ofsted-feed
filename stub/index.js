const csv = require("csvtojson")
const faker = require("faker")
const fetch = require("node-fetch")

const fetchAndProcess = async () => {
    try{
        const res = await fetch(process.env.STUB_DATASOURCE)
        const text = await res.text()
        let rows = await csv().fromString(text)
        rows = rows.slice(0, 100).map(row => {
            return {
                ...row,
                childcare_period: row.childcare_period.split("\n")
            }
        })
        return rows
    } catch(e) {
        console.log(e)
    }
}

module.exports = fetchAndProcess
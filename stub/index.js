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
                childcare_period: row.childcare_period.split("\n"),
                childcare_age: row.childcare_age.split("\n").map(element => convert(element))
            }
        })
        return rows
    } catch(e) {
        console.log(e)
    }
}

const convert = source => {
  let result = {}
  let sourceArray = source.split(",")
  sourceArray.forEach(element => {
      let [key, value] = element.trim().split(": ")
      result[key] = value
  })
  return result
}

module.exports = fetchAndProcess
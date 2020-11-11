const csv = require("csvtojson")
const faker = require("faker")
const fetch = require("node-fetch")

const fetchAndProcess = async () => {
    try{
        const res = await fetch(process.env.STUB_DATASOURCE)
        const text = await res.text()
        let rows = await csv().fromString(text)
        rows = rows.slice(0, rows.length).map(row => {
            return {
                ...row,
                registration_status_history: row.registration_status_history.split("\n").map(element => convert(element)),
                childcare_period: row.childcare_period.split("\n"),
                childcare_age: row.childcare_age.split("\n").map(element => convert(element)),
                child_services_register: row.child_services_register.split("\n").map(element => convert(element)),
                inspection: row.inspection.split("\n").map(element => convert(element)),
                notice_history: row.notice_history.split("\n").map(element => convert(element)),
                welfare_notice_history: row.welfare_notice_history.split("\n").map(element => convert(element))
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
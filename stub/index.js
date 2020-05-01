const faker = require("json-schema-faker")
const schema = require("./schema.json")

const res = faker.generate(schema)

module.exports = res
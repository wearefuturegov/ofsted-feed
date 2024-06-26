const express = require("express");
const fs = require("fs");
const swaggerUi = require("swagger-ui-express");
const swaggerJsdoc = require("swagger-jsdoc");
const jsf = require("json-schema-faker");
// const faker = require("@faker-js/faker");
// jsf.extend("faker", () => faker);
const app = express();
const port = process.env.PORT || 3000;

// Load JSON Schema
const schema = JSON.parse(fs.readFileSync("schema.json", "utf8"));

// Swagger set up
const swaggerOptions = {
  swaggerDefinition: {
    openapi: "3.0.0",
    info: {
      title: "Express API with Swagger",
      version: "1.0.0",
      description: "A simple Express API",
    },
    components: {
      schemas: {
        // Include your schema here under a named key
        MySchema: schema,
      },
    },
  },
  apis: ["./app.js"], // files containing annotations as above
};

const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocs));

/**
 * @openapi
 * /:
 *   get:
 *     description: Returns the content of data.json
 *     responses:
 *       200:
 *         description: Success
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/MySchema'
 */
app.get("/json", async (req, res) => {
  // Generate dummy data based on the schema
  try {
    const sampleData = await jsf.resolve(schema);
    res.setHeader("Content-Type", "application/json");
    res.send(sampleData);
  } catch (err) {
    res.status(500).send("Error generating dummy data");
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

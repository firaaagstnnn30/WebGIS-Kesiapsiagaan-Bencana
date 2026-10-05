const express = require("express");
const cors = require("cors");
const db = require("./database");
require("dotenv").config();

const app = express();

app.use(cors());
app.use(express.json());


// =====================================
// TEST SERVER
// =====================================

app.get("/", (req, res) => {
  res.send("WebGIS Kesiapsiagaan API Aktif 🚀");
});


// =====================================
// TEST DATABASE
// =====================================

app.get("/api/test-db", async (req, res) => {
  try {

    const result = await db.query(`
      SELECT
        current_database() AS database,
        current_user AS user,
        version() AS version
    `);

    res.json({
      status: "success",
      message: "PostgreSQL berhasil terhubung",
      data: result.rows[0]
    });

  } catch (error) {

    console.error(error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }
});


// =====================================
// FUNCTION AMBIL GEOJSON DARI POSTGIS
// =====================================

async function getGeoJSON(tableName) {

  const query = `
    SELECT
      json_build_object(
        'type', 'Feature',

        'geometry',
        ST_AsGeoJSON(
          ST_Transform(geom, 4326)
        )::json,

        'properties',
        to_jsonb(t) - 'geom'

      ) AS feature

    FROM ${tableName} t
  `;

  const result = await db.query(query);

  return {
    type: "FeatureCollection",
    features: result.rows.map(row => row.feature)
  };
}


// =====================================
// RUMAH SAKIT
// =====================================

app.get("/api/rumah-sakit", async (req, res) => {

  try {

    const data = await getGeoJSON("rumah_sakit");

    res.json(data);

  } catch (error) {

    console.error("ERROR RUMAH SAKIT:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// PUSKESMAS
// =====================================

app.get("/api/puskesmas", async (req, res) => {

  try {

    const data = await getGeoJSON("puskesmas");

    res.json(data);

  } catch (error) {

    console.error("ERROR PUSKESMAS:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// DAMKAR
// =====================================

app.get("/api/damkar", async (req, res) => {

  try {

    const data = await getGeoJSON("damkar");

    res.json(data);

  } catch (error) {

    console.error("ERROR DAMKAR:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// KANTOR POLISI
// =====================================

app.get("/api/kantor-polisi", async (req, res) => {

  try {

    const data = await getGeoJSON("kantor_polisi");

    res.json(data);

  } catch (error) {

    console.error("ERROR KANTOR POLISI:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// JALAN
// =====================================

app.get("/api/jalan", async (req, res) => {

  try {

    const data = await getGeoJSON("jalan");

    res.json(data);

  } catch (error) {

    console.error("ERROR JALAN:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// ADMINISTRASI
// =====================================

app.get("/api/administrasi", async (req, res) => {

  try {

    const data = await getGeoJSON("administrasi");

    res.json(data);

  } catch (error) {

    console.error("ERROR ADMINISTRASI:", error);

    res.status(500).json({
      status: "error",
      message: error.message
    });

  }

});


// =====================================
// JALANKAN SERVER
// =====================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {

  console.log("");
  console.log("======================================");
  console.log("🚀 WEBGIS API AKTIF");
  console.log("======================================");
  console.log(`Server : http://localhost:${PORT}`);
  console.log("");
  console.log("Endpoint:");
  console.log("/api/rumah-sakit");
  console.log("/api/puskesmas");
  console.log("/api/damkar");
  console.log("/api/kantor-polisi");
  console.log("/api/jalan");
  console.log("/api/administrasi");
  console.log("======================================");

});
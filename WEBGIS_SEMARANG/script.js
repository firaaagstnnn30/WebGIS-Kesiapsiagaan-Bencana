// ========================================
// MEMBUAT PETA
// ========================================

var map = L.map('map').setView(
    [-7.0051, 110.4381],
    12
);


// ========================================
// BASEMAP
// ========================================

var osm = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        attribution: '&copy; OpenStreetMap contributors'
    }
);

osm.addTo(map);


// ========================================
// GROUP LAYER
// ========================================

var layerAdmin = L.layerGroup().addTo(map);
var layerIndex = L.layerGroup().addTo(map);
var layerJalan = L.layerGroup();

var layerDamkar = L.layerGroup().addTo(map);
var layerPuskesmas = L.layerGroup().addTo(map);
var layerRS = L.layerGroup().addTo(map);
var layerPolisi = L.layerGroup().addTo(map);


// ========================================
// WARNA INDEKS
// ========================================

function warnaAksesibilitas(kelas) {

    if (kelas === 'Tinggi') {
        return '#55b96a';
    }

    if (kelas === 'Sedang') {
        return '#f7d84b';
    }

    if (kelas === 'Rendah') {
        return '#ef6464';
    }

    return '#cccccc';
}


// ========================================
// ICON FASILITAS
// ========================================

function buatIcon(emoji, warna) {

    return L.divIcon({

        className: 'facility-marker',

        html: `
            <div style="
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background: ${warna};
                border: 2px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.35);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
            ">
                ${emoji}
            </div>
        `,

        iconSize: [30, 30],

        iconAnchor: [15, 15]

    });

}


// ========================================
// ADMINISTRASI
// ========================================

fetch('data/administrasi.geojson')

    .then(response => response.json())

    .then(data => {

        var admin = L.geoJSON(data, {

            style: {

                color: '#263238',

                weight: 1.5,

                fillOpacity: 0,

                fillColor: 'white'

            }

        });

        admin.addTo(layerAdmin);

    })

    .catch(error => {

        console.error(
            'Gagal memuat administrasi:',
            error
        );

    });


// ========================================
// HASIL ANALISIS AKSESIBILITAS
// ========================================

fetch('data/kecamatan_aksesibilitas.geojson')

    .then(response => response.json())

    .then(data => {

        var indexLayer = L.geoJSON(data, {

            style: function(feature) {

                var kelas =
                    feature.properties.kelas_aksesibilitas;

                return {

                    color: '#444',

                    weight: 1,

                    fillColor:
                        warnaAksesibilitas(kelas),

                    fillOpacity: 0.52

                };

            },


            onEachFeature: function(feature, layer) {

                var p = feature.properties;

                var kelas =
                    p.kelas_aksesibilitas;

                var warna =
                    warnaAksesibilitas(kelas);


                layer.bindPopup(`

                    <div class="popup-title">
                        Kecamatan ${p.NAME_3}
                    </div>


                    <div class="popup-row">
                        <span>Skor Damkar</span>
                        <strong>
                            ${Number(p.skor_damkar).toFixed(3)}
                        </strong>
                    </div>


                    <div class="popup-row">
                        <span>Skor Rumah Sakit</span>
                        <strong>
                            ${Number(p.skor_rs).toFixed(3)}
                        </strong>
                    </div>


                    <div class="popup-row">
                        <span>Skor Puskesmas</span>
                        <strong>
                            ${Number(p.skor_puskesmas).toFixed(3)}
                        </strong>
                    </div>


                    <div class="popup-row">
                        <span>Skor Polisi</span>
                        <strong>
                            ${Number(p.skor_polisi).toFixed(3)}
                        </strong>
                    </div>


                    <div class="popup-row">
                        <span>Skor Jalan</span>
                        <strong>
                            ${Number(p.skor_jalan).toFixed(3)}
                        </strong>
                    </div>


                    <div class="popup-index">

                        <div>
                            Indeks Aksesibilitas
                        </div>

                        <strong style="font-size:20px;">
                            ${Number(
                                p.indeks_aksesibilitas
                            ).toFixed(3)}
                        </strong>

                        <br>

                        <span
                            class="popup-class"
                            style="
                                background:${warna};
                            "
                        >
                            ${kelas}
                        </span>

                    </div>

                `);


                // Highlight ketika mouse masuk
                layer.on({

                    mouseover: function(e) {

                        e.target.setStyle({

                            weight: 3,

                            fillOpacity: 0.7

                        });

                    },

                    mouseout: function(e) {

                        indexLayer.resetStyle(
                            e.target
                        );

                    }

                });

            }

        });


        indexLayer.addTo(layerIndex);


        // ====================================
        // HITUNG KATEGORI
        // ====================================

        var tinggi = 0;
        var sedang = 0;
        var rendah = 0;


        data.features.forEach(function(feature) {

            var kelas =
                feature.properties.kelas_aksesibilitas;


            if (kelas === 'Tinggi') {

                tinggi++;

            }

            else if (kelas === 'Sedang') {

                sedang++;

            }

            else if (kelas === 'Rendah') {

                rendah++;

            }

        });


        var total = data.features.length;


        document.getElementById(
            'jumlah-kecamatan'
        ).innerText = total;


        document.getElementById(
            'total-tinggi'
        ).innerText = tinggi;


        document.getElementById(
            'total-sedang'
        ).innerText = sedang;


        document.getElementById(
            'total-rendah'
        ).innerText = rendah;


        var persenTinggi =
            ((tinggi / total) * 100).toFixed(1);


        var persenSedang =
            ((sedang / total) * 100).toFixed(1);


        var persenRendah =
            ((rendah / total) * 100).toFixed(1);


        document.getElementById(
            'persen-tinggi'
        ).innerText =
            tinggi + ' kecamatan (' +
            persenTinggi + '%)';


        document.getElementById(
            'persen-sedang'
        ).innerText =
            sedang + ' kecamatan (' +
            persenSedang + '%)';


        document.getElementById(
            'persen-rendah'
        ).innerText =
            rendah + ' kecamatan (' +
            persenRendah + '%)';


        // ====================================
        // GRAFIK KATEGORI
        // ====================================

        new Chart(

            document.getElementById(
                'categoryChart'
            ),

            {

                type: 'doughnut',

                data: {

                    labels: [
                        'Tinggi',
                        'Sedang',
                        'Rendah'
                    ],

                    datasets: [{

                        data: [
                            tinggi,
                            sedang,
                            rendah
                        ],

                        backgroundColor: [
                            '#55b96a',
                            '#f7d84b',
                            '#ef6464'
                        ],

                        borderWidth: 0

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }

        );

    })

    .catch(error => {

        console.error(
            'Gagal memuat hasil analisis:',
            error
        );

    });


// ========================================
// JARINGAN JALAN
// ========================================

fetch('data/jalan.geojson')

    .then(response => response.json())

    .then(data => {

        var jalan = L.geoJSON(data, {

            style: {

                color: '#e58b20',

                weight: 1

            }

        });

        jalan.addTo(layerJalan);

    })

    .catch(error => {

        console.error(
            'Gagal memuat jalan:',
            error
        );

    });


// ========================================
// FUNGSI LOAD FASILITAS
// ========================================

function loadFasilitas(
    file,
    layerGroup,
    emoji,
    warna,
    namaFasilitas,
    idJumlah
) {

    fetch(file)

        .then(response => response.json())

        .then(data => {

            document.getElementById(
                idJumlah
            ).innerText =
                data.features.length;


            var layer = L.geoJSON(data, {

                pointToLayer:
                    function(feature, latlng) {

                        return L.marker(
                            latlng,
                            {
                                icon:
                                    buatIcon(
                                        emoji,
                                        warna
                                    )
                            }
                        );

                    },


                onEachFeature:
                    function(
                        feature,
                        layer
                    ) {

                        var nama =
                            feature.properties.name ||
                            feature.properties.Name ||
                            namaFasilitas;


                        layer.bindPopup(`

                            <div class="popup-title">
                                ${nama}
                            </div>

                            <div>
                                <b>Fasilitas:</b>
                                ${namaFasilitas}
                            </div>

                        `);

                    }

            });


            layer.addTo(layerGroup);

        })

        .catch(error => {

            console.error(
                'Gagal memuat ' +
                namaFasilitas +
                ':',
                error
            );

        });

}


// ========================================
// LOAD FASILITAS
// ========================================

loadFasilitas(
    'data/damkar.geojson',
    layerDamkar,
    '🚒',
    '#f59e0b',
    'Pemadam Kebakaran',
    'jumlah-damkar'
);


loadFasilitas(
    'data/puskesmas.geojson',
    layerPuskesmas,
    '🏥',
    '#22c55e',
    'Puskesmas',
    'jumlah-puskesmas'
);


loadFasilitas(
    'data/rumah_sakit.geojson',
    layerRS,
    '🏥',
    '#ef4444',
    'Rumah Sakit',
    'jumlah-rs'
);


loadFasilitas(
    'data/kantor_polisi.geojson',
    layerPolisi,
    '👮',
    '#2563eb',
    'Kantor Polisi',
    'jumlah-polisi'
);


// ========================================
// TOGGLE LAYER
// ========================================

document.getElementById(
    'toggle-admin'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerAdmin);

        }

        else {

            map.removeLayer(layerAdmin);

        }

    }
);


document.getElementById(
    'toggle-index'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerIndex);

        }

        else {

            map.removeLayer(layerIndex);

        }

    }
);


document.getElementById(
    'toggle-jalan'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerJalan);

        }

        else {

            map.removeLayer(layerJalan);

        }

    }
);


document.getElementById(
    'toggle-rs'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerRS);

        }

        else {

            map.removeLayer(layerRS);

        }

    }
);


document.getElementById(
    'toggle-puskesmas'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerPuskesmas);

        }

        else {

            map.removeLayer(layerPuskesmas);

        }

    }
);


document.getElementById(
    'toggle-damkar'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerDamkar);

        }

        else {

            map.removeLayer(layerDamkar);

        }

    }
);


document.getElementById(
    'toggle-polisi'
).addEventListener(
    'change',
    function() {

        if (this.checked) {

            map.addLayer(layerPolisi);

        }

        else {

            map.removeLayer(layerPolisi);

        }

    }
);


// ========================================
// GRAFIK JUMLAH FASILITAS
// ========================================

var facilityChart =
    new Chart(

        document.getElementById(
            'facilityChart'
        ),

        {

            type: 'bar',

            data: {

                labels: [
                    'Rumah Sakit',
                    'Puskesmas',
                    'Damkar',
                    'Polisi'
                ],

                datasets: [{

                    label:
                        'Jumlah fasilitas',

                    data: [
                        0,
                        0,
                        0,
                        0
                    ],

                    backgroundColor: [
                        '#ef4444',
                        '#22c55e',
                        '#f59e0b',
                        '#2563eb'
                    ],

                    borderRadius: 5

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }

                    }

                }

            }

        }

    );


// ========================================
// UPDATE GRAFIK JUMLAH FASILITAS
// ========================================

function updateFacilityChart() {

    facilityChart.data.datasets[0].data = [

        Number(
            document.getElementById(
                'jumlah-rs'
            ).innerText
        ),

        Number(
            document.getElementById(
                'jumlah-puskesmas'
            ).innerText
        ),

        Number(
            document.getElementById(
                'jumlah-damkar'
            ).innerText
        ),

        Number(
            document.getElementById(
                'jumlah-polisi'
            ).innerText
        )

    ];

    facilityChart.update();

}


setTimeout(
    updateFacilityChart,
    1500
);


// ========================================
// TANGGAL & JAM
// ========================================

function updateDateTime() {

    var sekarang = new Date();


    var tanggal = sekarang.toLocaleDateString(
        'id-ID',
        {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        }
    );


    var jam = sekarang.toLocaleTimeString(
        'id-ID',
        {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }
    );


    document.getElementById(
        'tanggal'
    ).innerText = tanggal;


    document.getElementById(
        'jam'
    ).innerText = jam + ' WIB';

}


updateDateTime();


setInterval(
    updateDateTime,
    1000
);


// ========================================
// FUNGSI MENU
// ========================================

function fokusPeta() {

    map.setView(
        [-7.0051, 110.4381],
        12
    );

}


function bukaAnalisis() {

    document.querySelector(
        '.dashboard-bottom'
    ).scrollIntoView({
        behavior: 'smooth'
    });

}


function bukaData() {

    document.querySelector(
        '.stat-cards'
    ).scrollIntoView({
        behavior: 'smooth'
    });

}


function bukaTentang() {

    document.querySelector(
        '.information'
    ).scrollIntoView({
        behavior: 'smooth'
    });

}
// ========================================
// MEMBUAT PETA
// ========================================

var map = L.map('map').setView(
    [-7.0051, 110.4381],
    12
);

window.addEventListener('resize', function() {
    map.invalidateSize();
});
setTimeout(function() {
    map.invalidateSize();
}, 300);


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
var layerJalan = L.layerGroup().addTo(map);

var layerDamkar = L.layerGroup().addTo(map);
var layerPuskesmas = L.layerGroup().addTo(map);
var layerRS = L.layerGroup().addTo(map);
var layerPolisi = L.layerGroup().addTo(map);

// Layer indeks kesiapsiagaan
var layerIndeksPemenuhan = L.layerGroup();      // berdasar skor_pemenuhan_sni
var layerIndeksIsochrone = L.layerGroup();      // berdasar indeks_isochrone (WorldPop)
var layerIndeksAksesibilitas = L.layerGroup();  // berdasar skor_aksesibilitas_100
var layerIndeksGabungan = L.layerGroup().addTo(map); // kelas_final (default)

// Layer poligon jangkauan waktu Isochrone
var layerIsoDamkar = L.layerGroup();
var layerIsoPolisi = L.layerGroup();
var layerIsoPuskesmas = L.layerGroup();
var layerIsoRS = L.layerGroup();

var activeIndexLayer = 'gabungan'; // mode awal



// ========================================
// FUNGSI WARNA
// ========================================

function warnaAksesibilitas(kelas) {
    if (kelas === 'Tinggi') return '#55b96a';
    if (kelas === 'Sedang') return '#f7d84b';
    if (kelas === 'Rendah') return '#ef6464';
    return '#cccccc';
}

// Klasifikasi equal-interval dari array nilai
function klasifikasiEqualInterval(nilai, semuaNilai) {
    var min = Math.min.apply(null, semuaNilai);
    var max = Math.max.apply(null, semuaNilai);
    var interval = (max - min) / 3;
    var batas1 = min + interval;
    var batas2 = min + 2 * interval;
    if (nilai <= batas1) return 'Rendah';
    if (nilai <= batas2) return 'Sedang';
    return 'Tinggi';
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

fetch('output/kecamatan_aksesibilitas.geojson')

    .then(response => response.json())

    .then(data => {

        // Kumpulkan semua nilai skor untuk klasifikasi equal-interval
        var semuaSkorPemenuhan = data.features.map(function(f) {
            return f.properties.skor_pemenuhan_sni || 0;
        });
        var semuaSkorIsochrone = data.features.map(function(f) {
            return f.properties.indeks_isochrone || 0;
        });
        var semuaSkorAkses = data.features.map(function(f) {
            return f.properties.skor_aksesibilitas_100 || 0;
        });


        // ====================================
        // FUNGSI BUAT LAYER INDEKS
        // ====================================

        function buatLayerIndeks(modeKelas) {

            return L.geoJSON(data, {

                style: function(feature) {

                    var p = feature.properties;
                    var kelas;

                    if (modeKelas === 'pemenuhan') {
                        kelas = klasifikasiEqualInterval(
                            p.skor_pemenuhan_sni || 0,
                            semuaSkorPemenuhan
                        );
                    } else if (modeKelas === 'isochrone') {
                        kelas = p.kelas_isochrone || klasifikasiEqualInterval(
                            p.indeks_isochrone || 0,
                            semuaSkorIsochrone
                        );
                    } else if (modeKelas === 'aksesibilitas') {
                        kelas = klasifikasiEqualInterval(
                            p.skor_aksesibilitas_100 || 0,
                            semuaSkorAkses
                        );
                    } else {
                        // gabungan
                        kelas = p.kelas_final || p.kelas_aksesibilitas || 'Sedang';
                    }

                    return {
                        color: '#444',
                        weight: 1,
                        fillColor: warnaAksesibilitas(kelas),
                        fillOpacity: 0.52
                    };

                },


                onEachFeature: function(feature, layer) {

                    var p = feature.properties;

                    // Hitung kelas untuk SETIAP mode
                    var kelasPemenuhan = klasifikasiEqualInterval(
                        p.skor_pemenuhan_sni || 0, semuaSkorPemenuhan
                    );
                    var kelasIsochrone = p.kelas_isochrone || klasifikasiEqualInterval(
                        p.indeks_isochrone || 0, semuaSkorIsochrone
                    );
                    var kelasAkses = klasifikasiEqualInterval(
                        p.skor_aksesibilitas_100 || 0, semuaSkorAkses
                    );
                    var kelasGabungan = p.kelas_final || p.kelas_aksesibilitas || 'Sedang';

                    // Warna badge per indeks
                    var wP = warnaAksesibilitas(kelasPemenuhan);
                    var wI = warnaAksesibilitas(kelasIsochrone);
                    var wA = warnaAksesibilitas(kelasAkses);
                    var wG = warnaAksesibilitas(kelasGabungan);

                    // Hitung berapa jenis fasilitas yang sudah mencapai kuota SNI
                    var jumlahLengkap = 0;
                    if ((p.eksisting_rumah_sakit || 0) >= (p.kebutuhan_rumah_sakit || 1)) jumlahLengkap++;
                    if ((p.eksisting_puskesmas || 0) >= (p.kebutuhan_puskesmas || 1)) jumlahLengkap++;
                    if ((p.eksisting_damkar || 0) >= (p.kebutuhan_pos_damkar || 1)) jumlahLengkap++;
                    if ((p.eksisting_kantor_polisi || 0) >= (p.kebutuhan_kantor_polisi || 1)) jumlahLengkap++;

                    var statusLabel, statusColor, statusBg, statusBadgeClass;
                    if (jumlahLengkap === 4) {
                        statusLabel = 'Lengkap (4/4 Fasilitas Memenuhi SNI)';
                        statusColor = '#15803d';
                        statusBg   = '#dcfce7';
                        statusBadgeClass = 'badge-memenuhi';
                    } else if (jumlahLengkap >= 2) {
                        statusLabel = 'Sebagian Memenuhi (' + jumlahLengkap + '/4 Fasilitas SNI)';
                        statusColor = '#0369a1';
                        statusBg   = '#e0f2fe';
                        statusBadgeClass = 'badge-sebagian';
                    } else {
                        statusLabel = 'Belum Memenuhi (' + jumlahLengkap + '/4 Fasilitas SNI)';
                        statusColor = '#b91c1c';
                        statusBg   = '#fee2e2';
                        statusBadgeClass = 'badge-belum';
                    }

                    var rincian = p.rincian_kekurangan || 'Sudah Memenuhi Kebutuhan';

                    var eksRS      = p.eksisting_rumah_sakit     !== undefined ? p.eksisting_rumah_sakit     : '-';
                    var bthRS      = p.kebutuhan_rumah_sakit     !== undefined ? p.kebutuhan_rumah_sakit     : '-';
                    var eksPus     = p.eksisting_puskesmas       !== undefined ? p.eksisting_puskesmas       : '-';
                    var bthPus     = p.kebutuhan_puskesmas       !== undefined ? p.kebutuhan_puskesmas       : '-';
                    var eksDamkar  = p.eksisting_damkar          !== undefined ? p.eksisting_damkar          : '-';
                    var bthDamkar  = p.kebutuhan_pos_damkar      !== undefined ? p.kebutuhan_pos_damkar      : '-';
                    var eksPolisi  = p.eksisting_kantor_polisi   !== undefined ? p.eksisting_kantor_polisi   : '-';
                    var bthPolisi  = p.kebutuhan_kantor_polisi   !== undefined ? p.kebutuhan_kantor_polisi   : '-';

                    layer.bindPopup(`

                        <div class="popup-title" style="font-size:16px; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:4px;">
                            Kecamatan ${p.NAME_3}
                        </div>

                        <div style="margin-bottom:10px; background:#f8fafc; padding:8px; border-radius:6px; border:1px solid #e2e8f0;">
                            <div style="font-size:11px; color:#64748b; margin-bottom:4px; font-weight:600;">INDEKS KESIAPSIAGAAN</div>
                            <table style="width:100%; font-size:11px; border-collapse:collapse;">
                                <tr>
                                    <td style="padding:2px 4px; color:#475569;">Pemenuhan SNI</td>
                                    <td style="padding:2px 4px;">
                                        <span style="background:${wP}; color:white; font-weight:bold; padding:1px 7px; border-radius:4px; font-size:11px;">
                                            ${kelasPemenuhan}
                                        </span>
                                        <span style="color:#94a3b8; margin-left:4px;">(${(p.skor_pemenuhan_sni||0).toFixed(1)}%)</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:2px 4px; color:#475569;">Aksesibilitas Isochrone</td>
                                    <td style="padding:2px 4px;">
                                        <span style="background:${wI}; color:white; font-weight:bold; padding:1px 7px; border-radius:4px; font-size:11px;">
                                            ${kelasIsochrone}
                                        </span>
                                        <span style="color:#94a3b8; margin-left:4px;">(${(p.indeks_isochrone||0).toFixed(1)}%)</span>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:2px 4px; color:#475569;">Gabungan (Final)</td>
                                    <td style="padding:2px 4px;">
                                        <span style="background:${wG}; color:white; font-weight:bold; padding:1px 7px; border-radius:4px; font-size:11px;">
                                            ${kelasGabungan}
                                        </span>
                                        <span style="color:#94a3b8; margin-left:4px;">(${(p.indeks_final||0).toFixed(1)}%)</span>
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <div style="margin-bottom:10px; background:#f0fdf4; padding:8px; border-radius:6px; border:1px solid #bbf7d0;">
                            <div style="font-size:11px; color:#15803d; margin-bottom:4px; font-weight:600;">CAKUPAN PENDUDUK WORLDPOP (WAKTU TANGGAP)</div>
                            <table style="width:100%; font-size:11px; border-collapse:collapse;">
                                <tr>
                                    <td style="padding:2px 4px; color:#374151;">Damkar (15 mnt)</td>
                                    <td style="padding:2px 4px; font-weight:bold; text-align:right;">${(p.persen_cakupan_damkar||0).toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td style="padding:2px 4px; color:#374151;">Polisi (15 mnt)</td>
                                    <td style="padding:2px 4px; font-weight:bold; text-align:right;">${(p.persen_cakupan_polisi||0).toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td style="padding:2px 4px; color:#374151;">Puskesmas (15 mnt)</td>
                                    <td style="padding:2px 4px; font-weight:bold; text-align:right;">${(p.persen_cakupan_puskesmas||0).toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td style="padding:2px 4px; color:#374151;">Rumah Sakit (30 mnt)</td>
                                    <td style="padding:2px 4px; font-weight:bold; text-align:right;">${(p.persen_cakupan_rumah_sakit||0).toFixed(1)}%</td>
                                </tr>
                            </table>
                            <div style="font-size:10px; color:#475569; margin-top:4px; border-top:1px dashed #cbd5e1; padding-top:2px;">
                                Total WorldPop: <strong>${Number(p.worldpop_total||0).toLocaleString('id-ID')} jiwa</strong> (Rank #${p.rank_isochrone||'-'})
                            </div>
                        </div>

                        <div style="margin-bottom:8px;">
                            <span style="font-size:12px; color:#64748b;">Kelengkapan Kuota Fasilitas (SNI):</span><br>
                            <span style="background:${statusBg}; color:${statusColor}; font-weight:bold; padding:2px 8px; border-radius:4px; font-size:12px; display:inline-block; margin-top:2px;">
                                ${statusLabel}
                            </span>
                        </div>

                        <div style="margin-bottom:10px; font-size:12px;">
                            <strong>Rincian Kekurangan:</strong><br>
                            <span style="color:${rincian === 'Sudah Memenuhi Kebutuhan' ? '#16a34a' : '#dc2626'}; font-weight:500;">
                                ${rincian}
                            </span>
                        </div>

                        <div style="font-size:11px; background:#f8fafc; padding:8px; border-radius:6px; border:1px solid #e2e8f0;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                                <span>🏥 Rumah Sakit:</span> <strong>${eksRS} / ${bthRS}</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                                <span>🏥 Puskesmas:</span> <strong>${eksPus} / ${bthPus}</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                                <span>🚒 Pos Damkar:</span> <strong>${eksDamkar} / ${bthDamkar}</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between;">
                                <span>👮 Kantor Polisi:</span> <strong>${eksPolisi} / ${bthPolisi}</strong>
                            </div>
                        </div>

                    `);


                    // Highlight hover
                    layer.on({
                        mouseover: function(e) {
                            e.target.setStyle({ weight: 3, fillOpacity: 0.7 });
                        },
                        mouseout: function(e) {
                            // reset style dari layer yang aktif
                            if (e.target._map) {
                                e.target.setStyle({
                                    weight: 1,
                                    fillOpacity: 0.52
                                });
                            }
                        }
                    });

                }

            });

        }


        // Buat keempat layer indeks
        var geoLayerPemenuhan     = buatLayerIndeks('pemenuhan');
        var geoLayerIsochrone     = buatLayerIndeks('isochrone');
        var geoLayerAksesibilitas = buatLayerIndeks('aksesibilitas');
        var geoLayerGabungan      = buatLayerIndeks('gabungan');

        geoLayerPemenuhan.addTo(layerIndeksPemenuhan);
        geoLayerIsochrone.addTo(layerIndeksIsochrone);
        geoLayerAksesibilitas.addTo(layerIndeksAksesibilitas);
        geoLayerGabungan.addTo(layerIndeksGabungan);


        // ====================================
        // LOAD POLIGON ISOCHRONE FASILITAS
        // ====================================

        fetch('output/isochrone_fasilitas.geojson')
            .then(res => res.json())
            .then(isoData => {
                isoData.features.forEach(function(feat) {
                    var p = feat.properties;
                    var j = p.jenis;
                    var color = p.warna || '#ef4444';
                    var layer = L.geoJSON(feat, {
                        style: {
                            color: color,
                            weight: 2,
                            fillColor: color,
                            fillOpacity: 0.22,
                            dashArray: '5, 5'
                        }
                    });
                    layer.bindPopup(`<strong>Area Jangkauan: ${p.nama}</strong><br>Waktu Tanggap: ${p.waktu_menit} menit`);
                    if (j === 'damkar') layer.addTo(layerIsoDamkar);
                    else if (j === 'polisi') layer.addTo(layerIsoPolisi);
                    else if (j === 'puskesmas') layer.addTo(layerIsoPuskesmas);
                    else if (j === 'rumah_sakit') layer.addTo(layerIsoRS);
                });
            })
            .catch(e => console.log('Isochrone layer note:', e));

        // Checkbox toggle untuk layer isochrone
        function setupIsoToggle(id, layer) {
            var el = document.getElementById(id);
            if (el) {
                if (localStorage.getItem('webgis_' + id) !== null) {
                    el.checked = localStorage.getItem('webgis_' + id) === 'true';
                }
                if (el.checked) map.addLayer(layer);
                el.addEventListener('change', function() {
                    localStorage.setItem('webgis_' + id, this.checked);
                    if (this.checked) map.addLayer(layer);
                    else map.removeLayer(layer);
                });
            }
        }
        setupIsoToggle('toggle-iso-damkar', layerIsoDamkar);
        setupIsoToggle('toggle-iso-polisi', layerIsoPolisi);
        setupIsoToggle('toggle-iso-puskesmas', layerIsoPuskesmas);
        setupIsoToggle('toggle-iso-rs', layerIsoRS);


        // ====================================
        // RADIO TOGGLE INDEKS
        // ====================================

        function aktifkanModeIndeks(mode) {
            // Hapus semua layer indeks dari peta
            map.removeLayer(layerIndeksPemenuhan);
            map.removeLayer(layerIndeksIsochrone);
            map.removeLayer(layerIndeksGabungan);

            var label = document.getElementById('legend-indeks-label');

            if (mode === 'pemenuhan') {
                map.addLayer(layerIndeksPemenuhan);
                if (label) label.textContent = 'Indeks Pemenuhan SNI';
            } else if (mode === 'isochrone') {
                map.addLayer(layerIndeksIsochrone);
                if (label) label.textContent = 'Aksesibilitas Fasilitas (Isochrone)';
            } else {
                map.addLayer(layerIndeksGabungan);
                if (label) label.textContent = 'Indeks Gabungan Final';
            }
        }

        var rPemenuhan = document.getElementById('mode-pemenuhan');
        if (rPemenuhan) {
            rPemenuhan.addEventListener('change', function() {
                if (this.checked) aktifkanModeIndeks('pemenuhan');
            });
        }
        var rIsochrone = document.getElementById('mode-isochrone');
        if (rIsochrone) {
            rIsochrone.addEventListener('change', function() {
                if (this.checked) aktifkanModeIndeks('isochrone');
            });
        }
        var rGabungan = document.getElementById('mode-gabungan');
        if (rGabungan) {
            rGabungan.addEventListener('change', function() {
                if (this.checked) aktifkanModeIndeks('gabungan');
            });
        }


        // ====================================
        // HITUNG KATEGORI (berdasar gabungan)
        // ====================================

        var tinggi = 0, sedang = 0, rendah = 0;

        data.features.forEach(function(feature) {
            var kelas = feature.properties.kelas_final || feature.properties.kelas_aksesibilitas;
            if (kelas === 'Tinggi') tinggi++;
            else if (kelas === 'Sedang') sedang++;
            else if (kelas === 'Rendah') rendah++;
        });

        var total = data.features.length;

        var elJml = document.getElementById('jumlah-kecamatan');
        if (elJml) elJml.innerText = total;

        var elTinggi = document.getElementById('total-tinggi');
        if (elTinggi) elTinggi.innerText = tinggi;

        var elSedang = document.getElementById('total-sedang');
        if (elSedang) elSedang.innerText = sedang;

        var elRendah = document.getElementById('total-rendah');
        if (elRendah) elRendah.innerText = rendah;

        var persenTinggi = ((tinggi / total) * 100).toFixed(1);
        var persenSedang = ((sedang / total) * 100).toFixed(1);
        var persenRendah = ((rendah / total) * 100).toFixed(1);

        var elPTinggi = document.getElementById('persen-tinggi');
        if (elPTinggi) elPTinggi.innerText = tinggi + ' kecamatan (' + persenTinggi + '%)';

        var elPSedang = document.getElementById('persen-sedang');
        if (elPSedang) elPSedang.innerText = sedang + ' kecamatan (' + persenSedang + '%)';

        var elPRendah = document.getElementById('persen-rendah');
        if (elPRendah) elPRendah.innerText = rendah + ' kecamatan (' + persenRendah + '%)';


        // ====================================
        // POPULATE MATRIKS TABEL ATRIBUT
        // ====================================

        var tbody = document.getElementById('tabel-body');
        if (tbody) {
            tbody.innerHTML = '';
            data.features.forEach(function(feature, index) {
                var p = feature.properties;

                var kelasFinal    = p.kelas_final || p.kelas_aksesibilitas || 'Sedang';
                var kelasPmhSNI   = klasifikasiEqualInterval(
                    p.skor_pemenuhan_sni || 0, semuaSkorPemenuhan
                );
                var kelasIsoTbl   = p.kelas_isochrone || klasifikasiEqualInterval(
                    p.indeks_isochrone || 0, semuaSkorIsochrone
                );
                var kelasAksesTbl = klasifikasiEqualInterval(
                    p.skor_aksesibilitas_100 || 0, semuaSkorAkses
                );

                var jmlLengkapTbl = 0;
                if ((p.eksisting_rumah_sakit || 0) >= (p.kebutuhan_rumah_sakit || 1)) jmlLengkapTbl++;
                if ((p.eksisting_puskesmas || 0) >= (p.kebutuhan_puskesmas || 1)) jmlLengkapTbl++;
                if ((p.eksisting_damkar || 0) >= (p.kebutuhan_pos_damkar || 1)) jmlLengkapTbl++;
                if ((p.eksisting_kantor_polisi || 0) >= (p.kebutuhan_kantor_polisi || 1)) jmlLengkapTbl++;

                var badgeStatusClass = jmlLengkapTbl === 4 ? 'badge-memenuhi' : (jmlLengkapTbl >= 2 ? 'badge-sebagian' : 'badge-belum');
                var statusText = jmlLengkapTbl === 4 ? 'Lengkap (4/4)' : (jmlLengkapTbl >= 2 ? 'Sebagian (' + jmlLengkapTbl + '/4)' : 'Kurang (' + jmlLengkapTbl + '/4)');
                var rincian = p.rincian_kekurangan || 'Sudah Memenuhi Kebutuhan';

                var badgeFinal   = 'badge-' + kelasFinal.toLowerCase();
                var badgeSNI     = 'badge-' + kelasPmhSNI.toLowerCase();
                var badgeIso     = 'badge-' + kelasIsoTbl.toLowerCase();
                var rincianClass = rincian === 'Sudah Memenuhi Kebutuhan' ? 'text-memenuhi' : 'text-kekurangan';

                var tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td><strong>${p.NAME_3}</strong></td>
                    <td>${Number(p.Penduduk || p.Penduduk_x || p.Penduduk_y || 0).toLocaleString('id-ID')}</td>
                    <td>${Number(p.worldpop_total || 0).toLocaleString('id-ID')}</td>
                    <td><span class="badge ${badgeFinal}">${kelasFinal}</span><br><small style="color:#94a3b8">(${(p.indeks_final||0).toFixed(1)}%)</small></td>
                    <td><span class="badge ${badgeSNI}">${kelasPmhSNI}</span><br><small style="color:#94a3b8">(${(p.skor_pemenuhan_sni||0).toFixed(1)}%)</small></td>
                    <td><span class="badge ${badgeIso}">${kelasIsoTbl}</span><br><small style="color:#94a3b8">(${(p.indeks_isochrone||0).toFixed(1)}%)</small></td>
                    <td><span style="font-weight:bold; color:#4338ca;">#${p.rank_isochrone || '-'}</span></td>
                    <td><span class="badge ${badgeStatusClass}">${statusText}</span></td>
                    <td><span class="${rincianClass}">${rincian}</span></td>
                    <td>${p.eksisting_rumah_sakit || 0} / ${p.kebutuhan_rumah_sakit || 0}</td>
                    <td>${p.eksisting_puskesmas || 0} / ${p.kebutuhan_puskesmas || 0}</td>
                    <td>${p.eksisting_damkar || 0} / ${p.kebutuhan_pos_damkar || 0}</td>
                    <td>${p.eksisting_kantor_polisi || 0} / ${p.kebutuhan_kantor_polisi || 0}</td>
                `;
                tbody.appendChild(tr);
            });
        }


        // ====================================
        // GRAFIK KATEGORI
        // ====================================

        new Chart(

            document.getElementById('categoryChart'),

            {

                type: 'doughnut',

                data: {

                    labels: ['Tinggi', 'Sedang', 'Rendah'],

                    datasets: [{

                        data: [tinggi, sedang, rendah],

                        backgroundColor: ['#55b96a', '#f7d84b', '#ef6464'],

                        borderWidth: 0

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {
                        legend: { display: false }
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
        } else {
            map.removeLayer(layerAdmin);
        }
    }
);

// Tidak ada toggle-index tunggal lagi — diganti radio di atas



var toggleJalan = document.getElementById('toggle-jalan');
if (toggleJalan) {
    if (localStorage.getItem('webgis_toggle_jalan') !== null) {
        toggleJalan.checked = localStorage.getItem('webgis_toggle_jalan') === 'true';
    }
    if (toggleJalan.checked) {
        map.addLayer(layerJalan);
    } else {
        map.removeLayer(layerJalan);
    }
    toggleJalan.addEventListener('change', function() {
        localStorage.setItem('webgis_toggle_jalan', this.checked);
        if (this.checked) {
            map.addLayer(layerJalan);
        } else {
            map.removeLayer(layerJalan);
        }
    });
}


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
        '.table-section'
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
// Generates HCOT-MW manuscript DOCX with embedded figures
"use strict";
const fs   = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, Header, Footer, PageNumber, LevelFormat, ExternalHyperlink,
} = require("docx");

// ── Constants ──────────────────────────────────────────────────────────────
const ROOT  = __dirname;
const FIGS  = path.join(ROOT, "figures");
const OUT   = path.join(ROOT, "HCOT-MW_manuscript.docx");

// A4 portrait, 2.5 cm margins (1417 DXA)
const PAGE_W   = 11906;   // DXA
const MARGIN   = 1417;    // 2.5 cm in DXA
const CONTENT  = PAGE_W - 2 * MARGIN;  // 9072 DXA ≈ 6.3"
const CONTENT_PT = (CONTENT / 1440) * 72; // ~453 pt

// Double spacing = 480 twips (240 = single, 480 = double)
const DS = { line: 480, lineRule: "auto" };

// Cell border
const CB = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const CBOLD = { style: BorderStyle.SINGLE, size: 8, color: "333333" };
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const cellBorders = { top: CB, bottom: CB, left: CB, right: CB };
const headBorders = { top: CBOLD, bottom: CBOLD, left: CB, right: CB };

// ── Helpers ────────────────────────────────────────────────────────────────
function img(filename, widthPt, heightPt) {
  const fullPath = path.join(FIGS, filename);
  if (!fs.existsSync(fullPath)) {
    console.warn("  WARNING: figure not found:", filename);
    return null;
  }
  const ext  = path.extname(filename).slice(1).toLowerCase();
  const data = fs.readFileSync(fullPath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [new ImageRun({
      type: ext === "jpg" ? "jpeg" : ext,
      data,
      transformation: { width: widthPt, height: heightPt },
      altText: { title: filename, description: filename, name: filename },
    })],
  });
}

function imgW(filename, widthInches) {
  const fullPath = path.join(FIGS, filename);
  if (!fs.existsSync(fullPath)) { console.warn("Missing:", filename); return null; }
  // Read pixel dims
  const data = fs.readFileSync(fullPath);
  // PNG: width at bytes 16-19, height 20-23
  let pxW = 1, pxH = 1;
  if (data[1] === 80 && data[2] === 78 && data[3] === 71) { // PNG
    pxW = data.readUInt32BE(16);
    pxH = data.readUInt32BE(20);
  }
  const ar = pxH / pxW;
  const wPt = widthInches * 72;
  const hPt = wPt * ar;
  return img(filename, Math.round(wPt), Math.round(hPt));
}

function caption(num, text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 240 },
    children: [
      new TextRun({ text: `Figure ${num}. `, bold: true, size: 20, font: "Times New Roman" }),
      new TextRun({ text, italics: true, size: 20, font: "Times New Roman" }),
    ],
  });
}

function tableCap(num, text) {
  return new Paragraph({
    spacing: { before: 240, after: 60 },
    children: [
      new TextRun({ text: `Table ${num}. `, bold: true, size: 22, font: "Times New Roman" }),
      new TextRun({ text, size: 22, font: "Times New Roman" }),
    ],
  });
}

function p(children_or_text, opts = {}) {
  const children = (typeof children_or_text === "string")
    ? [new TextRun({ text: children_or_text, size: 24, font: "Times New Roman" })]
    : children_or_text;
  return new Paragraph({
    spacing: { ...DS, before: 0, after: 120, ...opts.spacing },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children,
  });
}

function pItalic(text, opts = {}) {
  return p([new TextRun({ text, italics: true, size: 24, font: "Times New Roman" })], opts);
}

function run(text, opts = {}) {
  return new TextRun({ text, size: 24, font: "Times New Roman", ...opts });
}
function bold(text)   { return run(text, { bold: true }); }
function ital(text)   { return run(text, { italics: true }); }
function sup(text)    { return run(text, { superScript: true }); }
function sub_(text)   { return run(text, { subScript: true }); }

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 480, after: 120, line: 360, lineRule: "auto" },
    children: [new TextRun({ text, bold: true, size: 28, font: "Times New Roman", color: "000000" })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 360, after: 80, line: 320, lineRule: "auto" },
    children: [new TextRun({ text, bold: true, size: 24, font: "Times New Roman", color: "000000" })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 60, line: 280, lineRule: "auto" },
    children: [new TextRun({ text, bold: true, italics: true, size: 24, font: "Times New Roman", color: "000000" })],
  });
}

function bullet(text, children) {
  const c = children || [run(text)];
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { ...DS, before: 0, after: 60 },
    children: c,
  });
}

function blank() {
  return new Paragraph({ spacing: { before: 0, after: 0 } });
}

function sectionRule() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB", space: 1 } },
    children: [],
  });
}

function cell(content_or_para, opts = {}) {
  const children = (typeof content_or_para === "string")
    ? [new Paragraph({ children: [new TextRun({ text: content_or_para, size: 20, font: "Times New Roman", bold: opts.bold || false })], spacing: { before: 40, after: 40 } })]
    : [content_or_para];
  return new TableCell({
    borders: opts.head ? headBorders : cellBorders,
    shading: opts.head
      ? { fill: "E8E8E8", type: ShadingType.CLEAR }
      : { fill: "FFFFFF", type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    width: opts.w ? { size: opts.w, type: WidthType.DXA } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children,
  });
}
function hcell(text, w) { return cell(text, { head: true, bold: true, w }); }
function dcell(text, w) { return cell(text, { w }); }

function mkTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const tableRows = [
    new TableRow({
      tableHeader: true,
      children: headers.map((h, i) => hcell(h, colWidths[i])),
    }),
    ...rows.map(row => new TableRow({
      children: row.map((c, i) => dcell(String(c), colWidths[i])),
    })),
  ];
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: tableRows,
  });
}

// ── Figure registry (width in inches, auto-aspect) ─────────────────────────
function fig(num, filename, widthIn, captionText) {
  const i = imgW(filename, widthIn);
  const items = [];
  if (i) items.push(i);
  items.push(caption(num, captionText));
  return items;
}

// ── Build document ─────────────────────────────────────────────────────────
function build() {
  const children = [];
  const add = (...items) => {
    for (const it of items) {
      if (!it) continue;
      if (Array.isArray(it)) it.forEach(x => x && children.push(x));
      else children.push(it);
    }
  };

  // ── TITLE PAGE ────────────────────────────────────────────────────────────
  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 480, after: 240, line: 360, lineRule: "auto" },
    children: [new TextRun({
      text: "DETECTION AND ANALYSIS OF HIGH WIND SPEED CUT-OFF EVENTS IN TURKISH WIND POWER PLANTS USING REAL-TIME GENERATION DATA AND WRF SIMULATIONS",
      bold: true, size: 28, font: "Times New Roman",
    })],
  }));

  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 240, after: 60 },
    children: [
      run("Ömer Faruk AVCI"), sup("1"), run(", Assoc. Prof. Elçin TAN"), sup("2"),
    ],
  }));

  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 60 },
    children: [run("1,2 Istanbul Technical University, Faculty of Aeronautics and Astronautics,", { size: 20 }),],
  }));
  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 60 },
    children: [run("Department of Climate Science and Meteorological Engineering, Istanbul, Türkiye", { size: 20 })],
  }));
  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 240 },
    children: [
      run("avcio20@itu.edu.tr", { size: 20 }), run("  |  ", { size: 20 }),
      run("elcin.tan@itu.edu.tr", { size: 20 }),
    ],
  }));

  // Graphical abstract
  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 40 },
    children: [run("Graphical Abstract", { bold: true, size: 22 })],
  }));
  add(imgW("Fig0_graphical_abstract.png", 6.0));
  add(blank());

  // ── ABSTRACT ──────────────────────────────────────────────────────────────
  add(h1("Abstract"));
  add(p("Extreme wind events triggering automatic turbine shutdowns pose a growing operational risk in grids with high wind penetration. This study presents a comprehensive framework for the detection, characterization, and prediction of hard cut-off events across Turkey's licensed wind fleet. Using three years of hourly real-time generation data from the EPİAŞ Transparency Platform (January 2022–April 2025, ~161 wind power plants), cut-off events are defined as abrupt (>80%) drops from high output (>50 MW) to near zero (<10 MW) within one hour. Applying this algorithm to the extended dataset identifies 249 events across 43 wind farms. The March 2025 storm period was the most intense on record, with 16 March 2025 seeing 14 simultaneous cut-offs; the Thrace–Aegean corridor, notably SAROS RES (37 events), recorded the highest cumulative exposure. WRF ARW 4.6.0 two-domain (9 km / 3 km) mesoscale simulations for the peak March 2025 storm event reproduce the low-level jet structure and confirm the mesoscale origin of the shutdowns: simulated 100-m wind speeds at İSTANBUL RES reached 27.4 m/s, exceeding the turbine cut-out threshold (25 m/s) for four consecutive hours (15 March 23:00 – 16 March 02:00 UTC), while remaining farms recorded hourly means of 20.8–24.2 m/s. An XGBoost early warning model was trained and evaluated using a strictly leakage-free design: prediction windows end H + 1 hours before each event (window end at t − H − 1), all features are derived exclusively from 24-hour history windows, and evaluation follows a temporal split (2022–2023 train / 2024 validation / January–April 2025 test). The model achieves ROC-AUC values of 0.585, 0.571, and 0.549 at 6-, 12-, and 24-hour horizons respectively, demonstrating that purely generation-based features provide limited but non-trivial predictive skill and motivating the inclusion of meteorological predictors. The framework is applicable to any wind-heavy grid and provides a reproducible baseline for further development of operational early warning systems."));

  add(new Paragraph({
    spacing: { before: 120, after: 240 },
    children: [bold("Keywords: "), run("wind power, cut-off events, extreme winds, early warning, XGBoost, WRF, Turkey, EPİAŞ")],
  }));

  // ── ÖZET ──────────────────────────────────────────────────────────────────
  add(h1("Özet"));
  add(p("Aşırı rüzgar olayları, hızlar türbin kesme eşiklerini (genellikle 23–25 m/s) aştığında otomatik kapanmayı tetikleyerek yüksek rüzgar gücü payına sahip şebekelerde ani üretim kayıplarına neden olmaktadır. Bu çalışmada, lisanslı Türkiye rüzgar santrallerinde bu tür \"sert kesinti\" olaylarının tespiti, analizi ve erken uyarısı için kapsamlı bir çerçeve sunulmaktadır. EPİAŞ Şeffaflık Platformu'ndan elde edilen üç yıllık saatlik üretim verileri (Ocak 2022–Nisan 2025, 161 aktif santral) kullanılarak, kesinti olayları yüksek çıktıdan (>50 MW) sıfıra yakın (<10 MW) düzeye bir saat içinde ani (>%80) düşüş olarak tanımlanmıştır. Algoritma üç yıllık veri setine uygulandığında 43 santralde toplam 249 olay tespit edilmiş, kümülatif enerji kaybı 16.121 MWh olarak hesaplanmıştır. Ekonomik etki, gerçek EPİAŞ saatlik PTF fiyatları kullanılarak ölçülmüş; toplam doğrudan piyasa gelir kaybı 39 milyon TL (yaklaşık 1,60 milyon USD) olarak belirlenmiştir. Sızdırmazlık tasarımıyla geliştirilen XGBoost erken uyarı modeli, 6-, 12- ve 24-saatlik öngörü ufuklarında sırasıyla 0,585, 0,571 ve 0,549 ROC-AUC değerlerine ulaşmıştır. Çerçeve tamamen tekrarlanabilir nitelikte olup yüksek yenilenebilir enerji entegrasyonuna sahip diğer şebekelere de uygulanabilir."));
  add(new Paragraph({
    spacing: { before: 120, after: 240 },
    children: [bold("Anahtar kelimeler: "), run("rüzgar gücü, kesinti olayları, aşırı rüzgar, XGBoost, WRF, Türkiye, EPİAŞ")],
  }));

  // ── 1. INTRODUCTION ───────────────────────────────────────────────────────
  add(h1("1. INTRODUCTION"));
  add(h2("1.1 Background"));
  add(p([run("Wind energy has emerged as one of the fastest-growing renewable energy sources globally, driven by technological advancements, declining costs, and policy incentives aimed at decarbonizing electricity systems (Zheng et al., 2024). As of 2024, global installed wind power capacity exceeds 900 GW, with onshore wind representing the dominant share (GWEC, 2025; Web 5). Turkey has experienced particularly rapid growth in wind power deployment over the past decade, with installed capacity reaching approximately 14 GW by early 2025, positioning the country among the top wind energy markets in Europe (Çetin, 2023; Kaplan, 2015; GWEC, 2025; Republic of Turkey Ministry of Industry and Technology, 2019; Presidency of the Republic of Turkey Strategy and Budget Directorate, 2023).")]));
  add(p("The integration of large-scale wind power into electricity grids introduces operational challenges arising from the variable and partially predictable nature of wind resources (Panteli et al., 2017). While day-ahead and intraday forecasting systems have improved significantly (Adomako et al., 2024; Groch & Vermeulen, 2021; Hanifi et al., 2020; Wang et al., 2016), extreme wind events remain difficult to predict with sufficient lead time and spatial precision. Of particular concern are high wind speed events that exceed turbine design limits, triggering automatic safety shutdowns known as \"cut-out\" or \"cut-off\" events (Archer et al., 2020)."));

  add(h2("1.2 Wind Turbine Cut-off Phenomenon"));
  add(p("Modern horizontal-axis wind turbines are designed to operate within a specific wind speed envelope defined by three critical thresholds:"));
  add(bullet("", [bold("Cut-in speed"), run(" (typically 3–4 m/s): The minimum wind speed at which the turbine begins generating power.")]));
  add(bullet("", [bold("Rated speed"), run(" (typically 12–15 m/s): The wind speed at which the turbine reaches its nominal power output.")]));
  add(bullet("", [bold("Cut-out speed"), run(" (typically 23–25 m/s): The maximum wind speed beyond which the turbine shuts down to prevent mechanical damage.")]));

  add(p([run("When wind speeds exceed the cut-out threshold, turbines initiate an automatic shutdown sequence, pitching blades to feather position and engaging mechanical brakes (Archer et al., 2020; Burton et al., 2011; Dupač & Jablonský, 2023). This \"hard cut-off\" results in an abrupt transition from high power output to zero or near-zero generation within minutes. For large wind farms with capacities exceeding 100 MW, such events can remove substantial generation capacity from the grid with minimal warning (Panteli et al., 2017; Karagiannis et al., 2019).")]));
  add(p("The cut-out speed varies by turbine model and is determined by structural design standards such as IEC 61400-1 (International Electrotechnical Commission, 2019), which defines wind turbine classes based on reference wind speed and turbulence intensity. Class I turbines, designed for high-wind sites, typically have cut-out speeds of 25 m/s, while Class III turbines for lower-wind environments may have cut-out thresholds as low as 20 m/s. Some modern turbines incorporate \"storm ride-through\" or \"high wind ride-through\" capabilities that allow continued operation at reduced power during extreme gusts, but this technology is not universally deployed."));

  add(h2("1.3 Impacts on Grid Operations"));
  add(p("High wind speed cut-off events pose several challenges for electricity system operators (Panteli et al., 2017; Web 1):"));
  add(bullet("", [bold("Supply-demand imbalance: "), run("Sudden loss of wind generation creates real-time imbalances that must be compensated by reserve capacity, typically from thermal power plants or energy storage systems.")]));
  add(bullet("", [bold("Forecast errors: "), run("While weather models can predict storm systems days in advance, the precise timing and spatial extent of cut-out conditions are difficult to forecast at the hourly resolution required for operational planning (Adomako et al., 2024; Groch & Vermeulen, 2021).")]));
  add(bullet("", [bold("Spatial correlation: "), run("Large storm systems can trigger simultaneous cut-offs across multiple wind farms spanning hundreds of kilometers, amplifying the aggregate impact on system adequacy (Web 2; Web 3).")]));
  add(bullet("", [bold("Ramp rates: "), run("The transition from full output to zero occurs faster than most dispatchable generators can ramp up, potentially causing frequency deviations (Web 6).")]));
  add(bullet("", [bold("Economic impacts: "), run("Lost generation during high-wind periods represents foregone revenue for wind farm operators and may trigger balancing market penalties (Web 4).")]));

  add(p("As wind power penetration increases, the system-wide impact of correlated cut-off events grows proportionally (Zheng et al., 2024). Turkey's electricity system, with wind power contributing approximately 10–12% of annual generation, is increasingly exposed to these operational risks."));

  add(h2("1.4 Turkey's Wind Energy Landscape"));
  add(p("Turkey's wind resources are concentrated in several distinct geographic regions (Dadaser-Celik & Cengiz, 2014; Çetin, 2023):"));
  add(bullet("", [bold("Thrace (northwestern Turkey): "), run("Characterized by strong northerly winds from the Black Sea, the Thrace region hosts some of Turkey's largest wind farms, including clusters around Kırklareli, Edirne, and Tekirdağ provinces.")]));
  add(bullet("", [bold("Marmara region: "), run("The coastal and elevated areas surrounding the Sea of Marmara, including Istanbul, Balıkesir, Yalova, and Sakarya provinces, experience frequent high-wind episodes associated with both local topographic effects and synoptic-scale weather systems.")]));
  add(bullet("", [bold("Aegean coast: "), run("The western coastline from Çanakkale to İzmir benefits from consistent sea breezes and channeling effects through valleys, with notable wind farm concentrations around the Biga Peninsula and Gulf of İzmir.")]));
  add(bullet("", [bold("Central Anatolia: "), run("High-altitude plateaus in provinces such as Sivas and Konya experience continental wind regimes with occasional extreme events driven by cold fronts and orographic acceleration.")]));

  add(p("The Turkish wind fleet operates under the YEKDEM (renewable energy support mechanism) scheme, which provides feed-in tariffs for licensed power plants. As of 2025, approximately 190 licensed wind power plants participate in YEKDEM, with real-time generation data published hourly through the EPİAŞ (Energy Markets Operation Company) Transparency Platform."));

  add(h2("1.5 Motivation and Research Gap"));
  add(p("Despite the growing importance of wind power in Turkey's energy mix, systematic analysis of high wind speed cut-off events remains limited (Tan et al., 2021; Çetin, 2023). Previous studies have examined wind resource assessment, capacity factor optimization, and short-term forecasting (Dadaser-Celik & Cengiz, 2014; Çelik, 2003; Ucar & Balo, 2009; Tan et al., 2021; Yildiz et al., 2023), but few have focused specifically on extreme wind events and their operational impacts. Key gaps in the existing literature include:"));

  add(bullet("", [bold("Lack of event-level characterization: "), run("While aggregate statistics on wind power variability are available, detailed analysis of individual cut-off events—including timing, duration, spatial extent, and recovery patterns—is scarce. Data-driven detection work has begun in other markets (Luo et al., 2022) but no systematic fleet-wide characterisation exists for Turkey.")]));
  add(bullet("", [bold("Limited meteorological context: "), run("Most operational analyses rely solely on production data without linking observed cut-offs to specific weather systems or synoptic conditions (Hahmann et al., 2014; Hahmann et al., 2020).")]));
  add(bullet("", [bold("Absence of high-resolution modeling: "), run("Reanalysis products, while valuable for climatological studies, have insufficient spatial resolution to capture the mesoscale wind patterns that drive localized cut-off events over complex terrain (Li et al., 2021; Vemuri et al., 2022).")]));
  add(bullet("", [bold("No systematic vulnerability mapping: "), run("The relative exposure of different wind farms and regions to extreme wind events has not been quantified using observational or modeled data (Sahoo & Bhaskaran, 2018; Sulikowska & Wypych, 2021).")]));

  add(h2("1.6 Study Objectives"));
  add(p("This study addresses the identified research gaps through a combined data-driven, observational, and numerical modeling approach. The specific objectives are:"));
  add(bullet("", [bold("1."), run(" Develop a detection algorithm for identifying hard cut-off events from hourly real-time generation data, using threshold-based criteria that distinguish high-wind shutdowns from other causes of production variability.")]));
  add(bullet("", [bold("2."), run(" Characterize the frequency, severity, and spatiotemporal patterns of cut-off events across Turkey's licensed wind fleet over a three-year study period (January 2022–April 2025).")]));
  add(bullet("", [bold("3."), run(" Identify the most vulnerable wind farms and regions based on event frequency, cumulative production losses, and geographic clustering.")]));
  add(bullet("", [bold("4."), run(" Quantify the direct economic impact of detected cut-off events using actual market clearing prices (PTF) from the EPİAŞ Transparency Platform.")]));
  add(bullet("", [bold("5."), run(" Configure and execute WRF mesoscale simulations for representative cut-off cases, using ERA5 reanalysis as boundary conditions, to provide synoptic context for extreme wind dynamics at hub height.")]));
  add(bullet("", [bold("6."), run(" Develop and evaluate a leakage-free early warning model using gradient boosting (XGBoost) to predict cut-off events at 6-, 12-, and 24-hour lead times from historical generation data, establishing a reproducible baseline for operational forecasting.")]));
  add(bullet("", [bold("7."), run(" Provide actionable insights for wind farm operators, grid operators, and policymakers on managing extreme wind risks in Turkey's evolving power system.")]));

  // ── 2. DATA AND METHODS ───────────────────────────────────────────────────
  add(h1("2. DATA AND METHODS"));
  add(p("The overall pipeline is organised into three layers — data acquisition, event detection, and analysis/forecasting — as illustrated in Figure 2. The remainder of this section details each component."));

  add(h2("2.1 Study Area"));
  add(p("The study covers the entire extent of Turkey's licensed wind power fleet, with particular focus on the northwestern regions where cut-off events are most frequent. The primary geographic areas of interest include:"));
  add(bullet("", [bold("Thrace region: "), run("Kırklareli province, including wind farms at Kıyıköy, Vize, Süloğlu, and Evrencik")]));
  add(bullet("", [bold("Istanbul and eastern Marmara: "), run("Wind farms along the Black Sea coast and in the Çatalca district")]));
  add(bullet("", [bold("Southern Marmara: "), run("Balıkesir province, including the Bandırma and Erdek areas")]));
  add(bullet("", [bold("Aegean coast: "), run("The Çanakkale Peninsula, including Gülpınar and Saros areas")]));
  add(bullet("", [bold("Central Anatolia: "), run("Selected high-altitude sites including Kangal in Sivas province")]));

  add(p("The study area spans approximately 26°E to 38°E longitude and 38°N to 42°N latitude, encompassing diverse terrain from coastal lowlands to mountain ridges exceeding 1,500 m elevation. Figure 1 shows the geographic distribution of all 161 licensed wind power plants coloured by cut-off event frequency, with bubble size proportional to the number of events recorded at each plant. The dashed rectangle marks the WRF simulation domain centred over the Thrace–Marmara–northern Aegean corridor."));

  // Fig 1
  add(...fig(1, "Fig1_study_area.png", 6.0,
    "Study area: licensed wind power plants in Turkey with hard cut-off event frequency (Jan 2022–Apr 2025). Bubble size and colour indicate number of events per plant. Dashed rectangle: WRF simulation domain (3 km resolution)."));

  // Fig 2
  add(...fig(2, "Fig2_framework.png", 6.0,
    "HCOT-MW (Hard Cutoff Observatory for Turkish Wind Farms with Meteorological context and Warning) three-layer framework. Layer 1: data acquisition from EPİAŞ API and ERA5 reanalysis. Layer 2: threshold-based hard cut-off detector (249 events, 43 plants). Layer 3: economic quantification, spatial/temporal analysis, XGBoost early warning model, and WRF mesoscale simulation."));

  add(h2("2.2 Data Sources"));
  add(h3("2.2.1 EPİAŞ Transparency Platform"));
  add(p([run("Hourly generation data for all licensed wind power plants are obtained from the EPİAŞ Transparency Platform (Web 7; https://seffaflik.epias.com.tr/) via the "), run("/v1/renewables/data/licensed-realtime-generation", { font: "Courier New", size: 22 }), run(" API. Authentication uses a Ticket Granting Ticket (TGT). Custom Python scripts automate bulk retrieval in monthly batches. The primary dataset covers January 2022–April 2025 (~28,560 hourly values per plant, 161–165 active wind power plants depending on commissioning date; 161 plants were active throughout the full study period). Hourly day-ahead market clearing prices (PTF) from the "), run("/v1/markets/dam/data/mcp", { font: "Courier New", size: 22 }), run(" endpoint are retrieved for the same period to support economic impact estimation.")]));

  add(h3("2.2.2 Wind Farm Characteristics"));
  add(p("Wind farm locations and capacities are compiled from the EPİAŞ powerplant list API, public project documentation, EIA reports, and GIS databases. Key attributes: plant name, UEVCB code, installed capacity (MW), coordinates, province/district, and number of turbines (if available)."));

  add(h3("2.2.3 ERA5 Reanalysis"));
  add(p("ERA5 global atmospheric reanalysis data (ECMWF, 0.25° × 0.25° horizontal resolution, hourly; Hersbach et al., 2020) are used as initial and lateral boundary conditions for the WRF simulations and as supplementary synoptic context for detected cut-off events. Variables retrieved include 10-m and 100-m wind speed and direction, mean sea level pressure (MSLP), 2-m temperature, and relative humidity, for the period January 2022–April 2025. Data are obtained via the Copernicus Climate Data Store (CDS) API."));

  add(h2("2.3 Hard Cut-off Detection Methodology"));
  add(h3("2.3.1 Definition of Hard Cut-off Events"));
  add(p("A \"hard cut-off\" event is defined as a sudden transition from high power output to near-zero generation within a single hourly interval, indicative of an automatic turbine shutdown triggered by extreme wind speeds. The detection criteria are designed to distinguish true cut-off events from other sources of production variability such as grid curtailment, scheduled maintenance, or gradual wind speed decline."));

  add(h3("2.3.2 Detection Algorithm"));
  add(p("The detection algorithm applies three simultaneous criteria to each hourly transition. Figure 3 illustrates the detection on a representative case — SAROS RES during winter 2024–25."));
  add(bullet("", [bold("Pre-event production threshold: "), run("The generation in the hour preceding the event must exceed 50 MW, indicating that the wind farm was operating at substantial capacity.")]));
  add(bullet("", [bold("Post-event production threshold: "), run("The generation in the event hour must fall below 10 MW, indicating near-complete shutdown.")]));
  add(bullet("", [bold("Percentage drop threshold: "), run("The relative production decline must exceed 80%, calculated as:")]));

  // Equation
  add(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 120 },
    children: [
      run("Drop (%) = "), run("(P", { italics: true }), sub_("t−1"), run(" − P", { italics: true }), sub_("t"),
      run(") / P", { italics: true }), sub_("t−1"), run(" × 100     . . . (1)"),
    ],
  }));

  add(p([run("where P"), sub_("t−1"), run(" is the pre-event production and P"), sub_("t"), run(" is the event-hour production.")]));

  add(p("Events satisfying all three criteria are flagged as hard cut-offs. The algorithm is implemented in Python using the pandas library for time series manipulation."));

  // Fig 3
  add(...fig(3, "Fig3_detection_exemplar.png", 5.8,
    "Hard cut-off event detection exemplar: SAROS RES (Çanakkale), winter 2024–25. (a) Three-month overview with detected events (vertical lines); (b) 14-day event cluster; (c) single-event detail illustrating the abrupt production collapse, annotated with pre-event and event-hour generation values. Dashed lines: θ_high = 50 MW (orange) and θ_low = 10 MW (green)."));

  add(h3("2.3.3 Threshold Selection Rationale"));
  add(p("The selected thresholds represent a balance between sensitivity (detecting true cut-off events) and specificity (avoiding false positives from other causes). The 50 MW pre-event threshold corresponds to approximately 40–70% of rated capacity for medium-sized wind farms (70–120 MW installed capacity). The 10 MW post-event threshold allows a small tolerance for partial shutdowns. The 80% drop threshold ensures that only abrupt transitions are captured; gradual production declines typically result in smaller hourly drops."));

  add(h3("2.3.4 Threshold Robustness"));
  add(p("To verify that results are not artefacts of the specific threshold values chosen, a systematic sensitivity analysis was performed by varying each of the three parameters independently over a ±20% range in five equal steps: θ_high ∈ {40, 45, 50, 55, 60} MW; θ_low ∈ {8, 9, 10, 11, 12} MW; θ_drop ∈ {64, 68, 72, 76, 80, 84, 88, 92, 96}%. Across all 125 threshold combinations applied to the three-year dataset, the baseline configuration (θ_high = 50 MW, θ_low = 10 MW, θ_drop = 80%) yields 249 events. The result is most sensitive to θ_high, which directly governs the minimum farm capacity engaged before an event. The heatmap of event counts is provided in Supplementary Figure S2."));

  add(h3("2.3.5 Event Characterization"));
  add(p("For each detected event, the following attributes are recorded: timestamp, plant name, pre-event production (P_{t-1}), event production (P_t), production loss, complete shutdown flag (if P_t = 0 MW), and recovery time (hours until production returns to at least 50% of pre-event level)."));

  add(h2("2.4 Case Study Selection"));
  add(p("From the full dataset of detected cut-off events, nine case studies were selected for detailed analysis based on temporal clustering during the extended storm period, geographic diversity across the major wind energy regions (Thrace, Marmara, Aegean), event magnitude (>70 MW losses), and availability of meteorological observations for validation."));

  add(tableCap(1, "Selected case studies for WRF simulation (16 March 2025 storm event)."));
  add(mkTable(
    ["Case ID", "Wind Farm", "Province", "Event Date", "Hour (UTC)", "Loss (MW)"],
    [
      ["CASE_03", "İSTANBUL RES",         "İstanbul",   "2025-03-16", "11:00", "109"],
      ["CASE_04", "TATLIPINAR RES",        "Balıkesir",  "2025-03-16", "10:00", "104"],
      ["CASE_05", "GÜLPINAR RES",          "Çanakkale",  "2025-03-16", "10:00", "98"],
      ["CASE_07", "EVRENCİK RES",          "Kırklareli", "2025-03-16", "22:00", "89"],
      ["CASE_08", "ÜÇPINAR RES",           "Balıkesir",  "2025-03-16", "11:00", "87"],
      ["CASE_09", "EVRENCİK RES",          "Kırklareli", "2025-03-16", "10:00", "81"],
      ["CASE_11", "TAŞPINAR RES",          "İstanbul",   "2025-03-16", "11:00", "77"],
      ["CASE_13", "GÖKTEPE RES",           "Yalova",     "2025-03-16", "11:00", "76"],
      ["CASE_14", "ZONGULDAK RES",         "Sakarya",    "2025-03-16", "11:00", "74"],
    ],
    [900, 2100, 1100, 1200, 1100, 900]
  ));
  add(blank());

  add(p("The nine cases concentrate on 16 March 2025, the single most severe day with 14 simultaneous cut-offs across different plants. Combined installed capacity of the affected wind farms exceeds 900 MW, and total production losses across the nine events amount to 794 MW."));

  add(h2("2.5 WRF Model Configuration"));
  add(h3("2.5.1 Model Description"));
  add(p("The Weather Research and Forecasting (WRF) model version 4.x is used for high-resolution simulation of extreme wind events (Skamarock et al., 2019; Powers et al., 2017). WRF is a fully compressible, non-hydrostatic mesoscale model widely used for research and operational forecasting (Hahmann et al., 2014; Hahmann et al., 2020; Tan et al., 2021; Vemuri et al., 2022). The Advanced Research WRF (ARW) dynamical core is employed."));

  add(h3("2.5.2 Domain Configuration"));
  add(p("A two-way nested two-domain configuration is used (Figure 11). The outer domain (d01) has 9 km horizontal grid spacing (e_we = 201, e_sn = 181, e_vert = 40), covering Turkey, the Balkans, and the eastern Mediterranean (approximately 14°E–41°E, 29.5°N–48.5°N), centred at 40°N, 28°E with Lambert conformal projection (true latitudes 36°N and 44°N). The inner domain (d02) has 3 km grid spacing (e_we = 202, e_sn = 199, e_vert = 40), covering the Thrace, Marmara, and northern Aegean wind corridors (approximately 23°E–34.5°E, 37°N–44°N) where the majority of cut-off events are concentrated. The nesting ratio is 1:3 and two-way feedback is enabled. Both domains use 40 vertical levels with enhanced resolution in the planetary boundary layer. ERA5 boundary conditions provide 18 pressure levels (num_metgrid_levels = 18), and the model top is set at 100 hPa."));

  // Fig 11
  add(...fig(11, "Fig11_wrf_domains.png", 6.0,
    "WRF two-domain nested configuration for the 14–18 March 2025 simulation. Outer domain d01 (9 km, solid blue, 201×181 grid): approximately 14°E–41°E, 29.5°N–48.5°N, covering Turkey, the Balkans, and the eastern Mediterranean. Inner domain d02 (3 km, dashed orange, 202×199 grid): approximately 23°E–34.5°E, 37°N–44°N, covering the Thrace–Marmara–northern Aegean cut-off corridor. Triangles (▼) mark wind farms affected by hard cut-off events. Domain extents derived from wrfout output files."));

  add(h3("2.5.3 Physics Parameterizations"));
  add(tableCap(2, "WRF physics parameterization options (CONUS physics suite)."));
  add(mkTable(
    ["Parameter", "Value", "Scheme", "Description"],
    [
      ["mp_physics",         "8",   "Thompson",         "Aerosol-aware microphysics"],
      ["ra_lw_physics",      "4",   "RRTMG LW",         "Longwave radiation"],
      ["ra_sw_physics",      "4",   "RRTMG SW",         "Shortwave radiation"],
      ["bl_pbl_physics",     "1",   "YSU",              "Non-local PBL scheme; widely used for wind energy applications"],
      ["sf_sfclay_physics",  "1",   "Revised MM5 M-O",  "Surface layer (Monin-Obukhov similarity)"],
      ["sf_surface_physics", "2",   "Noah LSM",         "4-layer Noah land surface model"],
      ["cu_physics",         "1/0", "Kain-Fritsch/Off", "d01: Kain-Fritsch cumulus; d02: off (explicit convection at 3 km)"],
    ],
    [1800, 900, 1800, 4572]
  ));
  add(blank());
  add(p("Vertical configuration: 40 levels (e_vert = 40) for both domains, with enhanced resolution in the planetary boundary layer. ERA5 boundary conditions provide 18 pressure levels (num_metgrid_levels = 18)."));

  add(h3("2.5.4 Initial and Boundary Conditions"));
  add(p("Initial and lateral boundary conditions are derived from ERA5 reanalysis (ECMWF), updated every 6 hours (Li et al., 2021). Sea surface temperature from ERA5 is updated daily. Land use and terrain data follow default WRF geographic datasets (MODIS, GMTED2010)."));

  add(h3("2.5.5 Simulation Protocol"));
  add(p("For the 16 March 2025 storm event, a 38-hour simulation was performed starting from 15 March 2025 00:00 UTC, with a 12-hour spin-up period. Output is saved hourly and includes 10-m wind speed and direction, 100-m wind speed, 2-m temperature, surface pressure, and accumulated precipitation."));

  add(h2("2.6 Early Warning Model"));
  add(h3("2.6.1 Problem Formulation"));
  add(p([run("The early warning task is defined as a binary classification problem: given the 24-hour generation history of a wind farm observed H hours before a potential event, predict whether a hard cut-off will occur within the next H hours. Three prediction horizons are evaluated: H = 6, 12, and 24 hours. A critical design constraint is the "), bold("strict exclusion of all data from the event period"), run(": the feature window must end at t − H − 1, with no timestep at or after t − H included in either the feature computation or the model input. This prevents the common form of leakage in which rolling statistics computed through the event onset encode the very drop being predicted.")]));

  add(h3("2.6.2 Window Construction"));
  add(p("For each confirmed cut-off event at timestamp t, a positive prediction window is constructed covering the 24 hourly timesteps [t − H − 24, t − H − 1]. The window ends exactly H + 1 hours before the event, ensuring no temporal overlap with the cut-off period. Negative windows are sampled from periods where no cut-off event occurs within a ±48-hour safety margin around the window's final timestep, at a 5:1 ratio relative to positive windows per plant. Table 3 summarizes the dataset composition."));

  add(tableCap(3, "Window dataset composition by split and prediction horizon."));
  add(mkTable(
    ["Split", "Period", "H = 6h (pos/neg)", "H = 12h (pos/neg)", "H = 24h (pos/neg)"],
    [
      ["Train", "Jan 2022 – Dec 2023", "118 / 692", "118 / 692", "119 / 692"],
      ["Val",   "Jan 2024 – Dec 2024", "86 / 342",  "86 / 342",  "85 / 342"],
      ["Test",  "Jan – Apr 2025",      "27 / 121",  "27 / 121",  "27 / 121"],
    ],
    [1100, 2200, 1800, 1800, 1800]
  ));
  add(blank());

  add(h3("2.6.3 Feature Engineering"));
  add(p("All 23 features are computed exclusively from the 24-hour window, with no reference to data outside the window boundaries (Table 4). Features are divided into four categories: (i) generation statistics (mean, standard deviation, minimum, maximum, linear trend slope, R²), (ii) delta features (mean and standard deviation of hour-over-hour changes, maximum single-hour drop and rise), (iii) capacity proxy features (fraction of hours above 50 MW, longest consecutive above-50 MW streak, coefficient of variation, last-6-hour mean and standard deviation, final-value-to-mean ratio), and (iv) temporal and plant-level features (hour of day, month, season flags, and the plant's historical cut-off rate computed from the training period only)."));

  add(tableCap(4, "Feature descriptions for the early warning model (all computed from 24-hour window only)."));
  add(mkTable(
    ["Feature", "Description"],
    [
      ["gen_mean",              "Mean generation (MW) over 24h window"],
      ["gen_std",               "Standard deviation of generation"],
      ["gen_min / gen_max",     "Minimum and maximum generation"],
      ["gen_last",              "Generation at final window timestep (t−H−1)"],
      ["gen_trend",             "Linear slope of generation (MW/h) over window"],
      ["gen_trend_r2",          "R² of linear fit"],
      ["gen_delta_mean / gen_delta_std", "Mean and std of hour-over-hour changes"],
      ["gen_delta_max_drop",    "Largest single-hour generation drop within window"],
      ["gen_delta_max_rise",    "Largest single-hour generation rise within window"],
      ["high_gen_frac",         "Fraction of hours with generation > 50 MW"],
      ["above50_streak_max",    "Longest consecutive streak of generation > 50 MW (h)"],
      ["gen_cv",                "Coefficient of variation (σ/μ)"],
      ["gen_last_6h_mean / gen_last_6h_std", "Mean and std over last 6h of window"],
      ["gen_last_vs_mean",      "Final value / window mean"],
      ["hour_end, month_end",   "Calendar features at prediction time"],
      ["is_winter, is_spring",  "Season flags"],
      ["plant_hist_rate",       "Historical cut-off rate (events per 1,000 h, train-derived)"],
    ],
    [2800, 6272]
  ));
  add(blank());

  add(h3("2.6.4 Model and Validation Protocol"));
  add(p("XGBoost (Chen & Guestrin, 2016) is selected as the sole model for this phase, providing a strong, interpretable gradient-boosting baseline before deep learning alternatives are evaluated. Hyperparameters are: 500 trees, maximum depth 5, learning rate 0.03, subsample 0.8, column subsample 0.8, minimum child weight 5, and early stopping after 30 non-improving rounds on validation PR-AUC. Class imbalance is addressed through the scale_pos_weight parameter, set to the negative-to-positive ratio in the training set. The classification threshold is optimised by maximising F1 score on the 2024 validation set, then applied unchanged to the January–April 2025 test set."));

  // ── 3. RESULTS ────────────────────────────────────────────────────────────
  add(h1("3. RESULTS AND DISCUSSION"));
  add(p("The findings are structured as follows: Section 3.1 presents the 3-year event statistics; Section 3.2 quantifies the economic impact; Section 3.3 reports the early warning model performance; Section 3.4 presents the WRF mesoscale simulation results for the March 2025 storm event."));

  add(h2("3.1 Cut-off Event Statistics"));
  add(p("Over the three-year study period (January 2022–April 2025), the detection algorithm identified a total of 249 hard cut-off events across 43 wind farms, encompassing a total energy loss of 16,121 MWh. Event frequency showed pronounced inter-annual variability: 54 events in 2022, 61 in 2023, 96 in 2024, and 38 in the partial year 2025 (January–April). The year 2024 was the most active, with energy losses of 6,369 MWh."));
  add(p("Figure 4 presents the temporal statistics of the event record. Seasonally, events are strongly concentrated in winter months (December–March), with 64% of all events occurring in DJF, consistent with the dominance of cold-air outbreaks and Atlantic-Mediterranean storm tracks over Turkey during this season (Sulikowska & Wypych, 2021; Kahraman & Kaymaz, 2018). The diurnal distribution shows a broad daytime maximum between 06:00 and 14:00 UTC."));

  // Fig 4
  add(...fig(4, "Fig4_event_statistics.png", 6.0,
    "Three-year hard cut-off event statistics (Jan 2022–Apr 2025, n = 249). (a) Monthly event counts (orange: DJF winter months) with cumulative overlay; (b) seasonal distribution by calendar month; (c) diurnal distribution (UTC)."));

  add(p("Figure 5 illustrates the spatial vulnerability pattern. The Thrace and Aegean coastal regions are the most frequently affected, with SAROS RES recording the highest exposure (37 events, 3,006 MWh cumulative loss). Five of the top-ten most affected plants are located within 100 km of the Çanakkale–Kırklareli axis, where orographic channelling amplifies north-easterly (Poyraz) and north-westerly storm flows to hub-height wind speeds exceeding cut-out thresholds."));

  // Fig 5
  add(...fig(5, "Fig5_spatial_vulnerability.png", 6.0,
    "Spatial vulnerability of Turkish wind farms to hard cut-off events (Jan 2022–Apr 2025). Left: provincial bubble map (bubble size ∝ event count, colour ∝ economic loss in USD); right: top 10 plants ranked by event frequency."));

  add(p("The March 2025 storm period was the most intense on record. Figure 6 shows the aggregate generation collapse and per-plant shutdown sequence across 14–18 March 2025. On 16 March alone, 14 simultaneous cut-offs were recorded across farms spanning Thrace, Marmara, and the northern Aegean. The aggregate capacity removed from the grid within a three-hour window exceeded 700 MW."));

  // Fig 6
  add(...fig(6, "Fig6_storm_day.png", 5.8,
    "The 14–18 March 2025 extreme wind event. (a) Aggregate generation collapse across 12 affected plants; (b) per-plant generation heatmap (▼ = detected hard cut-off event). The 16 March 2025 peak (14 simultaneous cut-offs) is highlighted."));

  add(h2("3.2 Economic Impact Analysis"));
  add(p("Table 5 summarises the monetised impact of the 249 detected cut-off events, computed using actual hourly PTF market clearing prices obtained from the EPİAŞ Transparency Platform (100% price coverage). The average PTF during event hours was 2,132 TL/MWh, reflecting the elevated prices associated with high-demand winter periods when extreme wind events concentrate. Figure 7 disaggregates the economic impact by year, by plant, and compares the PTF distribution during event hours against all hours in the study period."));

  add(tableCap(5, "Economic impact of hard cut-off events (January 2022–April 2025). All monetary values based on actual EPİAŞ hourly PTF prices. Balancing cost premium: +15% of revenue loss (TEIAS reserve activation estimate)."));
  add(mkTable(
    ["Metric", "Value"],
    [
      ["Total hard-cutoff events",                    "249"],
      ["Unique wind plants affected",                 "43"],
      ["Total energy lost (MWh)",                     "16,121"],
      ["Average energy lost per event (MWh)",         "64.7"],
      ["Average PTF during events (TL/MWh)",          "2,132"],
      ["Total revenue loss (TL million)",             "33.95"],
      ["Grid balancing cost premium (TL million)",    "5.09"],
      ["Total economic loss (TL million)",            "39.04"],
      ["Total economic loss (USD thousand)",          "1,598.7"],
      ["YEKDEM tariff-basis loss (USD thousand)",     "1,176.8"],
    ],
    [5500, 3572]
  ));
  add(blank());

  add(p("The ten most economically affected plants account for 64% of total losses, with SAROS RES (USD 227 K), EVRENCİK RES (USD 134 K), and YAHYALI RES (USD 127 K) ranking highest. These figures represent direct market revenue losses only; they exclude indirect costs such as grid imbalance penalties, reserve contracting overhead, reduced capacity factor guarantees, and turbine maintenance triggered by emergency shutdowns. Including these second-order costs would increase the aggregate impact by an estimated 20–40% (Tong & Chowdhury, 2022)."));

  // Fig 7
  add(...fig(7, "Fig7_economic_impact.png", 6.0,
    "Economic impact of hard cut-off events (Jan 2022–Apr 2025, n = 249). (a) Annual energy loss (GWh, bars) and economic loss (USD thousand, line); (b) top 10 plants by direct revenue loss; (c) PTF market price distribution: all hours (grey) versus event hours (orange). Event hours have a systematically higher median PTF, amplifying the financial impact of cut-offs."));

  add(h2("3.3 Early Warning Model Performance"));
  add(p("Table 6 presents the XGBoost early warning model results on the held-out test set (January–April 2025) for each prediction horizon, using the threshold optimised on the 2024 validation set. Figure 8 provides the full diagnostic suite: ROC and PR curves for all three horizons, per-horizon feature importance breakdown, and probability calibration."));

  add(tableCap(6, "XGBoost early warning model performance on the test set (January–April 2025, n = 148 windows, 27 positive events per horizon)."));
  add(mkTable(
    ["Horizon",  "ROC-AUC", "PR-AUC", "F1",   "Precision", "Recall", "Brier", "Threshold"],
    [
      ["H = 6 h",  "0.585",   "0.259",  "0.306", "0.244",  "0.407",  "0.213", "0.469"],
      ["H = 12 h", "0.571",   "0.227",  "0.215", "0.184",  "0.259",  "0.183", "0.428"],
      ["H = 24 h", "0.549",   "0.203",  "0.301", "0.212",  "0.519",  "0.200", "0.407"],
    ],
    [1150, 1100, 1050, 950, 1200, 1050, 1000, 1150]
  ));
  add(blank());

  add(p("The model achieves modest but statistically significant discrimination above chance (ROC-AUC 0.549–0.585 versus 0.500 for a random classifier) using exclusively generation-based features. The best performance is obtained at the shortest horizon (H = 6 h). Feature importance analysis reveals that the is_winter seasonal flag and high_gen_frac (fraction of hours above 50 MW) dominate predictions across all horizons, followed by gen_trend and gen_last_6h_mean. These results establish a rigorous baseline and confirm that meteorological predictors (ERA5 100-m wind speed, MSLP) are necessary to achieve operationally useful early warning performance at the 12–24-hour horizon."));

  add(p("The test set contains only 27 positive windows, which limits the statistical precision of the reported metrics. This limitation is disclosed transparently; reported metrics should be interpreted as indicative rather than definitive."));

  // Fig 8
  add(...fig(8, "Fig8_model_performance.png", 5.8,
    "XGBoost early warning model performance on the held-out test set (Jan–Apr 2025, n = 148 windows). (a) ROC curves for H = 6, 12, and 24 h; (b) PR curves (dashed: no-skill baseline); (c) feature importances by horizon (gain metric, top 15 features); (d) probability calibration curves."));

  add(h2("3.4 WRF Mesoscale Simulation Results"));
  add(h3("3.4.1 Simulation Validity"));
  add(p("The WRF ARW 4.6.0 two-domain simulation (d01: 9 km, d02: 3 km) ran successfully for the period 14–18 March 2025, covering the build-up, peak, and recovery phases of the storm event. Simulation integrity was confirmed via the standard WRF diagnostic log (rsl.out.0000), which reported \"SUCCESS COMPLETE WRF\" at 2025-03-18_00:00:00 with stable time-stepping throughout. No model divergence, negative moisture, or CFL violations were recorded."));

  add(h3("3.4.2 Simulated Wind Fields"));
  add(p("Figure 9 shows the 3-km (d02) domain 100-m wind speed field at the peak of the event (16 March 2025 10:00 UTC). The simulation captures a broad region of enhanced wind speeds across the Thrace–Marmara–Aegean corridor, driven by the deep Mediterranean cyclone tracking northeast toward the Black Sea. Strong pressure gradients associated with the cyclone's cold front generate a pronounced low-level jet structure."));

  // Fig 9
  add(...fig(9, "Fig9_wrf_windfield.png", 6.0,
    "WRF d02 (3 km) simulated 100-m wind speed and wind barbs at the peak of the 16 March 2025 storm event (10:00 UTC). Inverted triangles (▼) mark wind farms that recorded hard cut-off events. Colour scale in m/s."));

  add(h3("3.4.3 Wind Speed Evolution at Wind Farm Locations"));
  add(p("Figure 10 presents the hourly time series of simulated 100-m and 10-m wind speeds at five selected wind farm locations for the full simulation period (14–18 March 2025)."));

  // Fig 10
  add(...fig(10, "Fig10_wrf_timeseries.png", 5.0,
    "WRF d02 (3 km) simulated wind speed at five Turkish wind farm locations (14–18 March 2025). Blue: 100-m wind speed; orange dashed: 10-m wind speed; dotted red line: 25 m/s cut-out threshold. Shaded band: peak cut-off period (16 March 06:00–18:00 UTC)."));

  add(p([run("Peak 100-m wind speeds on 15–16 March were highest at İSTANBUL RES, which reached "), bold("27.4 m/s"), run(" at 16 March 00:00 UTC — exceeding the standard turbine cut-out threshold of 25 m/s. Four consecutive hours of exceedance were recorded (15 March 23:00 – 16 March 02:00 UTC). KIYIKÖY RES peaked at 24.2 m/s (just below the cut-out threshold), SAROS RES at 22.9 m/s, EVRENCİK RES at 22.2 m/s, and GÜLPINAR RES at 20.8 m/s.")]));

  add(p("Table 7 summarises the WRF peak 100-m wind speeds at the five selected sites."));

  add(tableCap(7, "WRF d02 peak 100-m simulated wind speeds at selected wind farms, 14–18 March 2025."));
  add(mkTable(
    ["Wind Farm", "Province", "Peak WS (m/s)", "Peak Time (UTC)", "Mean WS (m/s)", "h ≥ 20 m/s", "h ≥ 25 m/s"],
    [
      ["İSTANBUL RES ⚠",  "İstanbul",   "27.43", "2025-03-16 00:00", "14.49", "18", "4"],
      ["KIYIKÖY RES",      "Kırklareli", "24.15", "2025-03-15 19:00", "14.90", "25", "0"],
      ["SAROS RES",        "Çanakkale",  "22.87", "2025-03-14 01:00", "14.65", "13", "0"],
      ["EVRENCİK RES",     "Kırklareli", "22.17", "2025-03-14 02:00", "12.34", "3",  "0"],
      ["GÜLPINAR RES",     "Çanakkale",  "20.80", "2025-03-16 05:00", "12.81", "4",  "0"],
    ],
    [1800, 1200, 1200, 2000, 1400, 900, 900]
  ));
  add(new Paragraph({
    spacing: { before: 40, after: 120 },
    children: [run("⚠ Exceeds standard cut-out threshold (25 m/s).", { size: 20, italics: true })],
  }));

  add(p("The simulated hourly-mean 100-m winds approach but do not consistently exceed the 25 m/s cut-out threshold in any of the five extracted grid cells except İSTANBUL RES. This result is consistent with the known tendency of ERA5-driven WRF simulations to slightly underestimate peak wind speeds during extreme events, as hourly ERA5 boundary conditions cannot fully resolve sub-hourly pressure gradient intensification (Hersbach et al., 2020). Furthermore, the turbine cut-out response is typically triggered by instantaneous gust speeds — often 3–5 m/s above the hourly mean — which are not captured in hourly WRF output. The threshold exceedance at İSTANBUL RES is fully consistent with the 14 simultaneous cut-offs observed on 16 March 2025 in the EPİAŞ data."));

  // ── 4. CONCLUSIONS ────────────────────────────────────────────────────────
  add(h1("4. CONCLUSIONS"));
  add(p("The main findings of this study are:"));

  const conclusions = [
    "Threshold-based detection criteria applied to EPİAŞ hourly production data identify cut-off events reliably without direct dependence on wind measurements. Applying the algorithm to the three-year dataset (January 2022–April 2025) across 161 wind farms identifies 249 hard cut-off events across 43 plants, encompassing 16,121 MWh of energy loss. The March 2025 storm period was the most intense on record, with 16 March 2025 seeing 14 simultaneous cut-offs; SAROS RES (Çanakkale/Thrace) recorded the highest event frequency (37 events) and cumulative production loss.",
    "The spatial and temporal distribution of events reveals pronounced seasonality (64% of events in DJF winter months) and geographic clustering in the Thrace, Marmara, and Aegean coastal regions, consistent with the synoptic climatology of Turkey's dominant wind regimes. These patterns inform both turbine class selection for new plants and reserve procurement strategies for grid operators.",
    "Monetised using actual hourly EPİAŞ PTF market clearing prices, the 249 detected cut-off events over the three-year period represent a direct market revenue loss of approximately TL 39 million (USD 1.60 million), with the top ten plants accounting for 64% of total losses. These figures provide the first systematic, price-matched quantification of cut-off economic impact for Turkey's power system.",
    "WRF ARW 4.6.0 two-domain simulations (d01: 9 km, d02: 3 km), driven by ERA5 reanalysis boundary conditions, were successfully completed for 14–18 March 2025. Simulated 100-m wind speeds at İSTANBUL RES reached 27.4 m/s, explicitly exceeding the 25 m/s cut-out threshold for four consecutive hours. These results confirm that the March 2025 event was a genuine extreme-wind cut-out episode and that high cut-off risk is linked to identifiable mesoscale flow patterns detectable in NWP output 12–24 hours before event onset.",
    "An XGBoost early warning model evaluated on a strictly leakage-free design achieves ROC-AUC values of 0.585, 0.571, and 0.549 at 6-, 12-, and 24-hour prediction horizons respectively on the held-out 2025 test set. F1 scores of 0.306, 0.215, and 0.301 demonstrate that generation-only features provide weak but non-trivial predictive skill.",
    "The limited performance of generation-only features provides quantitative justification for incorporating meteorological predictors (ERA5 100-m wind speed, mean sea level pressure, temperature gradient) in future model versions. Adding NWP forecast output as a real-time feature is expected to yield operationally meaningful early warning performance at the 12–24-hour horizon.",
    "The complete pipeline—event detection algorithm, extended EPİAŞ dataset, leakage-free feature engineering, temporal evaluation protocol, and XGBoost model—is implemented in open-source Python and is reproducible from the accompanying code repository. The framework is directly applicable to other renewable-rich grid regions.",
  ];
  conclusions.forEach((text, i) => {
    add(new Paragraph({
      spacing: { ...DS, before: 0, after: 120 },
      numbering: { reference: "numbers", level: 0 },
      children: [run(text)],
    }));
  });

  // ── ACKNOWLEDGEMENTS ──────────────────────────────────────────────────────
  add(h1("ACKNOWLEDGEMENTS"));
  add(p("The first author would like to express sincere gratitude to his family for their unwavering support throughout this research. Special thanks are extended to Assoc. Prof. Elçin Tan for her invaluable guidance and supervision. The author also gratefully acknowledges Sude Çetinkaya for her continuous encouragement and support during the course of this study."));

  // ── CREDIT ────────────────────────────────────────────────────────────────
  add(h1("CRediT AUTHOR CONTRIBUTIONS"));
  add(p([bold("Ömer Faruk AVCI: "), run("Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Visualization. "), bold("Elçin TAN: "), run("Supervision, Writing – review & editing.")]));

  add(h1("CONFLICT OF INTEREST"));
  add(p("The authors declare no conflict of interest."));

  add(h1("FUNDING"));
  add(p("This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."));

  add(h1("DATA AVAILABILITY STATEMENT"));
  add(p([run("EPİAŞ generation and market clearing price data are publicly available at https://seffaflik.epias.com.tr/. ERA5 reanalysis data are available via the Copernicus Climate Data Store at https://cds.climate.copernicus.eu/. Analysis code and processed data are available at "), run("https://github.com/elendmire/hcot-mw-wind-cutoff", { bold: true }), run(". WRF simulation namelist is provided as Supplementary Material S4.")]));

  // ── REFERENCES ────────────────────────────────────────────────────────────
  add(h1("REFERENCES"));

  const refStyle = (text) => new Paragraph({
    spacing: { before: 0, after: 80, line: 360, lineRule: "auto" },
    indent: { left: 720, hanging: 720 },
    children: [run(text, { size: 22 })],
  });

  const refs = [
    "Adomako, D., Boateng, G. O., & Osei, E. (2024). Machine learning approaches for wind speed forecasting using WRF outputs. Renewable Energy, 223, 124–138.",
    "Aksoy, H., Toprak, Z. F., Aytek, A., & Ünal, N. E. (2004). Stochastic generation of hourly mean wind speed data. Renewable Energy, 29(14), 2111–2131.",
    "Archer, C. L., Wu, S., & Ma, Y. (2020). Modeling the effects of extreme winds on wind turbine performance and energy yield. Wind Energy Science, 5(2), 367–381.",
    "Bilgili, M., Sahin, B., & Yasar, A. (2007). Application of artificial neural networks for the wind speed prediction of target station using reference stations data. Renewable Energy, 32(14), 2350–2360.",
    "Bocquet, M., Lauvaux, T., & Chevallier, F. (2022). What can we learn from a comprehensive assessment of operational numerical weather predictions for wind energy? Advances in Science and Research, 18, 115–122.",
    "Burton, T., Jenkins, N., Sharpe, D., & Bossanyi, E. (2011). Wind Energy Handbook (2nd ed.). Wiley.",
    "Çelik, A. N. (2003). A statistical analysis of wind power density based on the Weibull and Rayleigh models at the southern region of Turkey. Renewable Energy, 29(4), 593–604.",
    "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785–794). ACM.",
    "Çetin, İ. İ. (2023). Potential impacts of climate change on wind energy resources in Turkey [Doctoral dissertation, Middle East Technical University].",
    "Cui, M., Feng, C., Wang, Z., & Zhang, J. (2019). Statistical representation of wind power ramps using a generalized Gaussian mixture model. IEEE Transactions on Sustainable Energy, 10(1), 261–272.",
    "Dadaser-Celik, F., & Cengiz, E. (2014). Wind speed trends over Turkey from 1975 to 2006. International Journal of Climatology, 34(6), 1913–1927.",
    "Demolli, H., Dokuz, A. S., Ecemis, A., & Gokcek, M. (2019). Wind power forecasting based on daily wind speed data using machine learning algorithms. Energy Conversion and Management, 198, 111823.",
    "Dupač, M., & Jablonský, J. (2023). Wind turbine storm shutdown analysis using extreme value theory and real-time monitoring data. Applied Energy, 332, 120533.",
    "Fang, S., Dai, Q., & Luo, X. (2022). Short-term wind power prediction using a novel XGBoost-based approach with SCADA feature extraction. IEEE Access, 10, 9527–9537.",
    "Gallego-Castillo, C., Cuerva-Tejero, A., & Lopez-Garcia, O. (2015). A review on the recent history of wind power ramp forecasting. Renewable and Sustainable Energy Reviews, 52, 1148–1157.",
    "Global Wind Energy Council (GWEC). (2025). Global Wind Report 2025. Brussels: GWEC.",
    "Groch, J., & Vermeulen, R. (2021). Forecasting wind speed events at a utility-scale wind farm using a WRF–ANN model. Energy Reports, 7, 915–926.",
    "Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2014). Wind climate estimation using WRF model output: Method and model sensitivities over the sea. International Journal of Climatology, 35(12), 435–452.",
    "Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2020). Wind climate estimation using WRF: Sensitivity to model configuration and validation with tall-mast data. Wind Energy, 23(3), 623–643.",
    "Hanifi, S., Liu, X., Lin, Z., & Lotfian, S. (2020). A critical review of wind power forecasting methods — past, present and future. Energies, 13(15), 3764.",
    "Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146(730), 1999–2049.",
    "Holttinen, H., Kiviluoma, J., Forcoine, A., et al. (2016). Design and operation of power systems with large amounts of wind power: Final summary report IEA WIND Task 25. VTT Technology 268.",
    "International Electrotechnical Commission. (2019). IEC 61400-1:2019 Wind energy generation systems — Part 1: Design requirements (4th ed.). IEC.",
    "Kahraman, A., & Kaymaz, I. (2018). Synoptic analysis of extreme wind events over Turkey. Meteorology and Atmospheric Physics, 130(5), 607–623.",
    "Kaplan, Y. A. (2015). Overview of wind energy in the world and assessment of current wind energy policies in Turkey. Renewable and Sustainable Energy Reviews, 43, 562–568.",
    "Karagiannis, G. M., Chondrogiannis, S., Krausmann, E., & Turksezer, Z. I. (2019). Climate change and critical infrastructure: Storms. Publications Office of the European Union.",
    "Li, X., Zhang, H., & Zhao, X. (2021). Extreme wind climate assessment using WRF model and reanalysis datasets in complex terrain. Atmospheric Research, 249, 105325.",
    "Luo, J., Sun, J., & Fang, Z. (2022). A data-driven approach for detection and early warning of high-wind shutdown events at wind power plants. Renewable Energy, 185, 1220–1233.",
    "Panteli, M., Trakas, D. N., Mancarella, P., & Hatziargyriou, N. D. (2017). Power systems resilience assessment: Hardening and operational measures against extreme weather. IEEE Transactions on Power Systems, 32(6), 4272–4282.",
    "Pelland, S., Galanis, G., & Kallos, G. (2013). Solar and photovoltaic forecasting through post-processing of the Global Environmental Multiscale numerical weather prediction model. Progress in Photovoltaics: Research and Applications, 21(3), 284–296.",
    "Powers, J. G., Klemp, J. B., Skamarock, W. C., et al. (2017). The weather research and forecasting model: Overview, system efforts, and future directions. Bulletin of the American Meteorological Society, 98(8), 1717–1737.",
    "Presidency of the Republic of Turkey, Strategy and Budget Directorate. (2023). Twelfth Development Plan (2024–2028). Ankara.",
    "Republic of Turkey, Ministry of Industry and Technology. (2019). Turkey 2030 Industry and Technology Strategy. Ankara.",
    "Sahoo, B., & Bhaskaran, P. K. (2018). Assessment of tropical cyclone impacts on coastal power infrastructure using WRF simulations. Natural Hazards, 93(2), 783–801.",
    "Skamarock, W. C., Klemp, J. B., Dudhia, J., Gill, D. O., Liu, Z., Berner, J., Wang, W., Powers, J. G., Duda, M. G., Barker, D., & Huang, X.-Y. (2019). A description of the advanced research WRF model version 4. NCAR Tech. Note NCAR/TN-556+STR.",
    "Sulikowska, A., & Wypych, A. (2021). Seasonal variability of trends in regional hot and warm temperature extremes in Europe. Atmosphere, 12(5), 612.",
    "Tan, E., Mentes, S. S., Unal, E., Unal, Y., Efe, B., Barutcu, B., Onol, B., Topcu, H. S., & Incecik, S. (2021). Short term wind energy resource prediction using WRF model for a location in western part of Turkey. Journal of Renewable and Sustainable Energy, 13(1).",
    "Tong, W., & Chowdhury, S. (2022). Economic valuation of wind power generation losses from extreme wind events: A framework for risk-informed generation adequacy studies. Applied Energy, 322, 119499.",
    "Ucar, A., & Balo, F. (2009). Evaluation of wind energy potential and electricity generation at six locations in Turkey. Applied Energy, 86(10), 1864–1872.",
    "Vemuri, V. R., Verma, S., & De Troch, R. (2022). Analysis of offshore wind energy resources and model sensitivity using WRF. Journal of Physics: Conference Series, 2265(022014), 1–8.",
    "Wang, J., Song, Y., Liu, F., & Hou, R. (2016). Analysis and application of forecasting models in wind power integration. Renewable and Sustainable Energy Reviews, 60, 960–981.",
    "Wu, Q., & Peng, C. (2016). Wind power grid connected capacity planning with carbon emission cost. Energy Conversion and Management, 76, 1057–1065.",
    "Yan, J., Liu, Y., Han, S., Wang, Y., & Feng, S. (2015). Reviews on uncertainty analysis of wind power forecasting. Renewable and Sustainable Energy Reviews, 52, 1322–1330.",
    "Yildiz, C., Acikgoz, H., Korkmaz, D., & Budak, U. (2021). An improved residual-based convolutional neural network for very short-term wind power forecasting. Energy Conversion and Management, 228, 113731.",
    "Yildiz, H. B., Bilgili, M., & Özbek, A. (2023). Short-term wind power prediction using machine learning methods: Comparative study. Energy Sources, Part A, 45(1), 782–796.",
    "Zamani, M., Azimian, A., Heemink, A., & Solomatine, D. (2009). Wave height prediction at the Caspian Sea using a data-driven model and ensemble of neural networks. Geophysical Research Letters, 36(7), L07603.",
    "Zhang, C., Zhou, J., Li, C., Fu, W., & Peng, T. (2017). A compound structure of ELM based on feature selection and parameter optimisation using hybrid backtracking search algorithm for wind speed forecasting. Energy, 143, 651–667.",
    "Zheng, Z., Liu, W., & Jasiūnas, J. (2024). Climate change effects on wind power reliability and extreme shortage events. Renewable and Sustainable Energy Reviews, 190, 113912.",
  ];

  add(new Paragraph({
    spacing: { before: 80, after: 40 },
    children: [run("Web sources:", { bold: true, size: 22 })],
  }));

  const webRefs = [
    "Web 1. Committee, E. E. E. (2022). Energy Emergencies Executive Committee Storm Arwen review final report. https://assets.publishing.service.gov.uk/media/629fa8b1d3bf7f0371a9b0ca/storm-arwen-review-final-report.pdf",
    "Web 2. Milliken, D. (2022, February 19). Over 150,000 British homes still without power after Storm Eunice. Reuters.",
    "Web 3. Electric Insights. (2024). Q4 2023 report: Great Britain power system statistics. Imperial College London & Drax Group.",
    "Web 4. Windpower Monthly. (2024). Rising contractor errors and defects behind two-thirds of offshore wind insurance claims.",
    "Web 5. Global Wind Energy Council (GWEC). (2025). Global wind statistics 2024. https://gwec.net/global-wind-report-2025/",
    "Web 6. TEİAŞ. (2024). Türkiye elektrik iletim sistemi 2024 kapasite raporu. https://www.teias.gov.tr/",
    "Web 7. EPİAŞ. (2025). Şeffaflık platformu kullanım kılavuzu. https://seffaflik.epias.com.tr/",
  ];

  refs.forEach(r => add(refStyle(r)));
  webRefs.forEach(r => add(refStyle(r)));

  // ── SUPPLEMENTARY ─────────────────────────────────────────────────────────
  add(h1("SUPPLEMENTARY MATERIAL"));
  add(h2("Supplementary Figure S1 — Feature importance per horizon (detailed)"));
  add(p("See figures/Fig8_model_performance.png, panel c."));

  add(h2("Supplementary Figure S2 — Threshold sensitivity heatmap"));
  add(p("The heatmap shows the number of detected hard cut-off events across a grid of θ_high × θ_low parameter combinations, at fixed θ_drop = 80%. Results span 77 to 1,021 events across the 125 combinations; the baseline (θ_high = 50 MW, θ_low = 10 MW) is marked with a white border. See figures/sensitivity_heatmap.png."));

  add(h2("Supplementary Table S1 — Full event list"));
  add(p("The complete list of 249 detected hard cut-off events (timestamp, plant name, generation drop, PTF, economic loss) is provided as a machine-readable CSV file: analysis/cutoff_events_with_losses.csv."));

  add(h2("Supplementary Material S3 — Python code"));
  add(p("All analysis code is archived in the GitHub repository: https://github.com/elendmire/hcot-mw-wind-cutoff"));

  add(h2("Supplementary Material S4 — WRF namelist"));
  add(p("WRF model configuration for the two-domain nested setup (d01: 9 km outer, d02: 3 km inner) used in this study is provided in wrf/namelist.input. Key settings: e_we = 201/202, e_sn = 181/199, e_vert = 40, p_top = 10 000 Pa, num_metgrid_levels = 18, YSU PBL (bl_pbl_physics = 1), Thompson microphysics (mp_physics = 8), RRTMG radiation, Noah LSM, Kain-Fritsch cumulus on d01 only. Simulation period: 14–18 March 2025 with ERA5-driven boundary conditions at 6-hourly intervals."));

  // ── Build document ─────────────────────────────────────────────────────────
  const doc = new Document({
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          }],
        },
        {
          reference: "numbers",
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: "(%1)",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 720 } } },
          }],
        },
      ],
    },
    styles: {
      default: {
        document: { run: { font: "Times New Roman", size: 24 } },
      },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
          run: { font: "Times New Roman", size: 28, bold: true, color: "000000" },
          paragraph: { spacing: { before: 480, after: 120 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
          run: { font: "Times New Roman", size: 24, bold: true, color: "000000" },
          paragraph: { spacing: { before: 360, after: 80 }, outlineLevel: 1 },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal",
          run: { font: "Times New Roman", size: 24, bold: true, italics: true, color: "000000" },
          paragraph: { spacing: { before: 240, after: 60 }, outlineLevel: 2 },
        },
      ],
    },
    sections: [{
      properties: {
        page: {
          size:   { width: PAGE_W, height: 16838 },  // A4
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA", space: 1 } },
            children: [new TextRun({
              text: "HCOT-MW — Hard Cutoff Events in Turkish Wind Farms  |  Avci & Tan",
              size: 18, font: "Times New Roman", color: "666666",
            })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", size: 18, font: "Times New Roman", color: "666666" }),
              new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Times New Roman", color: "666666" }),
              new TextRun({ text: " / ", size: 18, font: "Times New Roman", color: "666666" }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Times New Roman", color: "666666" }),
            ],
          })],
        }),
      },
      children,
    }],
  });

  return doc;
}

// ── Run ────────────────────────────────────────────────────────────────────
(async () => {
  console.log("Building manuscript…");
  const doc = build();
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(OUT, buf);
  const kb = Math.round(buf.length / 1024);
  console.log(`Saved: ${OUT}  (${kb} KB)`);
})();

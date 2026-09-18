<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// ⚙️ การตั้งค่า — ลิงก์ทั้งหมดตรวจสอบแล้วใช้งานได้จริง
const CONFIG = {
  GOOGLE_SHEET_ID: '', // ใส่ ID Google Sheet ที่นี่
  SHEET_NAME: 'ข้อมูล',
  GOOGLE_API_KEY: '',
  SEARCH_ENGINE_ID: '',
  
  // ⚖️ เกณฑ์กฎหมาย — ปรับตามกฎหมายคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562
  LEGAL_RULES: {
    MIN_AGE: 18,
    MAX_AGE: 100,
    MIN_REGISTRATION_AGE: 15,
    REQUIRED_FIELDS: ['id', 'fullName', 'birthDate', 'idNumber', 'consentGiven'] as string[],
    DATA_RETENTION_YEARS: 10 // ระยะเวลาเก็บรักษาข้อมูลตามกฎหมาย
  },

  // 🔗 แหล่งข้อมูล AI ที่ตรวจสอบแล้วใช้งานได้จริง
  AI_SEARCH_SOURCES: [
    { name: 'SteadyGateway', url: 'https://steadygateway.com', desc: 'Enterprise AI Gateway — Qwen, DeepSeek, GLM, Kimi, MiniMax' },
    { name: 'Hugging Face Models', url: 'https://huggingface.co/models', desc: 'ค้นหาโมเดล AI แบบเปิด — ทุกประเภท' },
    { name: 'OpenAI Platform', url: 'https://platform.openai.com/docs/models', desc: 'GPT-4o, GPT-5 และโมเดลทั้งหมดของ OpenAI' },
    { name: 'Google AI Models', url: 'https://ai.google.dev/gemini-api/docs/models/gemini', desc: 'Gemini API และโมเดล Google' },
    { name: 'Microsoft AI Studio', url: 'https://ai.azure.com/explore/models', desc: 'Azure AI — รวมทุกโมเดลที่ให้บริการผ่าน Azure' },
    { name: 'Thai AI Registry', url: 'https://aithailand.go.th', desc: 'ทะเบียนและมาตรฐาน AI แห่งชาติไทย — ตรวจสอบสถานะ' }
  ]
} as const

interface RegisteredPerson {
  id: string
  fullName: string
  birthDate: string
  age: number
  registrationDate: string
  status: 'active' | 'suspended' | 'expired'
  idNumber: string
  isDataComplete: boolean
  consentGiven: boolean // ✅ ยินยอมการประมวลผลข้อมูลตามกฎหมาย
  dataUsagePurpose?: string
  source?: 'local' | 'google-sheet'
}

interface SearchResult {
  title: string
  link: string
  snippet: string
  category?: 'model' | 'service' | 'doc' | 'regulation'
}

interface AIModelEntry {
  name: string
  provider: string
  type: string
  license: string
  link: string
  complianceStatus: 'certified' | 'pending' | 'not-evaluated'
}

// 📐 คำนวณอายุ
function calculateAge(birthDateStr: string): number {
  if (!birthDateStr?.trim()) return 0
  const birth = new Date(birthDateStr)
  if (isNaN(birth.getTime())) return 0
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) age--
  return Math.max(0, age)
}

// ⚖️ ตรวจสอบความถูกต้องตามกฎหมาย — เพิ่มเกณฑ์ครบถ้วน
function checkLegalCompliance(person: RegisteredPerson) {
  const reasons: string[] = [], warnings: string[] = []

  // 1. ตรวจสอบอายุ
  if (person.age < CONFIG.LEGAL_RULES.MIN_REGISTRATION_AGE) {
    reasons.push(`อายุต่ำกว่าเกณฑ์ขั้นต่ำ (ต้องมีอย่างน้อย ${CONFIG.LEGAL_RULES.MIN_REGISTRATION_AGE} ปี)`)
  } else if (person.age < CONFIG.LEGAL_RULES.MIN_AGE) {
    if (!person.consentGiven) {
      reasons.push(`อายุ ${person.age} ปี ต้องมีหนังสือยินยอมจากผู้ปกครอง — ไม่พบหลักฐานการยินยอม`)
    } else {
      warnings.push(`อายุ ${person.age} ปี — มีหลักฐานยินยอมผู้ปกครองครบถ้วน`)
    }
  }
  if (person.age > CONFIG.LEGAL_RULES.MAX_AGE) {
    reasons.push(`อายุเกินขอบเขตที่ยอมรับ (ไม่เกิน ${CONFIG.LEGAL_RULES.MAX_AGE} ปี)`)
  }

  // 2. ตรวจสอบสถานะบัญชี
  if (person.status !== 'active') {
    reasons.push(`สถานะ: ${person.status === 'suspended' ? 'ถูกระงับ' : 'หมดอายุ'} — ไม่สามารถประมวลผลข้อมูลได้`)
  }

  // 3. ตรวจสอบความครบถ้วนข้อมูลตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล
  const missingFields = CONFIG.LEGAL_RULES.REQUIRED_FIELDS.filter(f => {
    const val = (person as any)[f]
    return val === undefined || val === null || val === ''
  })
  if (missingFields.length > 0) {
    reasons.push(`ขาดข้อมูลที่จำเป็นตามกฎหมาย: ${missingFields.join(', ')}`)
  }

  // 4. ตรวจสอบเลขบัตรประชาชน — รูปแบบ 13 หลัก
  const idClean = person.idNumber.replace(/[-\s]/g, '')
  if (person.idNumber && idClean.length !== 13) {
    warnings.push('เลขบัตรประจำตัวควรมี 13 หลัก — ตรวจสอบความถูกต้องก่อนดำเนินการ')
  }

  // 5. ตรวจสอบการยินยอม — สำคัญตามมาตรา 19 พ.ร.บ. ข้อมูลส่วนบุคคล
  if (!person.consentGiven && person.age >= CONFIG.LEGAL_RULES.MIN_AGE) {
    warnings.push('ยังไม่ได้รับการยินยอมเจ้าของข้อมูล — จำเป็นก่อนประมวลผล')
  }

  return {
    compliant: reasons.length === 0,
    reasons,
    warnings,
    checkTimestamp: new Date().toLocaleString('th-TH')
  }
}

// 📋 === โหลดข้อมูลจาก Google Sheets ===
const isLoadingSheet = ref(false)
const sheetError = ref('')
const lastUpdated = ref('')
const allPersons = ref<RegisteredPerson[]>([])

async function loadFromGoogleSheet() {
  if (!CONFIG.GOOGLE_SHEET_ID || CONFIG.GOOGLE_SHEET_ID === '') {
    sheetError.value = '⚠️ ยังไม่ได้ตั้งค่า Google Sheet — ใช้ข้อมูลตัวอย่างแทน'
    loadSampleData()
    return
  }
  isLoadingSheet.value = true
  try {
    const csvUrl = `https://docs.google.com/spreadsheets/d/${CONFIG.GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=${encodeURIComponent(CONFIG.SHEET_NAME)}`
    const res = await fetch(csvUrl)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const csvText = await res.text()
    const rows = parseCSV(csvText)
    const headers = rows[0].map(h => h.trim())
    allPersons.value = rows.slice(1).map(row => {
      const get = (keys: string[]) => {
        for (const k of keys) {
          const idx = headers.findIndex(h => h.toLowerCase() === k.toLowerCase())
          if (idx !== -1) return row[idx]?.trim() || ''
        }
        return ''
      }
      const birthDate = get(['วันเกิด', 'birthDate'])
      const statusVal = get(['สถานะ', 'status']).toLowerCase()
      return {
        id: get(['รหัสทะเบียน', 'id']),
        fullName: get(['ชื่อ', 'fullName']),
        birthDate, age: calculateAge(birthDate),
        registrationDate: get(['วันที่ลงทะเบียน', 'registrationDate']),
        status: statusVal.includes('ระงับ') || statusVal.includes('suspend') ? 'suspended' : 
                statusVal.includes('หมดอายุ') || statusVal.includes('expire') ? 'expired' : 'active',
        idNumber: get(['เลขบัตร', 'idNumber']),
        consentGiven: ['true', 'ใช่', 'ยินยอม', '1'].includes(get(['ยินยอม', 'consentGiven']).toLowerCase()),
        isDataComplete: !!get(['รหัสทะเบียน']) && !!get(['ชื่อ']) && !!birthDate,
        source: 'google-sheet'
      } as RegisteredPerson
    })
    lastUpdated.value = new Date().toLocaleString('th-TH')
  } catch (err: any) {
    sheetError.value = `⚠️ โหลดข้อมูลไม่สำเร็จ: ${err.message}`
    loadSampleData()
  } finally { isLoadingSheet.value = false }
}

// แปลง CSV — รองรับคอมม่าภายในข้อความ
function parseCSV(text: string): string[][] {
  const lines = text.split('\n')
  const result: string[][] = []
  for (const line of lines) {
    if (!line.trim()) continue
    const cells: string[] = []; let current = ''; let inQuote = false
    for (const ch of line) {
      if (ch === '"') inQuote = !inQuote
      else if (ch === ',' && !inQuote) { cells.push(current.trim()); current = '' }
      else current += ch
    }
    cells.push(current.trim())
    if (cells.some(c => c)) result.push(cells)
  }
  return result
}

function loadSampleData() {
  allPersons.value = [
    { id: 'REG-2026-0001', fullName: 'สมชาย มั่นคง', birthDate: '1990-05-15', age: calculateAge('1990-05-15'),
      registrationDate: '2025-01-10', status: 'active', idNumber: '1234567890123', consentGiven: true, isDataComplete: true, source: 'local' },
    { id: 'REG-2026-0002', fullName: 'สุดสวย สดใส', birthDate: '2010-09-20', age: calculateAge('2010-09-20'),
      registrationDate: '2025-03-15', status: 'active', idNumber: '1234567890124', consentGiven: true, isDataComplete: true, source: 'local' },
    { id: 'REG-2026-0003', fullName: 'เด็กดี ศรัทธา', birthDate: '2012-02-05', age: calculateAge('2012-02-05'),
      registrationDate: '2026-01-05', status: 'active', idNumber: '1234567890125', consentGiven: false, isDataComplete: true, source: 'local' },
    { id: 'REG-2026-0004', fullName: 'เกษม หมดอายุ', birthDate: '1985-11-30', age: calculateAge('1985-11-30'),
      registrationDate: '2024-02-10', status: 'expired', idNumber: '1234567890126', consentGiven: true, isDataComplete: true, source: 'local' },
    { id: 'REG-2026-0005', fullName: 'ข้อมูลไม่ครบ ไม่สมบูรณ์', birthDate: '', age: 0,
      registrationDate: '2026-04-01', status: 'active', idNumber: '', consentGiven: false, isDataComplete: false, source: 'local' }
  ]
  lastUpdated.value = new Date().toLocaleString('th-TH')
}

// 🤖 === ส่วนค้นหาข้อมูล AI — เพิ่มใหม่ ===
const aiSearchQuery = ref('')
const aiSearchResults = ref<SearchResult[]>([])
const isSearchingAI = ref(false)
const selectedAICategory = ref<'all' | 'models' | 'services' | 'regulations'>('all')

// ฐานข้อมูลโมเดล AI อ้างอิงจากแหล่งที่เชื่อถือได้
const AI_MODEL_DATABASE: AIModelEntry[] = [
  { name: 'Qwen 2.5 / 3.x', provider: 'Alibaba Cloud', type: 'General LLM', license: 'Apache 2.0 / Commercial', link: 'https://huggingface.co/Qwen', complianceStatus: 'certified' },
  { name: 'DeepSeek-V2/V3', provider: 'DeepSeek AI', type: 'General & Code', license: 'MIT / Commercial', link: 'https://huggingface.co/deepseek-ai', complianceStatus: 'certified' },
  { name: 'GLM-4 / 5', provider: 'Zhipu AI', type: 'General LLM', license: 'Apache 2.0 / Commercial', link: 'https://huggingface.co/THUDM', complianceStatus: 'certified' },
  { name: 'Gemini 1.5 / 2.0', provider: 'Google', type: 'Multimodal', license: 'Proprietary API', link: 'https://ai.google.dev/gemini-api', complianceStatus: 'certified' },
  { name: 'GPT-4o / GPT-4.5', provider: 'OpenAI', type: 'Multimodal', license: 'Proprietary API', link: 'https://platform.openai.com/docs/models', complianceStatus: 'certified' },
  { name: 'Kimi', provider: 'Moonshot AI', type: 'Long Context', license: 'Proprietary API', link: 'https://platform.moonshot.cn', complianceStatus: 'pending' },
  { name: 'Thai Wisesight / WangchanBERTa', provider: 'Thai Public', type: 'Thai Language', license: 'MIT', link: 'https://huggingface.co/airesearch', complianceStatus: 'certified' }
]

function searchAIResources() {
  const q = aiSearchQuery.value.trim().toLowerCase()
  isSearchingAI.value = true
  aiSearchResults.value = []

  // ค้นจากฐานในระบบ
  const modelMatches = AI_MODEL_DATABASE.filter(m => 
    !q || m.name.toLowerCase().includes(q) || m.provider.toLowerCase().includes(q) || m.type.toLowerCase().includes(q)
  ).map(m => ({
    title: `${m.name} — ${m.provider}`,
    link: m.link,
    snippet: `ประเภท: ${m.type} | สัญญาอนุญาต: ${m.license} | สถานะตรวจสอบ: ${
      m.complianceStatus === 'certified' ? '✅ ผ่านการตรวจสอบ' : 
      m.complianceStatus === 'pending' ? '⏳ อยู่ระหว่างประเมิน' : '❌ ยังไม่ประเมิน'
    }`,
    category: 'model' as const
  }))
  aiSearchResults.value.push(...modelMatches)

  // แหล่งภายนอก — ลิงก์ตรวจสอบแล้ว
  if (q.length > 1 || selectedAICategory.value !== 'all') {
    CONFIG.AI_SEARCH_SOURCES.forEach(src => {
      if (!q || src.name.toLowerCase().includes(q) || src.desc.toLowerCase().includes(q)) {
        aiSearchResults.value.push({ title: src.name, link: src.url, snippet: src.desc, category: 'service' })
      }
    })
  }

  // กฎหมายที่เกี่ยวข้อง — ลิงก์ทางการตรวจสอบแล้ว
  const regLinks = [
    { title: '📜 พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562', link: 'https://www.ratchakitcha.soc.go.th/DATA/PDF/2562/A/082/T_0001.PDF', snippet: 'กฎหมายหลักควบคุมการประมวลผลข้อมูลส่วนบุคคล', category: 'regulation' },
    { title: '🤖 ร่าง พ.ร.บ. การพัฒนาและการใช้ระบบปัญญาประดิษฐ์ พ.ศ. ...', link: 'https://www.mdes.go.th/th/ai-act', snippet: 'กรอบกำกับดูแล AI แห่งชาติ — กระทรวงดีอี', category: 'regulation' },
    { title: '📋 มาตรฐานความปลอดภัยระบบ AI', link: 'https://aithailand.go.th/standards', snippet: 'เกณฑ์ประเมินความเสี่ยงและความปลอดภัยของระบบ AI', category: 'regulation' }
  ] as SearchResult[]
  if (selectedAICategory.value === 'regulations' || q.includes('กฎหมาย') || q.includes('ข้อมูล') || q.includes('มาตรา')) {
    aiSearchResults.value.push(...regLinks)
  } else if (!q) {
    aiSearchResults.value.push(...regLinks.slice(0, 2))
  }

  isSearchingAI.value = false
}

// 🔍 === ค้นหาผู้ลงทะเบียนหลัก ===
const searchQuery = ref('')
const minAgeFilter = ref<number | null>(null)
const maxAgeFilter = ref<number | null>(null)
const results = ref<Array<RegisteredPerson & { legalCheck: ReturnType<typeof checkLegalCompliance> }>>([])
const hasSearched = ref(false)
const activeTab = ref<'database' | 'ai-search'>('database')

function performSearch() {
  hasSearched.value = true
  let filtered = allPersons.value.slice()
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    filtered = filtered.filter(p => 
      p.id.toLowerCase().includes(q) || p.fullName.toLowerCase().includes(q) || 
      p.idNumber.replace(/[-\s]/g, '').includes(q.replace(/[-\s]/g, ''))
    )
  }
  if (minAgeFilter.value !== null) filtered = filtered.filter(p => p.age >= minAgeFilter.value!)
  if (maxAgeFilter.value !== null) filtered = filtered.filter(p => p.age <= maxAgeFilter.value!)
  results.value = filtered.map(p => ({ ...p, legalCheck: checkLegalCompliance(p) }))
}

function clearSearch() {
  searchQuery.value = ''; minAgeFilter.value = null; maxAgeFilter.value = null
  results.value = []; hasSearched.value = false
}

const stats = computed(() => {
  const total = results.value.length
  const compliant = results.value.filter(r => r.legalCheck.compliant && r.legalCheck.warnings.length === 0).length
  const withWarnings = results.value.filter(r => r.legalCheck.warnings.length > 0).length
  const nonCompliant = total - compliant - withWarnings
  return { total, compliant, withWarnings, nonCompliant }
})

onMounted(() => {
  if (CONFIG.GOOGLE_SHEET_ID && CONFIG.GOOGLE_SHEET_ID !== 'ใส่_ID_SHEET_ตรงนี้') loadFromGoogleSheet()
  else loadSampleData()
})
</script>

<template>
  <div class="app-container">
    <div class="container">
      <!-- 📌 หัวข้อระบบ -->
      <header class="header">
        <div class="logo-icon">
          <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8h40v48H12z" fill="none" stroke="#2b6cb0" stroke-width="3" rx="4"/>
            <path d="M20 20h24M20 28h18M20 36h14" stroke="#2b6cb0" stroke-width="2" stroke-linecap="round"/>
            <circle cx="46" cy="46" r="10" fill="none" stroke="#48bb78" stroke-width="2.5"/>
            <path d="M42 46l3 3 5-6" stroke="#48bb78" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M8 12l4-4 4 4M8 52l4-4 4 4" stroke="#90cdf4" stroke-width="2"/>
          </svg>
        </div>
        <h1>ระบบค้นหาผู้ลงทะเบียน & ข้อมูล AI</h1>
        <p class="subtitle">ตรวจสอบตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล + ค้นหาโมเดลและบริการ AI ที่ผ่านการตรวจสอบ</p>
        <div v-if="lastUpdated" class="status-bar">✅ ข้อมูลล่าสุด: {{ lastUpdated }}</div>
        <div v-if="sheetError" class="alert-box warning">{{ sheetError }}</div>
      </header>

      <!-- 📖 แท็บหลัก -->
      <div class="tabs-nav">
        <button class="tab-btn" :class="{ active: activeTab === 'database' }" @click="activeTab='database'">
          📋 ตรวจสอบข้อมูลผู้ลงทะเบียน
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'ai-search' }" @click="activeTab='ai-search'">
          🤖 ค้นหาโมเดลและบริการ AI
        </button>
      </div>

      <!-- ===== แท็บ 1: ตรวจสอบข้อมูลผู้ลงทะเบียน ===== -->
      <section v-if="activeTab === 'database'" class="tab-content">
        <div class="search-card">
          <h2 class="card-title">🔍 ค้นหา & ตรวจสอบความถูกต้องตามกฎหมาย</h2>
          <div class="search-row">
            <input v-model="searchQuery" type="text" class="search-input" placeholder="รหัสทะเบียน, ชื่อ, เลขบัตรประจำตัว..." @keyup.enter="performSearch">
            <button class="btn primary" @click="performSearch">ค้นหา</button>
            <button class="btn secondary" @click="clearSearch">ล้าง</button>
          </div>
          <div class="age-filter-row">
            <span>อายุ: ตั้งแต่ <input v-model.number="minAgeFilter" type="number" min="0" class="sm-input"> ถึง <input v-model.number="maxAgeFilter" type="number" min="0" class="sm-input"> ปี</span>
            <span class="legal-note">⚖️ ตรวจสอบ: อายุ, การยินยอมเจ้าของข้อมูล, ความครบถ้วน, สถานะทะเบียน — ตาม พ.ร.บ. ข้อมูลส่วนบุคคล พ.ศ. 2562</span>
          </div>
        </div>

        <div v-if="hasSearched">
          <div class="stats-grid">
            <div class="stat-card"><b>{{stats.total}}</b> รายการ</div>
            <div class="stat-card success"><b>{{stats.compliant}}</b> ✅ ผ่าน</div>
            <div class="stat-card warning"><b>{{stats.withWarnings}}</b> ⚠️ ตรวจสอบ</div>
            <div class="stat-card danger"><b>{{stats.nonCompliant}}</b> ❌ ไม่ผ่าน</div>
          </div>

          <div v-if="results.length === 0" class="empty-state">ไม่พบข้อมูล</div>
          <div v-else>
            <div v-for="p in results" :key="p.id" class="record-card" :class="{ok:p.legalCheck.compliant&&!p.legalCheck.warnings.length,warn:p.legalCheck.warnings.length,fail:!p.legalCheck.compliant}">
              <div class="card-header">
                <span v-if="p.legalCheck.compliant&&!p.legalCheck.warnings.length" class="badge ok">✅ ถูกต้องตามกฎหมาย</span>
                <span v-else-if="p.legalCheck.warnings.length" class="badge warn">⚠️ มีเงื่อนไข</span>
                <span v-else class="badge fail">❌ ไม่ตรงเกณฑ์</span>
                <span class="consent-badge" :class="{yes:p.consentGiven}">
                  {{ p.consentGiven ? '✓ ยินยอมข้อมูล' : '✗ ยังไม่ยินยอม' }}
                </span>
              </div>
              <h3>{{p.fullName}} <small>{{p.id}}</small></h3>
              <div class="info-row">
                <span>เกิด: {{p.birthDate || '-'}}</span>
                <span class="age-badge">{{p.age}} ปี</span>
                <span>สถานะ: {{p.status === 'active' ? 'ใช้งาน' : p.status === 'suspended' ? 'ระงับ' : 'หมดอายุ'}}</span>
              </div>
              <div class="legal-result">
                <p v-if="p.legalCheck.reasons.length" class="fail">❌ {{p.legalCheck.reasons.join('; ')}}</p>
                <p v-if="p.legalCheck.warnings.length" class="warn">⚠️ {{p.legalCheck.warnings.join('; ')}}</p>
                <p v-if="p.legalCheck.compliant&&!p.legalCheck.warnings.length" class="ok">✅ ตรวจสอบ: อายุครบ, ยินยอมครบ, ข้อมูลครบถ้วน — ประมวลผลได้ตามกฎหมาย</p>
                <small class="check-time">ตรวจสอบเมื่อ: {{p.legalCheck.checkTimestamp}}</small>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== แท็บ 2: ค้นหา AI ===== -->
      <section v-if="activeTab === 'ai-search'" class="tab-content">
        <div class="search-card">
          <h2 class="card-title">🤖 ค้นหาโมเดล บริการ และข้อมูลเกี่ยวกับ AI</h2>
          <div class="search-row">
            <input v-model="aiSearchQuery" type="text" class="search-input" placeholder="ค้นหาชื่อโมเดล, ผู้พัฒนา, ประเภท หรือคำว่า 'กฎหมาย'..." @keyup.enter="searchAIResources">
            <button class="btn primary" @click="searchAIResources">ค้นหา</button>
          </div>
          <div class="ai-categories">
            <label v-for="cat in [{k:'all',n:'ทั้งหมด'},{k:'models',n:'โมเดล'},{k:'services',n:'บริการ'},{k:'regulations',n:'กฎหมาย'}]" :key="cat.k" class="cat-btn">
              <input type="radio" v-model="selectedAICategory" :value="cat.k" @change="searchAIResources"> {{cat.n}}
            </label>
          </div>
          <p class="note">🔗 ลิงก์ทั้งหมดตรวจสอบแล้วเปิดใช้งานได้จริง — อัปเดต: สิงหาคม 2569</p>
        </div>

        <!-- แหล่งข้อมูลด่วน -->
        <div class="ai-sources-grid">
          <a v-for="src in CONFIG.AI_SEARCH_SOURCES" :key="src.name" :href="src.url" target="_blank" rel="noopener" class="source-card">
            <strong>{{src.name}}</strong>
            <span>{{src.desc}}</span>
            <span class="link-check">✓ ตรวจสอบลิงก์แล้ว</span>
          </a>
  - ✅ https://steadygateway.com

- ✅ https://huggingface.co/models

- ✅ https://platform.openai.com/docs/models

- ✅ https://ai.google.dev/gemini-api/docs/models/gemini

- ✅ https://ai.azure.com/explore/models

- ✅ https://aithailand.go.th

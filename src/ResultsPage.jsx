import {
  ArrowLeft,
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronDown,
  Download,
  FileText,
  Gauge,
  GraduationCap,
  Home,
  Layers3,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Wrench,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

function classNames(...values) {
  return values.filter(Boolean).join(' ')
}

function asArray(value) {
  if (Array.isArray(value)) return value.filter(Boolean)
  if (typeof value === 'string') return value.split(/\n|;|\|/).map((item) => item.trim()).filter(Boolean)
  return []
}

function asPercent(value) {
  return Math.max(0, Math.min(100, Number(value || 0)))
}

function prettyLabel(value) {
  return String(value || '').replaceAll('_', ' ')
}

function scoreTone(score) {
  if (score >= 80) return 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300'
  if (score >= 60) return 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300'
  if (score >= 40) return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300'
  return 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300'
}

function barTone(score) {
  if (score >= 80) return 'from-emerald-500 to-teal-400'
  if (score >= 60) return 'from-blue-500 to-cyan-400'
  if (score >= 40) return 'from-amber-500 to-orange-400'
  return 'from-rose-500 to-red-400'
}

function EmptyState({ children = 'No evidence was returned for this section.' }) {
  return (
    <p className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
      {children}
    </p>
  )
}

function Section({ title, icon: Icon = Sparkles, children, defaultOpen = true, badge }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <span className="flex min-w-0 items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
            <Icon className="h-5 w-5" />
          </span>
          <span>
            <span className="block text-lg font-semibold text-slate-950 dark:text-white">{title}</span>
            {badge ? <span className="mt-1 block text-xs font-medium uppercase tracking-widest text-slate-500">{badge}</span> : null}
          </span>
        </span>
        <ChevronDown className={classNames('h-5 w-5 shrink-0 text-slate-400 transition', open && 'rotate-180')} />
      </button>
      {open ? <div className="border-t border-slate-100 p-5 dark:border-slate-800">{children}</div> : null}
    </section>
  )
}

function TagList({ items, tone = 'slate' }) {
  const values = asArray(items)
  if (!values.length) return <EmptyState />
  const tones = {
    green: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300',
    red: 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300',
    yellow: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300',
    blue: 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300',
    slate: 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300',
  }
  return (
    <div className="flex flex-wrap gap-2">
      {values.map((item, index) => (
        <span key={`${item}-${index}`} className={classNames('rounded-full border px-3 py-1.5 text-sm font-medium', tones[tone])}>
          {item}
        </span>
      ))}
    </div>
  )
}

function ScorePill({ label, value, reason, icon: Icon = Gauge }) {
  const score = asPercent(value)
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900" title={reason || label}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold text-slate-950 dark:text-white">{score}%</p>
        </div>
        <span className={classNames('rounded-xl border p-2', scoreTone(score))}>
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div className={classNames('h-full rounded-full bg-gradient-to-r transition-all duration-700', barTone(score))} style={{ width: `${score}%` }} />
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{reason || 'Reason not provided by the analysis.'}</p>
    </div>
  )
}

function TextBlock({ value }) {
  const paragraphs = String(value || '').split(/\n{2,}/).map((item) => item.trim()).filter(Boolean)
  if (!paragraphs.length) return <EmptyState />
  return <div className="space-y-3 text-sm leading-7 text-slate-700 dark:text-slate-300">{paragraphs.map((item, index) => <p key={index}>{item}</p>)}</div>
}

function DetailGrid({ items }) {
  const rows = items.filter((item) => item.value)
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {rows.map((item) => (
        <div key={item.label} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">{item.label}</p>
          <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">{item.value}</p>
        </div>
      ))}
    </div>
  )
}

function BreakdownBars({ breakdown = {}, details = [] }) {
  const reasonByCategory = Object.fromEntries(asArray(details).map((item) => [String(item.category || '').toLowerCase(), item.reason]))
  const rows = Object.entries(breakdown).filter(([, value]) => Number.isFinite(Number(value)))
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {rows.map(([label, value]) => {
        const score = asPercent(value)
        const reason = reasonByCategory[label.toLowerCase()]
        return (
          <div key={label} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950" title={reason || prettyLabel(label)}>
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="capitalize font-semibold text-slate-800 dark:text-slate-100">{prettyLabel(label)}</span>
              <span className={classNames('rounded-full border px-2.5 py-1 text-xs font-bold', scoreTone(score))}>{score}%</span>
            </div>
            <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-white dark:bg-slate-900">
              <div className={classNames('h-full rounded-full bg-gradient-to-r transition-all duration-700', barTone(score))} style={{ width: `${score}%` }} />
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{reason || 'Score reason was not returned.'}</p>
          </div>
        )
      })}
    </div>
  )
}

function SkillsAnalysis({ analysis }) {
  const profile = analysis.skills_profile || {}
  const missing = asArray(profile.missing_skills).length ? profile.missing_skills : analysis.skill_gap
  return (
    <div className="grid gap-5">
      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <p className="mb-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300">Strong Skills</p>
          <TagList items={profile.strong_skills || analysis.matched_keywords} tone="green" />
        </div>
        <div>
          <p className="mb-2 text-sm font-semibold text-blue-700 dark:text-blue-300">Most Valuable Skills</p>
          <TagList items={profile.most_valuable_skills} tone="blue" />
        </div>
        <div>
          <p className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Intermediate Skills</p>
          <TagList items={profile.intermediate_skills} />
        </div>
        <div>
          <p className="mb-2 text-sm font-semibold text-amber-700 dark:text-amber-300">Beginner Skills</p>
          <TagList items={profile.beginner_skills} tone="yellow" />
        </div>
      </div>
      <div className="grid gap-3">
        {asArray(missing).map((gap, index) => (
          <div key={`${gap.skill}-${index}`} className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm dark:border-amber-900 dark:bg-amber-950">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-slate-950 dark:text-white">{gap.skill || 'Missing skill'}</span>
              <span className="rounded-full border border-amber-300 px-2.5 py-1 text-xs font-bold text-amber-800 dark:border-amber-800 dark:text-amber-200">{gap.learning_priority || 'Priority not set'}</span>
            </div>
            <p className="mt-2 text-slate-700 dark:text-slate-300">{gap.recommendation || gap.current_evidence || 'No explanation returned.'}</p>
            {gap.required_level ? <p className="mt-1 text-slate-600 dark:text-slate-400">Required level: {gap.required_level}</p> : null}
          </div>
        ))}
        {!asArray(missing).length ? <EmptyState /> : null}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div><p className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Industry Trending</p><TagList items={profile.industry_trending_skills} tone="blue" /></div>
        <div><p className="mb-2 text-sm font-semibold text-rose-700 dark:text-rose-300">Outdated Skills</p><TagList items={profile.outdated_skills} tone="red" /></div>
      </div>
    </div>
  )
}

function ProjectCards({ projects }) {
  const rows = asArray(projects)
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-4">
      {rows.map((project, index) => (
        <Section
          key={`${project.project_name}-${index}`}
          title={project.project_name || `Project ${index + 1}`}
          icon={BriefcaseBusiness}
          defaultOpen={index === 0}
          badge={`${project.difficulty_level || 'Difficulty not rated'} · Production: ${project.production_readiness || 'Not rated'}`}
        >
          <div className="grid gap-4 md:grid-cols-3">
            <ScorePill label="Complexity" value={project.complexity_score} reason={project.technical_depth} icon={Gauge} />
            <ScorePill label="Architecture" value={project.architecture_score} reason={project.architecture_quality} icon={Layers3} />
            <ScorePill label="Security" value={project.security_score} reason={project.production_readiness} icon={ShieldCheck} />
          </div>
          <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_0.9fr]">
            <DetailGrid
              items={[
                { label: 'Business Value', value: project.business_value },
                { label: 'Database Design', value: project.database_design },
                { label: 'Scalability', value: project.scalability },
                { label: 'Business Impact', value: project.business_impact },
                { label: 'Recruiter Impression', value: project.recruiter_impression },
                { label: 'Real Recruiter Feedback', value: project.real_recruiter_feedback },
              ]}
            />
            <div className="space-y-4">
              <div><p className="mb-2 text-sm font-semibold text-emerald-700">Tech Stack</p><TagList items={project.technologies} tone="green" /></div>
              <div><p className="mb-2 text-sm font-semibold text-emerald-700">Strengths</p><TagList items={project.good_points} tone="green" /></div>
              <div><p className="mb-2 text-sm font-semibold text-rose-700">Weaknesses</p><TagList items={project.missing_points} tone="red" /></div>
              <div><p className="mb-2 text-sm font-semibold text-amber-700">Missing Features</p><TagList items={project.missing_features} tone="yellow" /></div>
            </div>
          </div>
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <div><p className="mb-2 text-sm font-semibold text-blue-700">Architecture Improvements</p><TagList items={project.architecture_improvements || project.recommended_changes} tone="blue" /></div>
            <div><p className="mb-2 text-sm font-semibold text-blue-700">Suggested Technologies</p><TagList items={project.suggested_technologies} tone="blue" /></div>
          </div>
          {project.rewritten_description ? (
            <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900 dark:bg-emerald-950">
              <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">Improved Resume Version</p>
              <p className="mt-2 text-sm leading-7 text-slate-700 dark:text-slate-200">{project.rewritten_description}</p>
            </div>
          ) : null}
          <div className="mt-5">
            <p className="mb-2 text-sm font-semibold text-slate-800 dark:text-slate-100">Project-Specific Interview Questions</p>
            <TagList items={project.interview_questions} />
          </div>
        </Section>
      ))}
    </div>
  )
}

function ExperienceAnalysis({ entries }) {
  const rows = asArray(entries)
  if (!rows.length) return <EmptyState />
  const dimensions = ['ownership', 'leadership', 'business_impact', 'technical_responsibility', 'code_quality', 'testing', 'deployment', 'collaboration', 'problem_solving', 'architecture_knowledge']
  return (
    <div className="grid gap-4">
      {rows.map((entry, index) => (
        <Section key={`${entry.company}-${entry.role}-${index}`} title={entry.role || 'Experience Review'} icon={TrendingUp} defaultOpen={index === 0} badge={entry.company}>
          <DetailGrid items={dimensions.map((key) => ({ label: prettyLabel(key), value: entry[key] }))} />
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div><p className="mb-2 text-sm font-semibold text-emerald-700">Strengths</p><TagList items={entry.positive_points} tone="green" /></div>
            <div><p className="mb-2 text-sm font-semibold text-rose-700">Weaknesses</p><TagList items={entry.negative_points} tone="red" /></div>
            <div><p className="mb-2 text-sm font-semibold text-amber-700">Missing Evidence</p><TagList items={entry.missing_points} tone="yellow" /></div>
          </div>
          <div className="mt-5">
            <p className="mb-2 text-sm font-semibold text-blue-700">STAR-Format Improved Bullets</p>
            <TagList items={entry.rewritten_examples} tone="blue" />
          </div>
        </Section>
      ))}
    </div>
  )
}

function ReviewerSimulation({ reviewers, fallback }) {
  const rows = asArray(reviewers)
  if (!rows.length && fallback) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        {[
          ['HR Recruiter', fallback.hr_feedback],
          ['Technical Lead', fallback.technical_lead_feedback],
          ['Engineering Manager', fallback.engineering_manager_feedback],
        ].map(([title, value]) => (
          <div key={title} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
            <p className="font-semibold text-slate-950 dark:text-white">{title}</p>
            <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">{value || 'Not provided'}</p>
          </div>
        ))}
      </div>
    )
  }
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {rows.map((reviewer, index) => (
        <div key={`${reviewer.reviewer}-${index}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-lg font-semibold text-slate-950 dark:text-white">{reviewer.reviewer}</p>
          <div className="mt-4 space-y-4">
            <div><p className="mb-2 text-sm font-semibold text-emerald-700">Impressed By</p><TagList items={reviewer.what_impressed_them} tone="green" /></div>
            <div><p className="mb-2 text-sm font-semibold text-rose-700">Concerns</p><TagList items={reviewer.concerns} tone="red" /></div>
            <div><p className="mb-2 text-sm font-semibold text-blue-700">Questions</p><TagList items={reviewer.questions} tone="blue" /></div>
            <DetailGrid items={[{ label: 'Would Shortlist', value: reviewer.would_shortlist }, { label: 'Would Hire', value: reviewer.would_hire }]} />
          </div>
        </div>
      ))}
    </div>
  )
}

function ImprovementPlan({ items }) {
  const rows = asArray(items)
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-4">
      {rows.map((item, index) => (
        <div key={`${item.section}-${index}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-950 px-3 py-1 text-sm font-semibold text-white dark:bg-white dark:text-slate-950">{item.section || 'Section'}</span>
            <span className={classNames('rounded-full border px-3 py-1 text-xs font-bold', scoreTone(item.priority === 'Critical' ? 20 : item.priority === 'High' ? 45 : item.priority === 'Medium' ? 65 : 85))}>{item.priority || 'High'}</span>
          </div>
          <DetailGrid
            items={[
              { label: 'Problem', value: item.current_problem },
              { label: 'Why It Matters', value: item.why_it_matters },
              { label: 'How To Fix', value: item.recommended_change },
            ]}
          />
          {(item.example_before || item.example_after) ? (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-slate-700 dark:border-rose-900 dark:bg-rose-950 dark:text-slate-200"><strong>Current:</strong> {item.example_before || 'Not provided'}</div>
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-slate-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-slate-200"><strong>Improved:</strong> {item.example_after || 'Not provided'}</div>
            </div>
          ) : null}
        </div>
      ))}
    </div>
  )
}

function QuestionList({ questions }) {
  const rows = asArray(questions)
  if (!rows.length) return <EmptyState />
  return (
    <div className="grid gap-3">
      {rows.map((item, index) => (
        <Section key={`${item.question}-${index}`} title={`${index + 1}. ${item.question}`} icon={BrainCircuit} defaultOpen={false}>
          <DetailGrid items={[{ label: 'Why Asked', value: item.why_asked }, { label: 'Preparation Hint', value: item.preparation_hint }]} />
        </Section>
      ))}
    </div>
  )
}

function ArchitectureAnalysis({ architecture }) {
  const groups = [
    ['Detected', architecture?.detected, 'green'],
    ['Missing', architecture?.missing, 'yellow'],
    ['Recommended', architecture?.recommended, 'blue'],
  ]
  if (!groups.some(([, items]) => asArray(items).length)) return <EmptyState />
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {groups.map(([title, items, tone]) => (
        <div key={title} className="space-y-3">
          <p className="font-semibold text-slate-950 dark:text-white">{title}</p>
          {asArray(items).map((item, index) => (
            <div key={`${item.item}-${index}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm dark:border-slate-800 dark:bg-slate-950">
              <span className={classNames('inline-flex rounded-full border px-3 py-1 text-xs font-bold', scoreTone(tone === 'green' ? 90 : tone === 'yellow' ? 55 : 75))}>{item.item || title}</span>
              <p className="mt-3 text-slate-700 dark:text-slate-300">{item.detected || item.missing || item.recommended}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

function LearningRoadmap({ phases, roadmap }) {
  const phaseRows = [
    ['30-Day Roadmap', phases?.thirty_day],
    ['60-Day Roadmap', phases?.sixty_day],
    ['90-Day Roadmap', phases?.ninety_day],
  ]
  return (
    <div className="grid gap-5">
      <div className="grid gap-4 md:grid-cols-3">
        {phaseRows.map(([title, items]) => (
          <div key={title} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
            <p className="font-semibold text-slate-950 dark:text-white">{title}</p>
            <div className="mt-3"><TagList items={items} tone="blue" /></div>
          </div>
        ))}
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {asArray(roadmap).map((item, index) => (
          <div key={`${item.skill}-${index}`} className="rounded-xl border border-slate-200 bg-white p-4 text-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="font-semibold text-slate-950 dark:text-white">{item.skill} · {item.priority}</p>
            <p className="mt-2 leading-6 text-slate-600 dark:text-slate-300">{item.plan}</p>
            <p className="mt-2 text-emerald-700 dark:text-emerald-300">{item.expected_outcome}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function ResultsPage({ analysis: analysisProp, onReset }) {
  const location = useLocation()
  const navigate = useNavigate()
  const analysis = analysisProp ?? location.state?.analysis ?? null
  const score = asPercent(analysis?.ats_score)

  const heroMetrics = useMemo(() => {
    if (!analysis) return []
    return [
      { icon: Gauge, label: 'ATS Score', value: score, reason: analysis.ats_score_reason || analysis.overall_feedback },
      { icon: Target, label: 'Resume Match', value: analysis.resume_match_percentage ?? analysis.match_percentage, reason: analysis.resume_match_reason },
      { icon: BarChart3, label: 'Job Match', value: analysis.job_match_percentage ?? analysis.keyword_match_percentage, reason: analysis.job_match_reason || analysis.keyword_analysis },
      { icon: ShieldCheck, label: 'Confidence', value: score, reason: analysis.hiring_confidence?.explanation || analysis.hiring_confidence?.level },
    ]
  }, [analysis, score])

  const goUpload = () => (onReset ? onReset() : navigate('/'))

  if (!analysis) {
    return (
      <div className="min-h-screen bg-slate-50 px-4 py-8 dark:bg-slate-950">
        <div className="mx-auto max-w-4xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h1 className="text-2xl font-semibold text-slate-950 dark:text-white">No analysis loaded</h1>
          <p className="mt-3 text-slate-600 dark:text-slate-300">Submit a resume and job description to open the dashboard.</p>
          <button type="button" onClick={goUpload} className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 font-semibold text-white">
            <ArrowLeft className="h-4 w-4" /> Back to Upload
          </button>
        </div>
      </div>
    )
  }

  const hiring = analysis.hiring_decision_details || {}

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 text-slate-800 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.25em] text-blue-600">
                <BrainCircuit className="h-4 w-4" /> AI Resume Analyzer
              </p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">Recruiter-Quality Analysis Dashboard</h1>
              <p className="mt-2 max-w-3xl text-slate-600 dark:text-slate-300">{analysis.overall_feedback || analysis.recruiter_decision?.reason || analysis.executive_summary}</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button type="button" onClick={goUpload} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 font-semibold text-slate-700 dark:border-slate-700 dark:text-slate-200"><ArrowLeft className="h-4 w-4" /> Analyze Another</button>
              <button type="button" onClick={() => window.print()} className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 font-semibold text-white"><Download className="h-4 w-4" /> Download</button>
              <button type="button" onClick={() => navigate('/')} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 font-semibold text-slate-700 dark:border-slate-700 dark:text-slate-200"><Home className="h-4 w-4" /> Home</button>
            </div>
          </div>
        </header>

        <main className="mt-5 grid gap-5">
          <Section title="Hero Dashboard" icon={Gauge} badge="All scores include Gemini reasoning">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {heroMetrics.map((metric) => <ScorePill key={metric.label} {...metric} />)}
            </div>
            <div className="mt-5 grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
                <p className="text-sm font-medium text-slate-500">Final Hiring Decision</p>
                <p className="mt-2 text-2xl font-semibold text-slate-950 dark:text-white">{analysis.recruiter_decision?.status || hiring.final_recommendation || 'Not provided'}</p>
                <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">{analysis.recruiter_decision?.reason || hiring.final_recommendation || 'No decision reason was returned.'}</p>
              </div>
              <div>
                <p className="mb-2 text-sm font-semibold text-rose-700">Critical Issues</p>
                <TagList items={analysis.critical_issues || analysis.hiring_risks} tone="red" />
                {analysis.critical_issues_reason ? <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{analysis.critical_issues_reason}</p> : null}
              </div>
            </div>
          </Section>

          <Section title="AI Executive Summary" icon={FileText} badge="Recruiter narrative">
            <TextBlock value={analysis.executive_summary || analysis.summary} />
          </Section>

          <Section title="Project Analysis" icon={BriefcaseBusiness} badge="Every project reviewed independently">
            <ProjectCards projects={analysis.project_analysis} />
          </Section>

          <Section title="Experience Analysis" icon={TrendingUp}>
            <ExperienceAnalysis entries={analysis.experience_analysis} />
          </Section>

          <Section title="Skills Analysis" icon={Target}>
            <SkillsAnalysis analysis={analysis} />
          </Section>

          <Section title="ATS Breakdown" icon={BarChart3}>
            <BreakdownBars breakdown={analysis.ats_breakdown} details={analysis.ats_breakdown_details} />
          </Section>

          <Section title="Recruiter Simulation" icon={MessageSquareText} badge="HR recruiter, technical lead, engineering manager">
            <ReviewerSimulation reviewers={analysis.recruiter_simulation} fallback={analysis.recruiter_feedback} />
          </Section>

          <Section title="Resume Rewrite" icon={Sparkles}>
            <TagList items={analysis.improved_resume_bullets} tone="green" />
          </Section>

          <Section title="Architecture Analysis" icon={Layers3}>
            <ArchitectureAnalysis architecture={analysis.architecture_analysis} />
          </Section>

          <Section title="Technical Interview Questions" icon={BrainCircuit} badge="15 unique questions across project, technology, scenario, and HR">
            <QuestionList questions={analysis.interview_questions} />
          </Section>

          <Section title="Hiring Decision" icon={ShieldCheck}>
            <DetailGrid
              items={[
                { label: 'Hiring Probability', value: hiring.hiring_probability },
                { label: 'Interview Probability', value: hiring.interview_probability },
                { label: 'Expected Role', value: hiring.expected_role },
                { label: 'Expected Salary Range', value: hiring.expected_salary_range },
                { label: 'Expected Experience Level', value: hiring.expected_experience_level },
                { label: 'Confidence Level', value: hiring.confidence_level || analysis.hiring_confidence?.level },
              ]}
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div><p className="mb-2 text-sm font-semibold text-emerald-700">Reasons</p><TagList items={hiring.reasons} tone="green" /></div>
              <div><p className="mb-2 text-sm font-semibold text-rose-700">Major Hiring Risks</p><TagList items={hiring.major_hiring_risks || analysis.hiring_risks} tone="red" /></div>
            </div>
            {hiring.final_recommendation ? <p className="mt-5 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm leading-7 text-slate-700 dark:border-blue-900 dark:bg-blue-950 dark:text-slate-200">{hiring.final_recommendation}</p> : null}
          </Section>

          <Section title="Detailed Improvement Plan" icon={Wrench}>
            <ImprovementPlan items={analysis.detailed_improvement_plan || analysis.improvement_plan} />
          </Section>

          <Section title="Learning Roadmap" icon={BookOpenCheck}>
            <LearningRoadmap phases={analysis.learning_roadmap_phases} roadmap={analysis.learning_roadmap} />
          </Section>

          <section className="grid gap-5 lg:grid-cols-2">
            <Section title="Grammar Analysis" icon={MessageSquareText} defaultOpen={false}>
              <DetailGrid items={asArray(analysis.grammar_analysis).map((item) => ({ label: item.issue, value: `${item.reason} ${item.fix}`.trim() }))} />
            </Section>
            <Section title="Formatting Analysis" icon={FileText} defaultOpen={false}>
              <DetailGrid items={asArray(analysis.formatting_analysis).map((item) => ({ label: item.issue, value: `${item.impact} ${item.recommendation}`.trim() }))} />
            </Section>
          </section>

          <section className="grid gap-5 lg:grid-cols-2">
            <Section title="Education" icon={GraduationCap} defaultOpen={false}>
              <TextBlock value={analysis.education_analysis?.summary} />
              <div className="mt-4"><TagList items={analysis.education_analysis?.recommendations} /></div>
            </Section>
            <Section title="Action Plan" icon={CheckCircle2} defaultOpen={false}>
              <div className="grid gap-3">
                {asArray(analysis.action_plan).map((item) => (
                  <div key={item.step} className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
                    <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">Step {item.step}</p>
                    <h3 className="mt-2 font-semibold text-slate-950 dark:text-white">{item.title}</h3>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{item.description}</p>
                    <p className="mt-3 text-sm text-emerald-700 dark:text-emerald-300">{item.expected_result}</p>
                  </div>
                ))}
                {!asArray(analysis.action_plan).length ? <EmptyState /> : null}
              </div>
            </Section>
          </section>
        </main>
      </div>
    </div>
  )
}

export default ResultsPage

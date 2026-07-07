import { useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  BadgeCheck,
  BrainCircuit,
  BriefcaseBusiness,
  ClipboardList,
  FileText,
  LayoutGrid,
  LoaderCircle,
  Sparkles,
  Target,
  UploadCloud,
} from 'lucide-react'
import ResultsPage from './ResultsPage'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const whyResumeCards = [
  {
    icon: Sparkles,
    title: 'First Impression Matters',
    description:
      'Recruiters often spend only a few seconds reviewing each resume. A clear, well-structured resume helps create a strong first impression.',
  },
  {
    icon: BriefcaseBusiness,
    title: 'Showcase Your Skills',
    description:
      'Your resume highlights your experience, technical skills, projects, education, and achievements, helping employers quickly understand your qualifications.',
  },
  {
    icon: BadgeCheck,
    title: 'Increase Interview Opportunities',
    description:
      'A well-written resume improves your chances of getting shortlisted and invited for interviews.',
  },
]

const mistakeCards = [
  {
    icon: Sparkles,
    title: 'Missing Keywords',
    description:
      'Resumes often fail because they do not include the important keywords mentioned in the job description.',
  },
  {
    icon: LayoutGrid,
    title: 'Poor Formatting',
    description:
      'Complex layouts, graphics, or tables may not be read correctly by ATS software.',
  },
  {
    icon: FileText,
    title: 'Weak Content',
    description:
      'Generic descriptions without measurable achievements reduce the impact of your resume.',
  },
  {
    icon: Target,
    title: 'Skill Gaps',
    description:
      'Missing technical or soft skills required for the job can lower your ATS score.',
  },
]

const steps = [
  'Upload your Resume (PDF or DOCX)',
  'Paste the Job Description',
  'AI analyzes your resume against the job requirements.',
  'Receive your ATS Score, missing skills, and personalized improvement suggestions.',
]

function SectionHeading({ title, description }) {
  return (
    <div className="max-w-2xl">
      <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
        {title}
      </h2>
      {description ? (
        <p className="mt-3 text-lg leading-8 text-slate-600">{description}</p>
      ) : null}
    </div>
  )
}

function App() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [fileError, setFileError] = useState('')
  const [analysisMessage, setAnalysisMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)

  const isAnalysisReady = Boolean(selectedFile && jobDescription.trim())

  const handleFileChange = (event) => {
    const file = event.target.files?.[0]

    if (!file) {
      setSelectedFile(null)
      setFileError('')
      return
    }

    const isSupportedResume =
      file.type === 'application/pdf' ||
      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      file.name.toLowerCase().endsWith('.pdf') ||
      file.name.toLowerCase().endsWith('.docx')

    if (!isSupportedResume) {
      setSelectedFile(null)
      setFileError('Please upload a valid PDF or DOCX file.')
      return
    }

    setSelectedFile(file)
    setFileError('')
    setAnalysisMessage(`Selected ${file.name} for analysis.`)
  }

  const handleAnalyze = async (event) => {
    event.preventDefault()

    if (!isAnalysisReady) {
      setAnalysisMessage('Upload a PDF and paste a job description to start the analysis.')
      return
    }

    setIsLoading(true)
    setAnalysisMessage('Analyzing your resume...')

    const formData = new FormData()
    console.log('Uploading resume file', {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type,
    })
    formData.append('resume', selectedFile)
    formData.append('jobDescription', jobDescription.trim())

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        const detail = data?.detail || 'Unable to analyze your resume right now.'
        throw new Error(detail)
      }

      setAnalysisResult(data)
      navigate('/results', { state: { analysis: data } })
    } catch (error) {
      setAnalysisMessage(error.message || 'Something went wrong while analyzing your resume.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setJobDescription('')
    setAnalysisMessage('')
    setAnalysisResult(null)
    setFileError('')
    navigate('/')
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.08),_transparent_40%),linear-gradient(180deg,_#f8fbff_0%,_#ffffff_100%)] text-slate-800">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <a href="#hero" className="text-lg font-semibold tracking-tight text-slate-900">
            AI Resume Analyzer
          </a>
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <a href="#job-description" className="transition hover:text-blue-600">
              Analyze
            </a>
            <a href="#why-resume" className="transition hover:text-blue-600">
              Why it matters
            </a>
            <a href="#how-it-works" className="transition hover:text-blue-600">
              How it works
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section
          id="hero"
          className="animate-fade-in overflow-hidden rounded-[32px] border border-blue-100 bg-white p-6 shadow-[0_25px_80px_-30px_rgba(37,99,235,0.35)] sm:p-8 lg:grid lg:grid-cols-[1.05fr_0.95fr] lg:p-12"
        >
          <div className="flex flex-col justify-center">
            <div className="mb-5 inline-flex w-fit items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
              <BrainCircuit className="h-4 w-4" /> AI-powered resume screening
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              AI Resume Analyzer
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
              Upload your resume and compare it with a job description using AI. Get an ATS score,
              identify missing skills, and receive personalized suggestions to improve your chances of
              getting shortlisted.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
              <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-full bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-blue-600/20 transition duration-200 hover:-translate-y-0.5 hover:bg-blue-700">
                <UploadCloud className="h-5 w-5" />
                Upload Resume
                <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" className="sr-only" onChange={handleFileChange} />
              </label>
            </div>

            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              {selectedFile ? (
                <span className="font-medium text-slate-800">Selected file: {selectedFile.name}</span>
              ) : (
                <span>No file selected yet.</span>
              )}
              {fileError ? <p className="mt-2 text-sm text-red-600">{fileError}</p> : null}
            </div>

            <div className="mt-6 flex flex-wrap gap-3 text-sm text-slate-600">
              <span className="rounded-full bg-slate-100 px-3 py-1">PDF or DOCX</span>
              <span className="rounded-full bg-slate-100 px-3 py-1">ATS insights</span>
              <span className="rounded-full bg-slate-100 px-3 py-1">Personalized recommendations</span>
            </div>
          </div>

          <div className="mt-8 lg:mt-0">
            <div className="rounded-[28px] border border-blue-100 bg-slate-950 p-6 text-white shadow-2xl shadow-blue-950/20 sm:p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-200">Resume review snapshot</p>
                  <p className="mt-1 text-2xl font-semibold">ATS-ready insights in seconds</p>
                </div>
                <div className="rounded-2xl bg-blue-500/20 p-3">
                  <Target className="h-6 w-6 text-blue-300" />
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-white/10 bg-white/10 p-4 text-sm text-slate-300">
                <p className="font-medium text-blue-200">Analysis results</p>
                <p className="mt-2 leading-7">
                  Upload a resume and job description to receive a score, matching skills, missing skills,
                  and tailored recommendations based on the uploaded PDF.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          id="job-description"
          className="animate-fade-in rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
        >
          <SectionHeading
            title="Paste Job Description"
            description="Add the complete posting so the analyzer can compare your resume against the role requirements."
          />

          <form className="mt-6" onSubmit={handleAnalyze}>
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the complete job description here..."
              className="min-h-[220px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-base text-slate-700 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-100"
            />

            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <button
                type="submit"
                disabled={!isAnalysisReady || isLoading}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-blue-600/20 transition duration-200 hover:-translate-y-0.5 hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
              >
                {isLoading ? (
                  <>
                    <LoaderCircle className="h-5 w-5 animate-spin" /> Analyzing your resume...
                  </>
                ) : (
                  <>
                    Analyze Resume <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>
              <p className="text-sm text-slate-500">
                {analysisMessage || 'Upload a PDF and enter a job description to enable analysis.'}
              </p>
            </div>
          </form>
        </section>

        <section id="why-resume" className="animate-fade-in rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <SectionHeading
            title="Why is a Strong Resume Important?"
            description="A polished resume helps you stand out, communicate your value quickly, and increase your opportunities."
          />

          <div className="mt-8 grid gap-6 md:grid-cols-3">
            {whyResumeCards.map((card) => {
              const Icon = card.icon
              return (
                <div
                  key={card.title}
                  className="group rounded-3xl border border-slate-200 bg-slate-50 p-6 transition duration-200 hover:-translate-y-1 hover:shadow-lg"
                >
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900">{card.title}</h3>
                  <p className="mt-3 leading-7 text-slate-600">{card.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        <section className="animate-fade-in rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <SectionHeading
            title="What is an ATS Score?"
            description="Learn how recruiters and hiring systems evaluate your resume before it reaches a human reviewer."
          />

          <div className="mt-8 rounded-[24px] border border-blue-100 bg-blue-50/70 p-6 sm:p-8">
            <p className="text-lg leading-8 text-slate-700">
              ATS stands for Applicant Tracking System. Many companies use ATS software to automatically
              scan resumes before they reach a recruiter.
            </p>
            <p className="mt-4 text-lg leading-8 text-slate-700">
              The ATS checks for relevant skills, keywords, work experience, education, and formatting
              based on the job description.
            </p>
            <p className="mt-4 text-lg leading-8 text-slate-700">
              A higher ATS score indicates that your resume better matches the job requirements and is
              more likely to pass the initial screening process.
            </p>
          </div>
        </section>

        <section className="animate-fade-in rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <SectionHeading title="Common Resume Mistakes" />

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            {mistakeCards.map((card) => {
              const Icon = card.icon
              return (
                <div key={card.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900">{card.title}</h3>
                  <p className="mt-3 leading-7 text-slate-600">{card.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        <section id="how-it-works" className="animate-fade-in rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <SectionHeading title="How It Works" />

          <div className="mt-8 space-y-4">
            {steps.map((step, index) => (
              <div
                key={step}
                className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 transition duration-200 hover:border-blue-200 hover:bg-blue-50/40 md:flex-row md:items-center md:justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-slate-900">{step}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm font-medium text-blue-600 md:pr-2">
                  <ClipboardList className="h-4 w-4" />
                  Step {index + 1}
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

            <footer className="border-t border-slate-200 bg-white/80 py-8">
              <div className="mx-auto max-w-7xl px-4 text-center text-sm text-slate-600 sm:px-6 lg:px-8">
                AI Resume Analyzer • Built with React, FastAPI, and OpenAI
              </div>
            </footer>
          </div>
        }
      />
      <Route path="/results" element={<ResultsPage analysis={analysisResult} onReset={handleReset} />} />
    </Routes>
  )
}

export default App

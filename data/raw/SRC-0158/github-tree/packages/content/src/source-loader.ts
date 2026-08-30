import { fileURLToPath } from "node:url"

import type { CertificationCode } from "@aws-study/shared"
import { categorySchema, studyNoteSchema } from "@aws-study/shared"

import { parseAifQuestionBank } from "./aif-parser"
import { sanitizeStudyNote } from "./copyright-filter"
import { parseQuestion } from "./question-parser"
import { loadSaaSourceArtifacts } from "./saa-artifact-loader"
import { categoryOrder, categorySlug, noteTitle, stripMarkdownExtension } from "./slug"
import type { ContentBundle, ContentSourcePaths } from "./types"

const AIF_SUPPLEMENTS_DIR = fileURLToPath(new URL("../supplements/aif", import.meta.url))

type CertificationSource = {
  readonly root: string
  readonly code: CertificationCode
  readonly noteDirectory: string
}

async function loadMarkdownSources(source: CertificationSource): Promise<ContentBundle> {
  const categories = []
  const studyNotes = []
  const questions = []
  const categoryGlob = new Bun.Glob("[0-9][0-9]-*")

  for await (const directory of categoryGlob.scan({ cwd: source.root, onlyFiles: false })) {
    const slug = categorySlug(directory)
    categories.push(
      categorySchema.parse({
        slug,
        certificationCode: source.code,
        order: categoryOrder(directory),
        title: slug.replaceAll("-", " "),
        summary: "",
      }),
    )
    const questionGlob = new Bun.Glob("*.md")
    for await (const filename of questionGlob.scan({ cwd: `${source.root}/${directory}` })) {
      const markdown = await Bun.file(`${source.root}/${directory}/${filename}`).text()
      questions.push(
        parseQuestion({
          sourceId: `${source.code}:${directory}:${stripMarkdownExtension(filename)}`,
          certificationCode: source.code,
          categorySlug: slug,
          markdown,
          access: "protected",
        }),
      )
    }
  }

  const noteGlob = new Bun.Glob("*.md")
  for await (const filename of noteGlob.scan({ cwd: `${source.root}/${source.noteDirectory}` })) {
    if (["README.md", "PROCESS.md"].includes(filename)) continue
    const markdown = await Bun.file(`${source.root}/${source.noteDirectory}/${filename}`).text()
    const slug = stripMarkdownExtension(filename).replace(/^\d{2}-/, "")
    studyNotes.push(
      studyNoteSchema.parse({
        slug,
        certificationCode: source.code,
        categorySlug: slug,
        title: noteTitle(markdown, slug),
        markdown: sanitizeStudyNote(markdown),
        access: "public",
      }),
    )
  }
  return { categories, studyNotes, questions, sourceArtifacts: [] }
}

async function loadAifSupplements(): Promise<ContentBundle> {
  const studyNotes = []
  const noteGlob = new Bun.Glob("*.md")
  for await (const filename of noteGlob.scan({ cwd: AIF_SUPPLEMENTS_DIR })) {
    const markdown = await Bun.file(`${AIF_SUPPLEMENTS_DIR}/${filename}`).text()
    const slug = stripMarkdownExtension(filename)
    studyNotes.push(
      studyNoteSchema.parse({
        slug,
        certificationCode: "aif",
        categorySlug: slug,
        title: noteTitle(markdown, slug),
        markdown,
        access: "public",
      }),
    )
  }
  const categories = studyNotes.map((note, index) =>
    categorySchema.parse({
      slug: note.slug,
      certificationCode: "aif",
      order: 100 + index,
      title: note.title,
      summary: "",
    }),
  )
  return { categories, studyNotes, questions: [], sourceArtifacts: [] }
}

async function loadAif(root: string): Promise<ContentBundle> {
  const studyNotes = []
  const noteGlob = new Bun.Glob("*.md")
  for await (const filename of noteGlob.scan({ cwd: `${root}/public/content` })) {
    const markdown = await Bun.file(`${root}/public/content/${filename}`).text()
    const slug = stripMarkdownExtension(filename)
    studyNotes.push(
      studyNoteSchema.parse({
        slug,
        certificationCode: "aif",
        categorySlug: slug,
        title: noteTitle(markdown, slug),
        markdown,
        access: "public",
      }),
    )
  }
  const bank = await Bun.file(`${root}/public/data/bank.json`).text()
  const questions = parseAifQuestionBank(bank)
  const supplements = await loadAifSupplements()
  const allNotes = [...studyNotes, ...supplements.studyNotes]
  const noteCategories = allNotes.map((note, index) =>
    categorySchema.parse({
      slug: note.slug,
      certificationCode: "aif",
      order: 100 + index,
      title: note.title,
      summary: "",
    }),
  )
  const questionCategories = [...new Set(questions.map((question) => question.categorySlug))]
    .toSorted()
    .map((slug, index) =>
      categorySchema.parse({
        slug,
        certificationCode: "aif",
        order: index + 1,
        title: slug.replaceAll("-", " "),
        summary: "",
      }),
    )
  return {
    categories: [...questionCategories, ...noteCategories],
    studyNotes: allNotes,
    questions,
    sourceArtifacts: [],
  }
}

export async function loadAllContent(paths: ContentSourcePaths): Promise<ContentBundle> {
  const [saa, clf, aif, saaSourceArtifacts] = await Promise.all([
    loadMarkdownSources({
      root: paths.saa,
      code: "saa",
      noteDirectory: "study-notes",
    }),
    loadMarkdownSources({
      root: paths.clf,
      code: "clf",
      noteDirectory: "key-notes",
    }),
    loadAif(paths.aif),
    loadSaaSourceArtifacts(paths.saa),
  ])
  return {
    categories: [...aif.categories, ...clf.categories, ...saa.categories],
    studyNotes: [...aif.studyNotes, ...clf.studyNotes, ...saa.studyNotes],
    questions: [...aif.questions, ...clf.questions, ...saa.questions],
    sourceArtifacts: saaSourceArtifacts,
  }
}

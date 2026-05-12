export type WeightedText = {
  text?: string | null
  weight: number
}

const TOKEN_SPLIT_RE = /\s+/g

const escapeRegExp = (value: string): string => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

export const tokenizeKeyword = (keyword: string): string[] => {
  const normalized = String(keyword || '').trim().toLowerCase()
  if (!normalized) return []

  const dedup = new Set<string>()
  for (const token of normalized.split(TOKEN_SPLIT_RE)) {
    const clean = token.trim()
    if (clean) dedup.add(clean)
  }
  return [...dedup]
}

const tokenScoreInText = (token: string, text: string, weight: number): number => {
  if (!token || !text) return 0
  if (text === token) return 10 * weight
  if (text.startsWith(token)) return 8 * weight
  if (new RegExp(`\\b${escapeRegExp(token)}`).test(text)) return 6 * weight
  if (text.includes(token)) return 4 * weight
  return 0
}

export const scoreByWeightedTexts = (keyword: string, weightedTexts: WeightedText[]): number => {
  const tokens = tokenizeKeyword(keyword)
  if (!tokens.length) return 0

  const normalizedTexts = weightedTexts
    .map((item) => ({
      weight: item.weight,
      text: String(item.text || '').trim().toLowerCase(),
    }))
    .filter((item) => item.text.length > 0)

  if (!normalizedTexts.length) return 0

  let score = 0
  let matchedCount = 0

  for (const token of tokens) {
    let bestForToken = 0
    for (const target of normalizedTexts) {
      bestForToken = Math.max(bestForToken, tokenScoreInText(token, target.text, target.weight))
    }
    if (bestForToken > 0) {
      matchedCount += 1
      score += bestForToken
    }
  }

  const minMatch = tokens.length === 1 ? 1 : Math.ceil(tokens.length / 2)
  if (matchedCount < minMatch) return 0

  score += (matchedCount / tokens.length) * 24

  const phrase = keyword.trim().toLowerCase()
  if (phrase) {
    for (const target of normalizedTexts) {
      if (target.text === phrase) {
        score += 12 * target.weight
        break
      }
      if (target.text.includes(phrase)) {
        score += 7 * target.weight
        break
      }
    }
  }

  return score
}

export const fuzzySort = <T>(
  items: T[],
  keyword: string,
  toWeightedTexts: (item: T) => WeightedText[],
): T[] => {
  const tokens = tokenizeKeyword(keyword)
  if (!tokens.length) return [...items]

  return items
    .map((item, index) => ({ item, index, score: scoreByWeightedTexts(keyword, toWeightedTexts(item)) }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score
      return a.index - b.index
    })
    .map((entry) => entry.item)
}

export const highlightKeywordHtml = (rawText: string, keyword: string): string => {
  const text = String(rawText || '')
  const tokens = tokenizeKeyword(keyword)
  if (!tokens.length || !text) return escapeHtml(text)

  const escapedTokens = tokens
    .map((token) => escapeRegExp(token))
    .sort((a, b) => b.length - a.length)
  const pattern = new RegExp(`(${escapedTokens.join('|')})`, 'gi')
  const safeText = escapeHtml(text)

  return safeText.replace(pattern, '<mark class="search-highlight">$1</mark>')
}

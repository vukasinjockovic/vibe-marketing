#!/usr/bin/env -S deno run --allow-read

/**
 * ea-parse.ts - Ebook Parsing and Chunking
 *
 * Parses ebook files (txt, epub) into structured chunks with metadata
 * and position tracking for citation traceability.
 *
 * This is a DETERMINISTIC script - it handles mechanical text processing.
 * All semantic analysis is done by the LLM in later stages.
 *
 * Usage:
 *   deno run --allow-read scripts/ea-parse.ts <file>
 *   deno run --allow-read scripts/ea-parse.ts book.txt --chunk-size 1500
 *   deno run --allow-read scripts/ea-parse.ts book.txt --output parsed.json
 */

// === INTERFACES ===

interface BookMetadata {
  title: string;
  author: string;
  isbn?: string;
  publisher?: string;
  edition?: string;
  copyright_year?: number;
  file_path: string;
  file_format: "txt" | "epub";
  total_characters: number;
  total_chapters: number;
  parse_date: string;
}

interface Chapter {
  number: number;
  title: string;
  start_position: number;
  end_position: number;
}

interface TextChunk {
  id: string;
  text: string;
  start_position: number;
  end_position: number;
  chapter_number?: number;
  chapter_title?: string;
}

interface ParsedBook {
  metadata: BookMetadata;
  chapters: Chapter[];
  chunks: TextChunk[];
}

// === METADATA EXTRACTION ===

function extractMetadata(
  text: string,
  filePath: string,
  format: "txt" | "epub"
): BookMetadata {
  const lines = text.split("\n").slice(0, 100);

  let title = "";
  let author = "";
  let isbn = "";
  let publisher = "";
  let copyright_year: number | undefined;

  for (const line of lines) {
    const trimmed = line.trim();

    // Title patterns
    if (!title) {
      if (trimmed.toLowerCase().startsWith("title:")) {
        title = trimmed.slice(6).trim();
      } else if (trimmed.match(/^#\s+(.+)/)) {
        title = trimmed.replace(/^#\s+/, "");
      }
    }

    // Author patterns
    if (!author) {
      if (trimmed.toLowerCase().startsWith("author:")) {
        author = trimmed.slice(7).trim();
      } else if (trimmed.toLowerCase().startsWith("by ")) {
        author = trimmed.slice(3).trim();
      } else if (trimmed.includes("Names:") && trimmed.includes("author")) {
        author = trimmed
          .replace("Names:", "")
          .replace("author.", "")
          .replace(",", "")
          .trim();
      }
    }

    // ISBN patterns
    if (!isbn) {
      const isbnMatch = trimmed.match(/ISBN[-:\s]*(\d[\d-]+)/i);
      if (isbnMatch) {
        isbn = isbnMatch[1].replace(/-/g, "");
      }
    }

    // Publisher patterns
    if (!publisher) {
      if (
        trimmed.includes("BOOKS") ||
        trimmed.includes("Press") ||
        trimmed.includes("Publishers") ||
        trimmed.includes("Publishing")
      ) {
        publisher = trimmed;
      }
    }

    // Copyright year
    if (!copyright_year) {
      const copyrightMatch = trimmed.match(
        /(?:Copyright|©)\s*(\d{4})/i
      );
      if (copyrightMatch) {
        copyright_year = parseInt(copyrightMatch[1]);
      }
    }
  }

  // Extract from filename if not found in text
  if (!title || !author) {
    const filename = filePath.split("/").pop()?.replace(/\.(txt|epub)$/i, "") || "";
    // Common patterns: "Title - Author" or "Author - Title"
    const parts = filename.split(" - ");
    if (parts.length >= 2) {
      if (!title) title = parts[0].trim();
      if (!author) author = parts[1].trim();
    } else if (!title) {
      title = filename;
    }
  }

  return {
    title: title || "Unknown Title",
    author: author || "Unknown Author",
    isbn: isbn || undefined,
    publisher: publisher || undefined,
    copyright_year,
    file_path: filePath,
    file_format: format,
    total_characters: text.length,
    total_chapters: 0, // Will be updated after chapter detection
    parse_date: new Date().toISOString(),
  };
}

// === CHAPTER DETECTION ===

function detectChapters(text: string): Chapter[] {
  const chapters: Chapter[] = [];

  // Common chapter patterns
  const patterns = [
    /^(CHAPTER|Chapter)\s+(\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|[IVX]+)[:\.\s]*(.*)/gim,
    /^(\d+)\.\s+([A-Z][A-Za-z\s]+)$/gm, // "1. Chapter Title"
    /^(Part|PART)\s+(\d+|ONE|TWO|THREE|[IVX]+)[:\.\s]*(.*)/gim,
  ];

  for (const pattern of patterns) {
    let match;
    pattern.lastIndex = 0;

    while ((match = pattern.exec(text)) !== null) {
      const fullMatch = match[0];
      const position = match.index;

      // Extract chapter number
      let chapterNum = chapters.length + 1;
      const numStr = match[2];
      if (numStr) {
        const parsed = parseInt(numStr);
        if (!isNaN(parsed)) {
          chapterNum = parsed;
        } else {
          // Roman numeral or word conversion
          const wordMap: Record<string, number> = {
            ONE: 1, TWO: 2, THREE: 3, FOUR: 4, FIVE: 5,
            SIX: 6, SEVEN: 7, EIGHT: 8, NINE: 9, TEN: 10,
            ELEVEN: 11, TWELVE: 12, I: 1, II: 2, III: 3,
            IV: 4, V: 5, VI: 6, VII: 7, VIII: 8, IX: 9, X: 10,
          };
          chapterNum = wordMap[numStr.toUpperCase()] || chapters.length + 1;
        }
      }

      const title = match[3]?.trim() || fullMatch.trim();

      chapters.push({
        number: chapterNum,
        title: title,
        start_position: position,
        end_position: text.length, // Will be updated
      });
    }
  }

  // Sort by position and update end positions
  chapters.sort((a, b) => a.start_position - b.start_position);

  for (let i = 0; i < chapters.length - 1; i++) {
    chapters[i].end_position = chapters[i + 1].start_position;
  }

  return chapters;
}

// === TEXT CHUNKING ===

function chunkText(
  text: string,
  chapters: Chapter[],
  chunkSize: number,
  overlap: number
): TextChunk[] {
  const chunks: TextChunk[] = [];
  let chunkId = 0;

  // Start from the beginning — don't skip front matter, as it may contain
  // valuable content (forewords, prefaces, introductions, early chapters).
  // The original heuristic searched for "Chapter N" and skipped everything
  // before it, but this discards critical content in many books.
  let startPosition = 0;

  let position = startPosition;

  while (position < text.length) {
    const start = position;
    let end = Math.min(start + chunkSize, text.length);

    // Try to break at sentence boundaries
    if (end < text.length) {
      // Look backward for sentence ending
      for (let i = end; i > end - overlap && i > start + 100; i--) {
        const char = text[i];
        const nextChar = text[i + 1];
        if (
          (char === "." || char === "!" || char === "?") &&
          nextChar &&
          (nextChar === " " || nextChar === "\n")
        ) {
          end = i + 1;
          break;
        }
      }
    }

    // Also try to avoid breaking in middle of paragraph
    const lastParagraphBreak = text.lastIndexOf("\n\n", end);
    if (lastParagraphBreak > start + chunkSize / 2) {
      end = lastParagraphBreak;
    }

    const chunkText = text.slice(start, end);

    // Find which chapter this chunk belongs to
    let chapterNum: number | undefined;
    let chapterTitle: string | undefined;

    for (const chapter of chapters) {
      if (start >= chapter.start_position && start < chapter.end_position) {
        chapterNum = chapter.number;
        chapterTitle = chapter.title;
        break;
      }
    }

    chunks.push({
      id: `chunk-${chunkId}`,
      text: chunkText,
      start_position: start,
      end_position: end,
      chapter_number: chapterNum,
      chapter_title: chapterTitle,
    });

    // Move forward, accounting for overlap
    const advance = end - start - overlap;
    position += Math.max(advance, chunkSize / 2); // Ensure we always advance
    chunkId++;

    // Safety check
    if (position === start) {
      position += chunkSize;
    }
  }

  return chunks;
}

// === EPUB HANDLING ===

async function extractEpubText(filePath: string): Promise<string> {
  // Epub files are ZIP archives containing XHTML content files.
  // We unzip, read the OPF manifest to get spine order, then extract
  // text from each XHTML file in reading order.

  const tempDir = await Deno.makeTempDir({ prefix: "ea-epub-" });

  try {
    // Unzip the epub
    const unzip = new Deno.Command("unzip", {
      args: ["-o", "-q", filePath, "-d", tempDir],
      stdout: "piped",
      stderr: "piped",
    });
    const unzipResult = await unzip.output();
    if (!unzipResult.success) {
      const errText = new TextDecoder().decode(unzipResult.stderr);
      throw new Error(`Failed to unzip epub: ${errText}`);
    }

    // Find the OPF file (contains reading order)
    let opfPath = "";
    const containerPath = `${tempDir}/META-INF/container.xml`;
    try {
      const containerXml = await Deno.readTextFile(containerPath);
      const opfMatch = containerXml.match(/full-path="([^"]+)"/);
      if (opfMatch) {
        opfPath = `${tempDir}/${opfMatch[1]}`;
      }
    } catch {
      // No container.xml, search for .opf file
    }

    if (!opfPath) {
      // Fallback: find any .opf file
      for await (const entry of walkDir(tempDir)) {
        if (entry.name.endsWith(".opf")) {
          opfPath = entry.path;
          break;
        }
      }
    }

    // Get content files in spine order from OPF, or fallback to sorted html files
    let contentFiles: string[] = [];
    const opfDir = opfPath ? opfPath.substring(0, opfPath.lastIndexOf("/")) : tempDir;

    if (opfPath) {
      try {
        const opfXml = await Deno.readTextFile(opfPath);

        // Extract manifest items (id → href mapping)
        const manifest = new Map<string, string>();
        const itemRegex = /<item\s+[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"[^>]*?\/?\s*>/gi;
        let itemMatch;
        while ((itemMatch = itemRegex.exec(opfXml)) !== null) {
          manifest.set(itemMatch[1], itemMatch[2]);
        }

        // Extract spine order (list of itemrefs)
        const spineRegex = /<itemref\s+[^>]*?idref="([^"]+)"[^>]*?\/?\s*>/gi;
        let spineMatch;
        while ((spineMatch = spineRegex.exec(opfXml)) !== null) {
          const href = manifest.get(spineMatch[1]);
          if (href) {
            const fullPath = `${opfDir}/${decodeURIComponent(href)}`;
            contentFiles.push(fullPath);
          }
        }
      } catch {
        // OPF parsing failed, fall through to glob
      }
    }

    if (contentFiles.length === 0) {
      // Fallback: find all html/xhtml files and sort them
      for await (const entry of walkDir(tempDir)) {
        if (entry.name.match(/\.(x?html?)$/i)) {
          contentFiles.push(entry.path);
        }
      }
      contentFiles.sort();
    }

    // Extract text from each content file in order
    const textParts: string[] = [];
    for (const file of contentFiles) {
      try {
        const html = await Deno.readTextFile(file);
        const text = stripHtml(html);
        if (text.trim().length > 0) {
          textParts.push(text.trim());
        }
      } catch {
        // Skip unreadable files
      }
    }

    if (textParts.length === 0) {
      throw new Error("No readable content found in epub");
    }

    return textParts.join("\n\n");
  } finally {
    // Clean up temp directory
    try {
      await Deno.remove(tempDir, { recursive: true });
    } catch {
      // Best effort cleanup
    }
  }
}

/** Walk a directory recursively, yielding file entries */
async function* walkDir(
  dir: string
): AsyncGenerator<{ path: string; name: string }> {
  for await (const entry of Deno.readDir(dir)) {
    const fullPath = `${dir}/${entry.name}`;
    if (entry.isDirectory) {
      yield* walkDir(fullPath);
    } else if (entry.isFile) {
      yield { path: fullPath, name: entry.name };
    }
  }
}

/** Strip HTML tags and decode common entities, preserving paragraph structure */
function stripHtml(html: string): string {
  return html
    // Remove script/style blocks entirely
    .replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, "")
    // Convert <br>, <p>, <div>, heading, and <li> tags to newlines
    .replace(/<\/(p|div|h[1-6]|li|tr|blockquote)>/gi, "\n\n")
    .replace(/<br\s*\/?>/gi, "\n")
    // Remove remaining HTML tags
    .replace(/<[^>]+>/g, " ")
    // Decode common HTML entities
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#(\d+);/g, (_m, code) => String.fromCharCode(parseInt(code)))
    .replace(/&apos;/gi, "'")
    // Collapse excessive whitespace within lines
    .replace(/[ \t]+/g, " ")
    // Collapse excessive blank lines
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// === EXPORTS FOR MODULE USE ===

export {
  extractMetadata,
  detectChapters,
  chunkText,
  extractEpubText,
};

export type {
  BookMetadata,
  Chapter,
  TextChunk,
  ParsedBook,
};

/**
 * Parse a book file and return structured data.
 * This is the main entry point for programmatic use.
 */
export async function parseBook(
  filePath: string,
  options: {
    chunkSize?: number;
    overlap?: number;
    format?: "txt" | "epub";
  } = {}
): Promise<ParsedBook> {
  const { chunkSize = 1000, overlap = 100 } = options;
  const format: "txt" | "epub" = options.format ||
    (filePath.toLowerCase().endsWith(".epub") ? "epub" : "txt");

  let text: string;
  if (format === "epub") {
    text = await extractEpubText(filePath);
  } else {
    text = await Deno.readTextFile(filePath);
  }

  const metadata = extractMetadata(text, filePath, format);
  const chapters = detectChapters(text);
  metadata.total_chapters = chapters.length;

  const chunks = chunkText(text, chapters, chunkSize, overlap);

  return {
    metadata,
    chapters,
    chunks,
  };
}

// === MAIN (CLI) ===

async function main(): Promise<void> {
  const args = Deno.args;

  // Help
  if (args.includes("--help") || args.includes("-h") || args.length === 0) {
    console.log(`ea-parse.ts - Ebook Parsing and Chunking

Usage:
  deno run --allow-read scripts/ea-parse.ts <file> [options]

Arguments:
  file                 Path to ebook file (txt or epub)

Options:
  --chunk-size <n>     Characters per chunk (default: 1000)
  --overlap <n>        Overlap between chunks (default: 100)
  --format <fmt>       Force format: txt or epub (auto-detect if not specified)
  --output <file>      Write JSON to file instead of stdout
  --json               Output as JSON (default)
  --summary            Output summary only, not full chunks

Examples:
  deno run --allow-read scripts/ea-parse.ts book.txt
  deno run --allow-read scripts/ea-parse.ts book.txt --chunk-size 1500 --overlap 150
  deno run --allow-read scripts/ea-parse.ts book.epub --output parsed.json
`);
    Deno.exit(0);
  }

  // Parse arguments
  const chunkSizeIdx = args.indexOf("--chunk-size");
  const chunkSize = chunkSizeIdx !== -1 ? parseInt(args[chunkSizeIdx + 1]) : 1000;

  const overlapIdx = args.indexOf("--overlap");
  const overlap = overlapIdx !== -1 ? parseInt(args[overlapIdx + 1]) : 100;

  const formatIdx = args.indexOf("--format");
  const forcedFormat = formatIdx !== -1 ? args[formatIdx + 1] as "txt" | "epub" : null;

  const outputIdx = args.indexOf("--output");
  const outputFile = outputIdx !== -1 ? args[outputIdx + 1] : null;

  const summaryOnly = args.includes("--summary");

  // Find file argument (first non-flag argument)
  const skipIndices = new Set<number>();
  if (chunkSizeIdx !== -1) {
    skipIndices.add(chunkSizeIdx);
    skipIndices.add(chunkSizeIdx + 1);
  }
  if (overlapIdx !== -1) {
    skipIndices.add(overlapIdx);
    skipIndices.add(overlapIdx + 1);
  }
  if (formatIdx !== -1) {
    skipIndices.add(formatIdx);
    skipIndices.add(formatIdx + 1);
  }
  if (outputIdx !== -1) {
    skipIndices.add(outputIdx);
    skipIndices.add(outputIdx + 1);
  }

  let filePath: string | null = null;
  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith("--") && !skipIndices.has(i)) {
      filePath = args[i];
      break;
    }
  }

  if (!filePath) {
    console.error("Error: No input file specified");
    Deno.exit(1);
  }

  // Detect format
  const format: "txt" | "epub" = forcedFormat ||
    (filePath.toLowerCase().endsWith(".epub") ? "epub" : "txt");

  // Read file
  let text: string;
  try {
    if (format === "epub") {
      text = await extractEpubText(filePath);
    } else {
      text = await Deno.readTextFile(filePath);
    }
  } catch (e) {
    console.error(`Error reading file: ${e}`);
    Deno.exit(1);
  }

  // Process
  const metadata = extractMetadata(text, filePath, format);
  const chapters = detectChapters(text);
  metadata.total_chapters = chapters.length;

  const chunks = chunkText(text, chapters, chunkSize, overlap);

  const result: ParsedBook = {
    metadata,
    chapters,
    chunks,
  };

  // Output
  let output: string;
  if (summaryOnly) {
    output = JSON.stringify({
      metadata,
      chapters,
      chunk_count: chunks.length,
      chunk_size: chunkSize,
      overlap: overlap,
    }, null, 2);
  } else {
    output = JSON.stringify(result, null, 2);
  }

  if (outputFile) {
    await Deno.writeTextFile(outputFile, output);
    console.log(`Parsed output written to: ${outputFile}`);
    console.log(`  - ${chunks.length} chunks created`);
    console.log(`  - ${chapters.length} chapters detected`);
    console.log(`  - ${metadata.total_characters} total characters`);
  } else {
    console.log(output);
  }
}

// Only run main() when executed directly, not when imported
if (import.meta.main) {
  main();
}

import { useState } from "react";

const LAYERS = [
  {
    id: "ingest",
    label: "01 — INGEST",
    title: "Document Ingestion",
    color: "#E8FFF0",
    accent: "#22C55E",
    border: "#16A34A",
    components: [
      {
        name: "Source Docs",
        desc: "Markdown, PDF, HTML from open-source networking repos, RFCs, vendor docs",
        tech: "File system / Git repos",
      },
      {
        name: "Loader",
        desc: "Reads files, extracts text, normalizes formatting",
        tech: "LangChain DocumentLoaders or Unstructured.io",
      },
      {
        name: "Chunker",
        desc: "Splits docs into overlapping chunks (512-1024 tokens, 20% overlap)",
        tech: "RecursiveCharacterTextSplitter",
      },
    ],
    notes: "Domain-agnostic: swap /docs/networking/ for /docs/anything/",
  },
  {
    id: "embed",
    label: "02 — EMBED",
    title: "Vectorization",
    color: "#EEF0FF",
    accent: "#6366F1",
    border: "#4F46E5",
    components: [
      {
        name: "Embedding Model",
        desc: "Converts text chunks into 384-dim vectors that capture semantic meaning",
        tech: "all-MiniLM-L6-v2 (runs on CPU, ~80MB)",
      },
      {
        name: "Vector Store",
        desc: "Stores and indexes embeddings for fast similarity search",
        tech: "ChromaDB (local, no server needed)",
      },
      {
        name: "Metadata Tags",
        desc: "Source file, domain, doc type, section headers stored alongside vectors",
        tech: "Key-value pairs in Chroma",
      },
    ],
    notes: "All runs locally on your MacBook — no GPU required",
  },
  {
    id: "retrieve",
    label: "03 — RETRIEVE",
    title: "Query & Retrieval",
    color: "#FFF7ED",
    accent: "#F59E0B",
    border: "#D97706",
    components: [
      {
        name: "Query Embedding",
        desc: "Your question gets embedded with the same model as your docs",
        tech: "Same MiniLM model",
      },
      {
        name: "Similarity Search",
        desc: "Finds top-k most relevant chunks (cosine similarity)",
        tech: "ChromaDB .query(n_results=5)",
      },
      {
        name: "Re-Ranker (optional)",
        desc: "Second pass to re-score results for higher precision",
        tech: "cross-encoder/ms-marco-MiniLM-L-6-v2",
      },
    ],
    notes: "Retrieval quality = answer quality. This is where you tune.",
  },
  {
    id: "generate",
    label: "04 — GENERATE",
    title: "Augmented Generation",
    color: "#FDF2F8",
    accent: "#EC4899",
    border: "#DB2777",
    components: [
      {
        name: "Prompt Builder",
        desc: "Injects retrieved chunks into a system prompt template with your question",
        tech: "Python string template / Jinja2",
      },
      {
        name: "Claude API",
        desc: "Sends augmented prompt to Claude for reasoning and response",
        tech: "anthropic Python SDK (Sonnet for speed, Opus for depth)",
      },
      {
        name: "Response + Sources",
        desc: "Returns answer with citations back to the source chunks",
        tech: "CLI output or simple web UI",
      },
    ],
    notes: "Claude does the thinking — RAG just gives it the right context",
  },
];

const FILE_TREE = `rag-engine/
├── config.yaml          # Domains, paths, model settings
├── ingest/
│   ├── loader.py        # File readers (md, pdf, html)
│   ├── chunker.py       # Splitting logic
│   └── pipeline.py      # Orchestrates ingest
├── embed/
│   ├── embedder.py      # Embedding model wrapper
│   └── store.py         # ChromaDB operations
├── retrieve/
│   ├── query.py         # Search + optional re-rank
│   └── prompt.py        # Template builder
├── generate/
│   └── claude_client.py # API call + response formatting
├── domains/
│   └── networking/      # ← Swap this folder for any domain
│       ├── rfcs/
│       ├── linux-networking/
│       ├── troubleshooting/
│       └── vendor-docs/
├── cli.py               # Main entry point
└── requirements.txt`;

export default function RAGArchitecture() {
  const [activeLayer, setActiveLayer] = useState(null);
  const [view, setView] = useState("pipeline");

  return (
    <div style={{
      fontFamily: "'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace",
      color: "#1a1a2e",
      padding: "32px 24px",
      maxWidth: 780,
      margin: "0 auto",
      lineHeight: 1.6,
    }}>
      <div style={{ marginBottom: 32 }}>
        <div style={{
          fontSize: 11,
          letterSpacing: 3,
          color: "#6366F1",
          textTransform: "uppercase",
          marginBottom: 6,
          fontWeight: 600,
        }}>
          Architecture Blueprint
        </div>
        <h1 style={{
          fontSize: 26,
          fontWeight: 700,
          margin: 0,
          letterSpacing: -0.5,
          color: "#0f172a",
        }}>
          Domain-Agnostic RAG Pipeline
        </h1>
        <p style={{
          fontSize: 13,
          color: "#64748b",
          margin: "8px 0 0",
        }}>
          Local-first retrieval augmented generation — swap domains, keep the engine
        </p>
      </div>

      {/* Tab switcher */}
      <div style={{
        display: "flex",
        gap: 2,
        marginBottom: 28,
        background: "#f1f5f9",
        borderRadius: 8,
        padding: 3,
        width: "fit-content",
      }}>
        {[
          ["pipeline", "Pipeline"],
          ["project", "Project Structure"],
          ["stack", "Tech Stack"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setView(key)}
            style={{
              padding: "8px 18px",
              fontSize: 12,
              fontWeight: 600,
              fontFamily: "inherit",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              background: view === key ? "#fff" : "transparent",
              color: view === key ? "#0f172a" : "#64748b",
              boxShadow: view === key ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
              transition: "all 0.2s",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Pipeline View */}
      {view === "pipeline" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {LAYERS.map((layer, i) => {
            const isActive = activeLayer === layer.id;
            return (
              <div key={layer.id}>
                <div
                  onClick={() => setActiveLayer(isActive ? null : layer.id)}
                  style={{
                    background: isActive ? layer.color : "#fff",
                    border: `2px solid ${isActive ? layer.border : "#e2e8f0"}`,
                    borderRadius: 12,
                    padding: "18px 22px",
                    cursor: "pointer",
                    transition: "all 0.25s ease",
                  }}
                >
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}>
                    <div>
                      <span style={{
                        fontSize: 10,
                        fontWeight: 700,
                        letterSpacing: 2,
                        color: layer.accent,
                        textTransform: "uppercase",
                      }}>
                        {layer.label}
                      </span>
                      <div style={{
                        fontSize: 17,
                        fontWeight: 700,
                        marginTop: 2,
                        color: "#0f172a",
                      }}>
                        {layer.title}
                      </div>
                    </div>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: layer.accent,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#fff",
                      fontSize: 14,
                      fontWeight: 700,
                      transition: "transform 0.2s",
                      transform: isActive ? "rotate(45deg)" : "rotate(0)",
                    }}>
                      +
                    </div>
                  </div>

                  {isActive && (
                    <div style={{ marginTop: 18 }}>
                      {layer.components.map((comp, j) => (
                        <div
                          key={j}
                          style={{
                            background: "rgba(255,255,255,0.8)",
                            borderRadius: 8,
                            padding: "14px 16px",
                            marginBottom: j < layer.components.length - 1 ? 10 : 0,
                            borderLeft: `3px solid ${layer.accent}`,
                          }}
                        >
                          <div style={{
                            fontSize: 13,
                            fontWeight: 700,
                            color: "#0f172a",
                          }}>
                            {comp.name}
                          </div>
                          <div style={{
                            fontSize: 12,
                            color: "#475569",
                            marginTop: 4,
                          }}>
                            {comp.desc}
                          </div>
                          <div style={{
                            fontSize: 11,
                            color: layer.accent,
                            fontWeight: 600,
                            marginTop: 6,
                            background: `${layer.accent}15`,
                            display: "inline-block",
                            padding: "2px 8px",
                            borderRadius: 4,
                          }}>
                            {comp.tech}
                          </div>
                        </div>
                      ))}
                      <div style={{
                        marginTop: 12,
                        fontSize: 11,
                        color: "#64748b",
                        fontStyle: "italic",
                        padding: "8px 12px",
                        background: "rgba(255,255,255,0.5)",
                        borderRadius: 6,
                      }}>
                        💡 {layer.notes}
                      </div>
                    </div>
                  )}
                </div>

                {i < LAYERS.length - 1 && (
                  <div style={{
                    display: "flex",
                    justifyContent: "center",
                    padding: "4px 0",
                  }}>
                    <div style={{
                      width: 2,
                      height: 16,
                      background: "#cbd5e1",
                    }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Project Structure View */}
      {view === "project" && (
        <div style={{
          background: "#0f172a",
          borderRadius: 12,
          padding: "24px 28px",
          color: "#e2e8f0",
          fontSize: 13,
          lineHeight: 1.8,
          overflow: "auto",
        }}>
          <div style={{
            fontSize: 10,
            letterSpacing: 2,
            color: "#6366F1",
            textTransform: "uppercase",
            fontWeight: 600,
            marginBottom: 16,
          }}>
            Project Layout
          </div>
          <pre style={{
            margin: 0,
            fontFamily: "inherit",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}>
            {FILE_TREE}
          </pre>
          <div style={{
            marginTop: 20,
            padding: "14px 16px",
            background: "#1e293b",
            borderRadius: 8,
            borderLeft: "3px solid #22C55E",
            fontSize: 12,
            color: "#94a3b8",
          }}>
            <strong style={{ color: "#22C55E" }}>Key insight:</strong> The{" "}
            <code style={{
              background: "#334155",
              padding: "1px 6px",
              borderRadius: 3,
            }}>
              domains/
            </code>{" "}
            folder is where modularity lives. Drop in a new folder of docs, re-run ingest, and your RAG now knows a new domain. Everything upstream stays the same.
          </div>
        </div>
      )}

      {/* Tech Stack View */}
      {view === "stack" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[
            {
              cat: "Language",
              pick: "Python 3.10+",
              why: "Best ecosystem for ML/AI tooling, LangChain, and the Anthropic SDK",
            },
            {
              cat: "Embedding Model",
              pick: "all-MiniLM-L6-v2",
              why: "Only ~80MB, runs on CPU, solid quality for retrieval tasks — perfect for your MacBook",
            },
            {
              cat: "Vector Store",
              pick: "ChromaDB",
              why: "Zero-config, runs locally as a Python library, persistent storage, good docs",
            },
            {
              cat: "Orchestration",
              pick: "LangChain (lightweight)",
              why: "Use only the loaders + splitters — avoid over-abstracting. You can strip it out later.",
            },
            {
              cat: "LLM",
              pick: "Claude API (Sonnet default)",
              why: "Sonnet for fast Q&A, Opus for deep troubleshooting — model is a config switch",
            },
            {
              cat: "Interface",
              pick: "CLI first → simple web UI later",
              why: "Start with a terminal tool. Add a Streamlit or Flask UI when the pipeline works.",
            },
            {
              cat: "Re-ranker (Phase 2)",
              pick: "cross-encoder/ms-marco-MiniLM-L-6-v2",
              why: "Second-pass scoring to boost precision. Add once base retrieval is working.",
            },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                background: "#fff",
                border: "2px solid #e2e8f0",
                borderRadius: 10,
                padding: "14px 18px",
                display: "grid",
                gridTemplateColumns: "130px 1fr",
                gap: "4px 16px",
                alignItems: "start",
              }}
            >
              <div style={{
                fontSize: 10,
                fontWeight: 700,
                letterSpacing: 1.5,
                color: "#6366F1",
                textTransform: "uppercase",
                paddingTop: 2,
              }}>
                {item.cat}
              </div>
              <div>
                <div style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: "#0f172a",
                }}>
                  {item.pick}
                </div>
                <div style={{
                  fontSize: 12,
                  color: "#64748b",
                  marginTop: 2,
                }}>
                  {item.why}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Build phases */}
      <div style={{
        marginTop: 32,
        padding: "20px 22px",
        background: "#f8fafc",
        borderRadius: 12,
        border: "1px solid #e2e8f0",
      }}>
        <div style={{
          fontSize: 10,
          letterSpacing: 2,
          color: "#64748b",
          textTransform: "uppercase",
          fontWeight: 600,
          marginBottom: 14,
        }}>
          Build Order
        </div>
        {[
          ["Phase 1", "Ingest + Embed", "Get docs chunked and into ChromaDB"],
          ["Phase 2", "Retrieve + CLI", "Query from terminal, see raw retrieved chunks"],
          ["Phase 3", "Claude Integration", "Wire retrieval into Claude API prompts"],
          ["Phase 4", "Tune + Expand", "Adjust chunking, add re-ranker, new domains"],
        ].map(([phase, title, desc], i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 14,
              alignItems: "flex-start",
              marginBottom: i < 3 ? 14 : 0,
            }}
          >
            <div style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#6366F1",
              background: "#EEF0FF",
              padding: "3px 8px",
              borderRadius: 4,
              whiteSpace: "nowrap",
              marginTop: 1,
            }}>
              {phase}
            </div>
            <div>
              <span style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>
                {title}
              </span>
              <span style={{ fontSize: 12, color: "#64748b" }}> — {desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

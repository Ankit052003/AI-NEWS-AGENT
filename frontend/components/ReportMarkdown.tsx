import type { ReactNode } from "react";

type ReportMarkdownProps = {
  content: string;
};

type ListState = {
  type: "ul" | "ol";
  items: ReactNode[];
};

export function ReportMarkdown({ content }: ReportMarkdownProps) {
  const lines = content.split("\n");
  const blocks: ReactNode[] = [];
  let list: ListState | null = null;

  const flushList = () => {
    if (!list) {
      return;
    }

    const ListTag = list.type;
    blocks.push(
      <ListTag
        className={
          list.type === "ol"
            ? "my-3 list-decimal space-y-2 pl-5 text-sm leading-6 text-neutral-700"
            : "my-3 list-disc space-y-2 pl-5 text-sm leading-6 text-neutral-700"
        }
        key={`list-${blocks.length}`}
      >
        {list.items}
      </ListTag>,
    );
    list = null;
  };

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();

    if (!line) {
      flushList();
      return;
    }

    if (line.startsWith("# ")) {
      flushList();
      blocks.push(
        <h1
          className="mb-4 mt-1 text-2xl font-semibold text-neutral-950"
          key={index}
        >
          {renderInline(line.slice(2))}
        </h1>,
      );
      return;
    }

    if (line.startsWith("## ")) {
      flushList();
      blocks.push(
        <h2
          className="mb-2 mt-6 text-lg font-semibold text-neutral-950"
          key={index}
        >
          {renderInline(line.slice(3))}
        </h2>,
      );
      return;
    }

    if (line.startsWith("- ")) {
      if (!list || list.type !== "ul") {
        flushList();
        list = { type: "ul", items: [] };
      }
      list.items.push(<li key={index}>{renderInline(line.slice(2))}</li>);
      return;
    }

    const orderedMatch = line.match(/^\d+\.\s+(.+)$/);
    if (orderedMatch) {
      if (!list || list.type !== "ol") {
        flushList();
        list = { type: "ol", items: [] };
      }
      list.items.push(<li key={index}>{renderInline(orderedMatch[1])}</li>);
      return;
    }

    flushList();
    blocks.push(
      <p className="my-3 text-sm leading-6 text-neutral-700" key={index}>
        {renderInline(line)}
      </p>,
    );
  });

  flushList();

  return <div>{blocks}</div>;
}

function renderInline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const linkPattern = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = linkPattern.exec(text))) {
    if (match.index > lastIndex) {
      nodes.push(...renderBold(text.slice(lastIndex, match.index), nodes.length));
    }

    nodes.push(
      <a
        className="font-medium text-teal-700 underline decoration-teal-200 underline-offset-4 hover:text-teal-900"
        href={match[2]}
        key={`link-${nodes.length}`}
        rel="noreferrer"
        target="_blank"
      >
        {match[1]}
      </a>,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    nodes.push(...renderBold(text.slice(lastIndex), nodes.length));
  }

  return nodes;
}

function renderBold(text: string, keyOffset: number): ReactNode[] {
  const nodes: ReactNode[] = [];
  const boldPattern = /\*\*([^*]+)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = boldPattern.exec(text))) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    nodes.push(
      <strong className="font-semibold text-neutral-950" key={keyOffset + nodes.length}>
        {match[1]}
      </strong>,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes;
}

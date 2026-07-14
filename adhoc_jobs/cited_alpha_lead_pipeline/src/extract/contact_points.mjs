import { parse } from "parse5";
import { domainToASCII } from "node:url";

const EMAIL_PATTERN = /\b[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+\b/gi;
const FREE_MAIL_DOMAINS = new Set([
  "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "msn.com",
  "yahoo.com", "icloud.com", "me.com", "proton.me", "protonmail.com", "hey.com", "aol.com"
]);
const GENERIC_LOCAL_PARTS = new Set([
  "contact", "hello", "info", "research", "press", "media", "partnerships", "business",
  "sales", "support", "team", "office", "editor", "editorial", "inquiries", "enquiries"
]);
const RELEVANT_PATH = /(about|contact|team|author|research|press|media|partner|consult|company|people|leadership)/i;
const BUSINESS_CONTEXT = /(contact|inquir|business|research|press|media|partner|consult|speaking|work with|reach me)/i;
const BOOKING_HOSTS = ["cal.com", "calendly.com", "savvycal.com", "meetings.hubspot.com"];

function attr(node, name) {
  return node.attrs?.find((candidate) => candidate.name.toLowerCase() === name)?.value ?? "";
}

function walk(node, visitor, excluded = false) {
  const tag = node.tagName?.toLowerCase();
  const nextExcluded = excluded || ["script", "style", "noscript", "template"].includes(tag);
  if (!nextExcluded) visitor(node);
  for (const child of node.childNodes ?? []) walk(child, visitor, nextExcluded);
}

function normalizeEmail(value) {
  let decoded;
  try { decoded = decodeURIComponent(String(value).split("?")[0]); } catch { return ""; }
  const cleaned = decoded.trim().toLowerCase().replace(/^mailto:/, "");
  const at = cleaned.lastIndexOf("@");
  if (at <= 0) return "";
  const domain = domainToASCII(cleaned.slice(at + 1));
  return domain ? `${cleaned.slice(0, at)}@${domain}` : "";
}

export function classifyEmail(email, canonicalDomain, businessContext = false) {
  const [localPart, domain] = email.split("@");
  if (!localPart || !domain) return "invalid";
  if (FREE_MAIL_DOMAINS.has(domain)) return businessContext ? "public_creator_email" : "personal_email";
  if (domain !== canonicalDomain && !domain.endsWith(`.${canonicalDomain}`)) return "external_work_email";
  return GENERIC_LOCAL_PARTS.has(localPart) ? "role_business_email" : "named_work_email";
}

function endpointKey(endpoint) {
  return `${endpoint.contactType}:${endpoint.contactValue.toLowerCase()}`;
}

export function extractContactPoints(html, pageUrl, canonicalDomain) {
  const document = parse(html);
  const textParts = [];
  const rawLinks = [];
  const forms = [];

  const subtreeText = (node) => {
    const parts = [];
    walk(node, (child) => {
      if (child.nodeName === "#text" && child.value?.trim()) parts.push(child.value.trim());
    });
    return parts.join(" ");
  };
  const subtreeHasEmailInput = (node) => {
    let found = false;
    walk(node, (child) => {
      if (child.tagName?.toLowerCase() === "input" && attr(child, "type").toLowerCase() === "email") found = true;
    });
    return found;
  };

  walk(document, (node) => {
    if (node.nodeName === "#text" && node.value?.trim()) textParts.push(node.value.trim());
    if (node.tagName?.toLowerCase() === "a" && attr(node, "href")) rawLinks.push(attr(node, "href"));
    if (node.tagName?.toLowerCase() === "form") {
      forms.push({
        action: attr(node, "action"),
        hasEmail: subtreeHasEmailInput(node),
        intent: [attr(node, "id"), attr(node, "class"), attr(node, "name"), attr(node, "action"), subtreeText(node)].join(" ")
      });
    }
  });

  const visibleText = textParts.join(" ").replace(/\s+/g, " ");
  const businessContext = BUSINESS_CONTEXT.test(visibleText) || RELEVANT_PATH.test(new URL(pageUrl).pathname);
  const endpoints = [];
  const internalLinks = new Set();

  const addEmail = (raw, evidenceType) => {
    const email = normalizeEmail(raw);
    if (!email || !EMAIL_PATTERN.test(email)) {
      EMAIL_PATTERN.lastIndex = 0;
      return;
    }
    EMAIL_PATTERN.lastIndex = 0;
    const creatorContext = businessContext && (evidenceType === "mailto" || evidenceType === "deobfuscated_visible_text" || RELEVANT_PATH.test(new URL(pageUrl).pathname));
    endpoints.push({
      contactType: classifyEmail(email, canonicalDomain, creatorContext),
      contactValue: email,
      sourceUrl: pageUrl,
      sourceType: "official_website",
      evidenceType
    });
  };

  for (const match of visibleText.matchAll(EMAIL_PATTERN)) addEmail(match[0], "visible_text");
  const deobfuscated = visibleText
    .replace(/\s*(?:\[at\]|\(at\)|\sat\s)\s*/gi, "@")
    .replace(/\s*(?:\[dot\]|\(dot\)|\sdot\s)\s*/gi, ".");
  if (deobfuscated !== visibleText) {
    for (const match of deobfuscated.matchAll(EMAIL_PATTERN)) addEmail(match[0], "deobfuscated_visible_text");
  }

  for (const href of rawLinks) {
    if (/^mailto:/i.test(href)) {
      addEmail(href, "mailto");
      continue;
    }
    let url;
    try {
      url = new URL(href, pageUrl);
    } catch {
      continue;
    }
    if (!["http:", "https:"].includes(url.protocol)) continue;
    url.hash = "";
    const hostname = url.hostname.toLowerCase().replace(/^www\./, "");
    if (hostname === canonicalDomain || hostname === `www.${canonicalDomain}`) {
      if (RELEVANT_PATH.test(url.pathname)) internalLinks.add(url.href);
      continue;
    }
    if (["x.com", "twitter.com"].includes(hostname)) {
      endpoints.push({ contactType: "x_profile", contactValue: url.href, sourceUrl: pageUrl, sourceType: "official_website", evidenceType: "official_outbound_link" });
    } else if (hostname === "linkedin.com" || hostname.endsWith(".linkedin.com")) {
      endpoints.push({ contactType: "linkedin_profile", contactValue: url.href, sourceUrl: pageUrl, sourceType: "official_website", evidenceType: "official_outbound_link" });
    } else if (BOOKING_HOSTS.some((host) => hostname === host || hostname.endsWith(`.${host}`))) {
      endpoints.push({ contactType: "booking_url", contactValue: url.href, sourceUrl: pageUrl, sourceType: "official_website", evidenceType: "official_outbound_link" });
    }
  }

  const pageIsContact = /contact|inquir|demo|consult|book|request/i.test(new URL(pageUrl).pathname);
  const contactForms = forms.filter((form) => {
    const intent = form.intent.toLowerCase();
    const contactIntent = /contact|inquir|message|demo|consult|book|request|business/.test(intent);
    const subscriptionOnly = /subscribe|newsletter|sign[ -]?up|login|sign[ -]?in/.test(intent) && !contactIntent;
    return !subscriptionOnly && (pageIsContact || contactIntent) && form.hasEmail;
  });
  if (contactForms.length > 0 || (pageIsContact && forms.length === 0)) {
    const form = contactForms[0];
    let formUrl = pageUrl;
    if (form?.action) {
      try {
        const actionUrl = new URL(form.action, pageUrl);
        const host = actionUrl.hostname.toLowerCase().replace(/^www\./, "");
        if (["http:", "https:"].includes(actionUrl.protocol) && host === canonicalDomain) formUrl = actionUrl.href;
      } catch { formUrl = pageUrl; }
    }
    endpoints.push({ contactType: "contact_form", contactValue: formUrl, sourceUrl: pageUrl, sourceType: "official_website", evidenceType: "html_form_or_contact_page" });
  }

  const deduped = [...new Map(endpoints.map((endpoint) => [endpointKey(endpoint), endpoint])).values()];
  return { endpoints: deduped, internalLinks: [...internalLinks], visibleText };
}

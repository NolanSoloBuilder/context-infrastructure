import { useEffect, useRef, useState } from "react";
import { ArrowUp, CircleArrowRight } from "lucide-react";
import {
  ArrowCircleLeft,
  ArrowCircleRight,
  ArrowSquareOut,
  Brain,
  Briefcase,
  Command,
  Cpu,
  EnvelopeSimple,
  GithubLogo,
  GlobeHemisphereEast,
  LinkedinLogo,
  MapPin,
  NotePencil,
  Sparkle,
  Stack,
  TerminalWindow,
  Wrench,
  XLogo,
} from "@phosphor-icons/react";
import { focusAreas, nowItems, profile, projects } from "./content.js";

const screens = ["hello", "portfolio", "work", "now", "end"];

const iconMap = {
  "Cited Alpha": Brain,
  "CHINA METRO TYPING": GlobeHemisphereEast,
  "Mindspace Workspace": Stack,
  "AI Tool Environment Sync": TerminalWindow,
  "Automation Lab": Wrench,
};

function getScreenFromHash() {
  const index = screens.indexOf(window.location.hash.replace("#", ""));
  return index < 0 ? 0 : index;
}

function SocialLink({ label, href, children, disabled = false }) {
  if (disabled) {
    return (
      <span className="social-button is-disabled" aria-label={`${label}，待补充`} title={`${label} · 待补充`}>
        {children}
      </span>
    );
  }

  return (
    <a className="social-button" aria-label={label} href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  );
}

function Intro({ onEnter }) {
  return (
    <section className="screen intro-screen" aria-labelledby="intro-name">
      <header className="intro-header">
        <h1 id="intro-name" className="name-chip">{profile.name} · {profile.englishName}</h1>
        <nav className="social-links" aria-label="Social links">
          <SocialLink label="GitHub" href={profile.github}><GithubLogo weight="fill" /></SocialLink>
          <SocialLink label="LinkedIn" disabled><LinkedinLogo weight="fill" /></SocialLink>
          <SocialLink label="X" disabled><XLogo weight="fill" /></SocialLink>
          <SocialLink label="Notes" disabled><NotePencil weight="fill" /></SocialLink>
        </nav>
      </header>

      <div className="intro-copy">
        <p className="intro-hello">Hello</p>
        <p className="intro-identity">I&apos;m <mark>{profile.englishName}</mark></p>
      </div>
      <div className="about-action">
        <button className="about-button" type="button" onClick={onEnter}>
          About Me <CircleArrowRight aria-hidden="true" />
        </button>
      </div>
      <div className="click-hint" aria-hidden="true">
        <div className="click-hint-content">
          <ArrowUp strokeWidth={3.5} />
          <span>Click</span>
        </div>
      </div>
    </section>
  );
}

function PageHeader({ title, onBack, onNext }) {
  return (
    <header className="page-header">
      <button className="page-arrow" type="button" onClick={onBack} aria-label="Previous section">
        <ArrowCircleLeft weight="bold" />
      </button>
      <h2><span>{title}</span></h2>
      <button className="page-arrow" type="button" onClick={onNext} aria-label="Next section">
        <ArrowCircleRight weight="bold" />
      </button>
    </header>
  );
}

function ProfilePanel() {
  return (
    <div className="profile-panel">
      <div className="avatar-monogram" aria-label="Xu Hao monogram">XH</div>
      <div className="profile-copy">
        <p className="eyebrow">{profile.publicName}</p>
        <h3>Hi, I&apos;m {profile.englishName}</h3>
        <ul className="profile-meta">
          <li><MapPin weight="bold" /> {profile.location}</li>
          <li><Cpu weight="bold" /> {profile.role}</li>
          <li><Sparkle weight="bold" /> {profile.headline}</li>
          <li><GithubLogo weight="bold" /><a href={profile.github} target="_blank" rel="noreferrer">{profile.githubLabel}</a></li>
        </ul>
        <p className="profile-bio">{profile.bio}</p>

        <div className="focus-list">
          <h4>Current Focus</h4>
          {focusAreas.map((item) => (
            <article key={item.title}>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}

function MiniProjects() {
  return (
    <div className={`mini-projects${projects.length === 0 ? " is-empty" : ""}`}>
      <p className="eyebrow">Selected projects</p>
      {projects.slice(0, 3).map((project) => (
        <article key={project.title}>
          <strong>{project.title}</strong>
          <span>{project.tag}</span>
          <p>{project.description}</p>
          <a className="mini-project-link" href={project.url} target="_blank" rel="noreferrer" aria-label={`View ${project.title} live`}>
            View live <ArrowSquareOut weight="bold" />
          </a>
        </article>
      ))}
    </div>
  );
}

function Toolbox() {
  return (
    <div className="toolbox-panel">
      <p className="eyebrow">Working style</p>
      <h3>Build the whole system</h3>
      <div className="toolbox-grid">
        <span>Product judgment</span><span>Frontend</span><span>Backend</span>
        <span>AI agents</span><span>Deployment</span><span>Live verification</span>
      </div>
      <p>Interfaces, contracts, data, runtime behavior, and acceptance evidence belong to one delivery loop.</p>
    </div>
  );
}

function Portfolio({ onBack, onNext }) {
  const [panel, setPanel] = useState("profile");
  const panels = { profile: <ProfilePanel />, projects: <MiniProjects />, toolbox: <Toolbox /> };

  return (
    <section className="screen page-screen portfolio-screen" aria-labelledby="portfolio-title">
      <PageHeader title="My Portfolio" onBack={onBack} onNext={onNext} />
      <div className="desktop-stage">
        <div className="browser-window">
          <div className="window-bar">
            <div className="traffic-lights" aria-hidden="true"><i /><i /><i /></div>
            <span className="window-title">finder</span>
            <span />
          </div>
          <div className="window-content" aria-live="polite">{panels[panel]}</div>
        </div>

        <nav className="dock" aria-label="Portfolio shortcuts">
          <button type="button" onClick={() => setPanel("profile")} aria-label="About Xu Hao"><img src="/assets/finder.png" alt="" /></button>
          <button type="button" onClick={() => setPanel("projects")} aria-label="Selected projects"><img src="/assets/photo.png" alt="" /></button>
          <button type="button" onClick={() => setPanel("toolbox")} aria-label="Working style"><img src="/assets/instagram.webp" alt="" /></button>
          <a href={profile.github} target="_blank" rel="noreferrer" aria-label="Open GitHub"><img src="/assets/github.webp" alt="" /></a>
          <button type="button" onClick={() => setPanel("toolbox")} aria-label="Toolbox"><img src="/assets/raycast.png" alt="" /></button>
          <button type="button" onClick={onNext} aria-label="Selected work"><img src="/assets/flightcn.png" alt="" /></button>
          <button type="button" onClick={() => setPanel("projects")} aria-label="Context infrastructure"><img src="/assets/subflow.png" alt="" /></button>
          <button type="button" onClick={onNext} aria-label="What I am doing now"><img src="/assets/coffee-diary.webp" alt="" /></button>
        </nav>
      </div>
    </section>
  );
}

function Work({ onBack, onNext }) {
  const [selected, setSelected] = useState(0);
  const selectedProject = projects[selected] ?? null;
  return (
    <section className="screen page-screen work-screen" aria-labelledby="work-title">
      <PageHeader title="Selected Work" onBack={onBack} onNext={onNext} />
      <div className="command-window">
        <div className="command-topbar">
          <span>{profile.name}&apos;s Projects...</span>
          <a href={profile.github} target="_blank" rel="noreferrer">To GitHub <kbd>↗</kbd></a>
        </div>
        <p className="command-section-label">Projects</p>
        <div className="command-list" role="listbox" aria-label="Selected projects">
          {projects.map((project, index) => {
            const Icon = iconMap[project.title] || Briefcase;
            return (
              <button
                type="button"
                role="option"
                aria-selected={selected === index}
                className={selected === index ? "is-selected" : ""}
                key={project.title}
                onClick={() => setSelected(index)}
              >
                <span className="project-icon"><Icon weight="duotone" /></span>
                <strong>{project.title}</strong>
                <span>{project.description}</span>
                <em>{project.status}</em>
              </button>
            );
          })}
        </div>
        {selectedProject && (
          <div className="command-detail">
            <div className="command-detail-meta"><span>{selectedProject.tag}</span><strong>{selectedProject.title}</strong></div>
            <div className="command-detail-copy">
              <p>{selectedProject.description}</p>
              <a className="project-live-link" href={selectedProject.url} target="_blank" rel="noreferrer" aria-label={`Open ${selectedProject.title} live project`}>
                Open live project <ArrowSquareOut weight="bold" />
              </a>
            </div>
          </div>
        )}
        {selectedProject && <div className="command-footer"><img src="/assets/raycast-mark.svg" alt="" /><span>Select a project to explore</span></div>}
      </div>
    </section>
  );
}

function Now({ onBack, onNext }) {
  return (
    <section className="screen page-screen now-screen" aria-labelledby="now-title">
      <PageHeader title="What I’m Doing Now" onBack={onBack} onNext={onNext} />
      <div className="now-layout">
        <article className="now-overview">
          <span className="eyebrow">Long-term builder</span>
          <h3>Useful products, durable systems, real evidence.</h3>
          <p>My work tends to start where product intent, technical architecture, and day-to-day execution stop agreeing with each other.</p>
          <div className="principle-row">
            <span><Command weight="bold" /> Build</span>
            <span><GlobeHemisphereEast weight="bold" /> Verify</span>
            <span><NotePencil weight="bold" /> Document</span>
          </div>
        </article>
        <div className="now-cards">
          {nowItems.map((item, index) => (
            <article key={item.label}>
              <span>0{index + 1} · {item.label}</span>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
        <aside className="contact-card">
          <div><span className="eyebrow">Find me</span><h3>{profile.githubLabel}</h3></div>
          <a href={profile.github} target="_blank" rel="noreferrer">GitHub <ArrowSquareOut weight="bold" /></a>
          <span className="contact-pending"><EnvelopeSimple weight="bold" /> Email · 待补充</span>
        </aside>
      </div>
    </section>
  );
}

function End({ onRestart }) {
  return (
    <section className="screen end-screen" aria-labelledby="end-title">
      <div>
        <h2 id="end-title">© 2026 {profile.name} · {profile.englishName}</h2>
        <p>Build useful things. Keep the system honest.</p>
        <button type="button" onClick={onRestart} aria-label="Back to start">↶</button>
      </div>
    </section>
  );
}

export function App() {
  const [active, setActive] = useState(getScreenFromHash);
  const dragStart = useRef(null);

  const goTo = (next) => {
    const bounded = Math.max(0, Math.min(screens.length - 1, next));
    setActive(bounded);
    window.history.replaceState(null, "", `#${screens[bounded]}`);
  };

  useEffect(() => {
    const handleKey = (event) => {
      if (event.key === "ArrowRight") goTo(active + 1);
      if (event.key === "ArrowLeft") goTo(active - 1);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [active]);

  return (
    <main
      className="site-shell"
      onPointerDown={(event) => { dragStart.current = event.clientX; }}
      onPointerUp={(event) => {
        if (dragStart.current === null) return;
        const distance = event.clientX - dragStart.current;
        dragStart.current = null;
        if (Math.abs(distance) >= 70) goTo(distance < 0 ? active + 1 : active - 1);
      }}
    >
      <div className="screen-track" style={{ transform: `translate3d(-${active * 20}%, 0, 0)` }}>
        <Intro onEnter={() => goTo(1)} />
        <Portfolio onBack={() => goTo(0)} onNext={() => goTo(2)} />
        <Work onBack={() => goTo(1)} onNext={() => goTo(3)} />
        <Now onBack={() => goTo(2)} onNext={() => goTo(4)} />
        <End onRestart={() => goTo(0)} />
      </div>
    </main>
  );
}

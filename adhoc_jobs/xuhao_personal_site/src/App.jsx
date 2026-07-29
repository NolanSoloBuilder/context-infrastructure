import { useEffect, useRef, useState } from "react";
import { ArrowUp, CircleArrowRight, Undo2 } from "lucide-react";
import {
  ArrowCircleLeft,
  ArrowCircleRight,
  ArrowSquareOut,
  Cpu,
  GithubLogo,
  LinkedinLogo,
  MapPin,
  NotePencil,
  Sparkle,
  XLogo,
} from "@phosphor-icons/react";
import { focusAreas, notes, profile, projects } from "./content.js";

const screens = ["hello", "portfolio", "notes", "end"];

function getScreenFromHash() {
  const hash = window.location.hash.replace("#", "");
  const index = screens.indexOf(["work", "now"].includes(hash) ? "portfolio" : hash);
  return index < 0 ? 0 : index;
}

function SocialLink({ label, href, children, disabled = false, onClick }) {
  if (disabled) {
    return (
      <span className="social-button is-disabled" aria-label={`${label}，待补充`} title={`${label} · 待补充`}>
        {children}
      </span>
    );
  }

  if (onClick) {
    return (
      <button className="social-button" aria-label={label} type="button" onClick={onClick}>
        {children}
      </button>
    );
  }

  return (
    <a className="social-button" aria-label={label} href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  );
}

function Intro({ onEnter, onNotes }) {
  return (
    <section className="screen intro-screen" aria-labelledby="intro-name">
      <header className="intro-header">
        <h1 id="intro-name" className="name-chip">{profile.name}</h1>
        <nav className="social-links" aria-label="Social links">
          <SocialLink label="GitHub" href={profile.github}><GithubLogo weight="fill" /></SocialLink>
          <SocialLink label="LinkedIn" href={profile.linkedin}><LinkedinLogo weight="fill" /></SocialLink>
          <SocialLink label="X" href={profile.x}><XLogo weight="fill" /></SocialLink>
          <SocialLink label="小红书" href={profile.xiaohongshu}><img src="/assets/xiaohongshu.svg" alt="" /></SocialLink>
          <SocialLink label="Notes" onClick={onNotes}><NotePencil weight="fill" /></SocialLink>
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
      <div className="avatar-monogram" aria-label="Nalon monogram">N</div>
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

function ProjectGallery() {
  const [selected, setSelected] = useState(0);
  const project = projects[selected];

  return (
    <div className="project-gallery">
      <aside className="project-sidebar" aria-label="Selected projects">
        <p className="eyebrow">Selected projects</p>
        <div className="project-picker" role="listbox" aria-label="Choose a project">
          {projects.map((item, index) => (
            <button
              type="button"
              role="option"
              aria-selected={selected === index}
              className={selected === index ? "is-selected" : ""}
              key={item.title}
              onClick={() => setSelected(index)}
            >
              <img src={item.mark} alt="" />
              <span><strong>{item.title}</strong><small>{item.tag}</small></span>
            </button>
          ))}
        </div>
      </aside>

      <article className={`project-showcase gallery-layout-${project.images.length}`} aria-live="polite">
        <div className={`project-media${project.images.length > 1 ? ` has-gallery gallery-count-${project.images.length}` : ""}`}>
          <img className="project-hero" src={project.images[0]} alt={`${project.title} product preview`} />
          {project.images.slice(1).map((image, index) => (
            <img className="project-supporting-image" src={image} alt={`${project.title} feature preview ${index + 2}`} key={image} />
          ))}
        </div>
        <div className="project-showcase-copy">
          <div className="project-heading-row">
            <div><span>{project.tag}</span><h3>{project.title}</h3></div>
            <span className="live-status">{project.status}</span>
          </div>
          <p>{project.description}</p>
          <div className="project-highlights" aria-label={`${project.title} highlights`}>
            {project.highlights.map((highlight) => <span key={highlight}>{highlight}</span>)}
          </div>
          <a href={project.url} target="_blank" rel="noreferrer" aria-label={`Open ${project.title} live`}>
            Open live project <ArrowSquareOut weight="bold" />
          </a>
        </div>
      </article>
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

function GitHubPanel() {
  return (
    <div className="github-panel">
      <GithubLogo weight="fill" aria-hidden="true" />
      <p className="eyebrow">Open source profile</p>
      <h3>{profile.githubLabel}</h3>
      <p>Public repositories, experiments, and the code behind the products I choose to share.</p>
      <a href={profile.github} target="_blank" rel="noreferrer">
        Visit GitHub <ArrowSquareOut weight="bold" />
      </a>
    </div>
  );
}

function WindowBar({ title, onClose, onMinimize, onToggleMaximize, isMaximized }) {
  return (
    <div className="window-bar">
      <div className="traffic-lights">
        <button className="close-window" type="button" onClick={onClose} aria-label="Close window" />
        <button className="minimize-window" type="button" onClick={onMinimize} aria-label="Minimize window" />
        <button className="maximize-window" type="button" onClick={onToggleMaximize} aria-label={isMaximized ? "Restore window" : "Maximize window"} />
      </div>
      <span className="window-title">{title}</span>
      <span />
    </div>
  );
}

function Portfolio({ onBack, onNext }) {
  const [activeApp, setActiveApp] = useState("finder");
  const [isMaximized, setIsMaximized] = useState(false);
  const apps = {
    finder: { title: "finder", content: <ProfilePanel /> },
    projects: { title: "projects", content: <ProjectGallery /> },
    github: { title: "github", content: <GitHubPanel /> },
    toolbox: { title: "toolbox", content: <Toolbox /> },
  };
  const openApp = (app) => {
    setActiveApp(app);
    setIsMaximized(false);
  };

  return (
    <section className="screen page-screen portfolio-screen" aria-labelledby="portfolio-title">
      <PageHeader title="My Portfolio" onBack={onBack} onNext={onNext} />
      <div className="desktop-stage">
        {activeApp && (
          <div className={`browser-window desktop-window${isMaximized ? " is-maximized" : ""}`}>
            <WindowBar
              title={apps[activeApp].title}
              onClose={() => setActiveApp(null)}
              onMinimize={() => setActiveApp(null)}
              onToggleMaximize={() => setIsMaximized((value) => !value)}
              isMaximized={isMaximized}
            />
            <div className="window-content">{apps[activeApp].content}</div>
          </div>
        )}

        <nav className="dock" aria-label="Portfolio shortcuts">
          <button type="button" onClick={() => openApp("finder")} aria-label="Open Finder" aria-pressed={activeApp === "finder"}><img src="/assets/finder.png" alt="" /></button>
          <button type="button" onClick={() => openApp("projects")} aria-label="Open Projects" aria-pressed={activeApp === "projects"}><img src="/assets/photo.png" alt="" /></button>
          <button type="button" onClick={() => openApp("github")} aria-label="Open GitHub window" aria-pressed={activeApp === "github"}><img src="/assets/github.webp" alt="" /></button>
          <button type="button" onClick={() => openApp("toolbox")} aria-label="Open Toolbox" aria-pressed={activeApp === "toolbox"}><img src="/assets/raycast.png" alt="" /></button>
        </nav>
      </div>
    </section>
  );
}

function Notes({ onPortfolio, onNext }) {
  const [selectedSlug, setSelectedSlug] = useState(null);
  const selectedNote = notes.find((note) => note.slug === selectedSlug);

  return (
    <section className="screen notes-screen" aria-labelledby="notes-title">
      <div className="notes-page">
        <nav className="notes-nav" aria-label="Notes navigation">
          <button type="button" onClick={() => setSelectedSlug(null)}>Notes</button>
          <button type="button" onClick={onPortfolio}>Portfolio</button>
        </nav>

        {selectedNote ? (
          <article className="note-article">
            <button className="notes-back" type="button" onClick={() => setSelectedSlug(null)}>
              <ArrowCircleLeft weight="bold" /> All Notes
            </button>
            <p className="note-date">{selectedNote.date}</p>
            <h2 id="notes-title">{selectedNote.title}</h2>
            {selectedNote.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            <aside>This placeholder will be replaced when the first note is ready to publish.</aside>
          </article>
        ) : (
          <div className="notes-index">
            <header>
              <NotePencil weight="fill" aria-hidden="true" />
              <h2 id="notes-title">Nalon&apos;s Notes</h2>
            </header>
            <p className="notes-intro">Product decisions, engineering lessons, build logs, and the reasoning behind useful systems.</p>

            <div className="notes-list">
              {notes.map((note) => (
                <button type="button" key={note.slug} onClick={() => setSelectedSlug(note.slug)}>
                  <span>{note.date}</span>
                  <strong>{note.title}</strong>
                  <small>{note.excerpt}</small>
                </button>
              ))}
            </div>

            <footer className="notes-footer">
              <a href={profile.github} target="_blank" rel="noreferrer">GitHub <ArrowSquareOut weight="bold" /></a>
              <a href={profile.x} target="_blank" rel="noreferrer">X <ArrowSquareOut weight="bold" /></a>
              <a href={profile.linkedin} target="_blank" rel="noreferrer">LinkedIn <ArrowSquareOut weight="bold" /></a>
              <button type="button" onClick={onNext}>Continue</button>
            </footer>
          </div>
        )}
      </div>
    </section>
  );
}

function End({ onRestart }) {
  return (
    <section className="screen end-screen" aria-labelledby="end-title">
      <div>
        <h2 id="end-title">© 2026 {profile.name}</h2>
        <p>Build useful things. Keep the system honest.</p>
        <button type="button" onClick={onRestart} aria-label="Back to start">
          <Undo2 strokeWidth={2.25} aria-hidden="true" />
        </button>
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
      <div className="screen-track" style={{ "--screen-count": screens.length, transform: `translate3d(-${active * (100 / screens.length)}%, 0, 0)` }}>
        <Intro onEnter={() => goTo(1)} onNotes={() => goTo(2)} />
        <Portfolio onBack={() => goTo(0)} onNext={() => goTo(2)} />
        <Notes onPortfolio={() => goTo(1)} onNext={() => goTo(3)} />
        <End onRestart={() => goTo(0)} />
      </div>
    </main>
  );
}
